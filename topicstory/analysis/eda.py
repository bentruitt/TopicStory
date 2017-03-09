import util
import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import topics
from ..conn import connect

plt.style.use('ggplot')

def plot_article_lengths():
    articles = load_eda_articles(filter_short=False)
    article_lengths = articles['text'].apply(len)
    plt.figure(figsize=(10,6))
    article_lengths.hist(bins=200)
    plt.xlim(0, 20000)
    plt.ylabel('counts')
    plt.xlabel('characters')
    plt.title('Lengths of articles')
    plt.tight_layout()
    plt.savefig('plots/article_lengths.png')
    plt.show()

def plot_sources_overall():
    articles = load_eda_articles(filter_short=True)
    counts = articles['source'].value_counts()
    ind = np.arange(0, len(counts)) - 0.5
    plt.figure(figsize=(10,6))
    plt.bar(ind, counts.values)
    plt.xticks(np.arange(len(counts)), counts.index)
    plt.xlabel('source')
    plt.ylabel('number of articles')
    plt.title('Articles by source between February 20th and February 27th')
    plt.tight_layout()
    plt.savefig('plots/source_counts_overall.png')
    plt.show()

def plot_sources_over_time():
    articles = load_eda_articles(filter_short=True)
    sources = pd.get_dummies(articles['source'])
    sources = sources[sources.mean().sort_values(ascending=False).index.tolist()]
    sources['date'] = articles['date']
    source_counts = sources.groupby('date').sum()
    # don't use pandas dataframe.plot, creates undeletable tick labels (extremely annoying!)
    plt.figure(figsize=(10,6))
    for col in source_counts.columns:
        plt.plot(source_counts[col], '-o', label=col, ms=3, lw=2)
    days = {0:'Mon',1:'Tues',2:'Weds',3:'Thurs',4:'Fri',5:'Sat',6:'Sun'}
    labels = pd.Series(source_counts.index).apply(lambda d: '{} {}/{}'.format(days[d.dayofweek], d.month, d.day)).values
    xmin, xmax = plt.xlim()
    xticks = np.linspace(xmin, xmax, len(source_counts))
    plt.xticks(xticks, labels)
    plt.xlabel('date')
    plt.ylabel('number of articles')
    plt.title('Articles by source over time')
    plt.legend(loc=0)
    plt.tight_layout()
    plt.savefig('plots/source_counts_by_date.png')
    plt.show()

def plot_log_likelihoods():
    articles = load_eda_articles(filter_short=True)
    train_articles = articles[articles['split']=='train']['text']
    test_articles = articles[articles['split']=='test']['text']
    ks = [2,3,4,6,8,10,20,30,40,60,80,100]
    train_scores, test_scores = log_likelihoods(train_articles, test_articles, ks=ks, method='batch')
    plt.plot(ks, -train_scores, '-o', color='r', label='train log-likelihood')
    plt.plot(ks, -test_scores, '--o', color='r', label='test log-likelihood')
    plt.title('Log Likelihoods for LDA')
    plt.xlabel('number of topics')
    plt.ylabel('negative log likelihood')
    plt.xscale('log')
    plt.yscale('log')
    plt.legend(loc=0)
    plt.tight_layout()
    plt.savefig('log_likelihoods.png')
    plt.show()
    return train_scores, test_scores

def run_many(method):
    articles = load_eda_articles(filter_short=True)
    train_docs = articles[articles['split']=='train']['text']
    ks = [2,3,4,6,8,10,20,30,40,60,80,100]
    topic_models = []
    for k in ks:
        print k
        topic_pipeline = topics.TopicPipeline(num_topics=k, method=method)
        topic_pipeline.fit(train_docs)
        topic_models.append(topic_pipeline)
    return topic_models

def clone_many(topic_pipelines):
    topic_pipelines2 = []
    for topic_pipeline in topic_pipelines:
        topic_pipeline2 = topics.TopicPipeline()
        topic_pipeline2.clone(topic_pipeline)
        topic_pipelines2.append(topic_pipeline2)
    return topic_pipelines2

def plot_empty_topics(ldas, nmfs, documents, filename):
    ks_ldas = [lda.num_topics for lda in ldas]
    ks_nmfs = [nmf.num_topics for nmf in nmfs]
    empty_ldas = [lda.compute_empty_topics(documents) for lda in ldas]
    empty_nmfs = [nmf.compute_empty_topics(documents) for nmf in nmfs]
    plt.plot(ks_ldas, empty_ldas, '--o', label='LDA')
    plt.plot(ks_nmfs, empty_nmfs, '--o', label='NMF')
    plt.xlabel('number of topics')
    plt.ylabel('number of empty topics')
    plt.title('Empty Topics')
    plt.legend(loc=0)
    plt.tight_layout()
    plt.savefig('plots/{}'.format(filename))
    plt.show()

def plot_reconstruction_error(nmfs):
    ks = [nmf.num_topics for nmf in nmfs]
    errs = [nmf.topic_model.reconstruction_err_ for nmf in nmfs]
    plt.plot(ks, errs)
    plt.xlabel('number of topics')
    plt.ylabel('reconstruction error')
    plt.title('Reconstruction Error for NMF')
    plt.tight_layout()
    plt.savefig('plots/reconstruction_error.png')
    plt.show()

def print_top_topics(topic_pipeline):
    for i in range(topic_pipeline.num_topics):
        print 'TOPIC {}'.format(i)
        print topic_pipeline.get_topic_words(i)

def log_likelihoods(train_docs, test_docs, ks=None, method='batch'):
    if ks is None:
        ks = [2,3,4,6,8,10,20,30,40,60,80,100]
    train_scores = []
    test_scores = []
    for k in ks:
        print k
        lda_pipeline = lda.LdaPipeline(num_topics=k, method=method)
        lda_pipeline.fit(train_docs)
        train_scores.append(lda_pipeline.score(train_docs))
        test_scores.append(lda_pipeline.score(test_docs))
    return np.array(train_scores), np.array(test_scores)

def plot_topics(articles, lda_pipeline):
    lda2 = lda.LdaPipeline(num_topics=100)
    lda2.clone(lda_pipeline)
    lda_pipeline = lda2
    lda_pipeline.plot_prevalent_topics(articles[articles['split']=='test'])
    plt.tight_layout()
    plt.show()
    return lda_pipeline

def eda(num_topics=100):
    articles = load_eda_articles(filter_short=True)
    lda_pipeline = lda.LdaPipeline(num_topics=num_topics)
    lda_pipeline.fit(articles[articles['split']=='train']['text'])
    # lda_pipeline.plot_prevalent_topics(articles[articles['split']=='test']['text'])
    return articles, lda_pipeline

def load_eda_articles(filter_short=False):
    conn = connect()
    start_date = datetime.date(2017, 02, 20)
    end_date = datetime.date(2017, 02, 27)
    articles = util.load_articles(conn, start_date, end_date)
    articles['split'] = articles['date'].apply(lambda d: 'test' if d==end_date else 'train')
    conn.close()
    if filter_short:
        articles = articles[articles['text'].apply(len)>1000]
    articles['date'] = pd.to_datetime(articles['date'])
    return articles

if __name__ == '__main__':
    articles = load_eda_articles(filter_short=True)
    train_articles = articles[articles['split']=='train']['text']
    test_articles = articles[articles['split']=='test']['text']
    ldas = run_many(method='lda')
    nmfs = run_many(method='nmf')
