import datetime
import models
from conn import connect
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from nltk.stem.snowball import EnglishStemmer
import scipy.cluster.hierarchy as hcluster
import numpy as np

import util

def cluster_date(date, thresh=0.7):
    if type(date) != datetime.date:
        raise ValueError('Argument `date` must be of type `datetime.date`')
    conn = connect()
    articles_model = models.Articles(conn)
    articles = articles_model.get_articles_by_date(date)
    docs = [article['text'] for article in articles]
    docs = util.clean_docs(docs)
    vectorizer = TfidfVectorizer(docs)
    tfidf = vectorizer.fit_transform(docs).todense()

    clusters = hcluster.fclusterdata(tfidf, thresh, metric='cosine', criterion='distance')
    cluster_ids, cluster_counts = np.unique(clusters, return_counts=True)
    sorted_cluster_ids = np.argsort(-cluster_counts)
    for cluster in cluster_ids[sorted_cluster_ids]:
        print ''
        idx = (clusters==cluster).nonzero()[0]
        for i in idx:
            print '({}) {}'.format(articles[i]['name'], articles[i]['title'])
