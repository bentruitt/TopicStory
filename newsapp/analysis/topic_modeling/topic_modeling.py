from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer
import analysis.nlp as nlp
import string
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
import numpy as np
# from nltk.stem.snowball import EnglishStemmer

def find_topics(conn, publish_date):
    num_topics = 10
    from_table = 'articles'
    from_field = 'text'
    url_ids, articles = nlp.lookup_vectors_by_date(conn, from_table, from_field, publish_date)
    url_ids = np.array(url_ids)
    articles = [clean_document(article) for article in articles]
    tfidf_model = TfidfVectorizer()
    tfidf_model.fit(articles)
    tfidf = tfidf_model.transform(articles)
    lda_model = LatentDirichletAllocation(n_topics=num_topics)
    lda_model.fit(tfidf)
    vocab = tfidf_model.get_feature_names()
    top_words = [[vocab[i] for i in component.argsort()[:-10:-1]] for component in lda_model.components_]
    article_topics = np.array([lda_model.transform(article_vec).argmax() for article_vec in tfidf])
    topic_groups = []
    for i in range(num_topics):
        topic_groups.append(url_ids[article_topics==i])
    topic_groups = [[nlp.lookup_article_info(conn, article) for article in group] for group in topic_groups]
    topics = [{'words': words, 'articles': articles} for words,articles in zip(top_words, topic_groups)]
    return topics

def clean_document(document):
    document = document.encode('utf-8', 'ignore')
    document = document.split()
    document = [word.lower() for word in document]
    document = [filter(lambda c: c in string.letters, word) for word in document]
    document = filter(lambda w: w not in ENGLISH_STOP_WORDS,document)
    # es = EnglishStemmer()
    # document = [es.stem(word) for word in document]
    document = filter(lambda w: w != '',document)
    document = string.join(document, ' ')
    return document

