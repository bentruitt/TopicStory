import string
from gensim import corpora, models, similarities
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
import sys  

import models.articles as ma
import models.cosine_similarities as mcs
from config import connect

reload(sys)  
sys.setdefaultencoding('utf8')

def calculate_cosine_similarities():
  conn = connect()
  articles_model = ma.Articles(conn)
  cosine_similarities = mcs.CosineSimilarities(conn)

  articles = articles_model.get_all_articles()
  ids = [article.url for article in articles]
  docs = [article.text for article in articles]
  sims = calculate_similarities(docs)
  cosine_similarities.insert_similarities(articles, sims)

  conn.close()

def calculate_similarities(docs):
  docs = [doc.encode('utf-8', 'ignore') for doc in docs]
  docs = [doc.split() for doc in docs]
  docs = [[word.lower() for word in doc] for doc in docs]
  docs = [[filter(lambda c: c in string.letters, word) for word in doc] for doc in docs]
  docs = [filter(lambda w: w != '',doc) for doc in docs]
  docs = [filter(lambda w: w not in ENGLISH_STOP_WORDS,doc) for doc in docs]
  dictionary = corpora.Dictionary(docs)
  corpus = [dictionary.doc2bow(doc) for doc in docs]
  tfidf = models.TfidfModel(corpus)
  tfidf_corpus = tfidf[corpus]
  index = similarities.MatrixSimilarity(tfidf_corpus)
  sims = index[tfidf_corpus]
  return sims
