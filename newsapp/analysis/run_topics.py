import datetime
import os
import cPickle as pickle

import topics
import util
from conn import connect

def run_topics(start_date=datetime.date(2017,02,20), end_date=datetime.date(2017,02,26), num_topics=50):
    print 'creating topics...'
    print 'start date: {}'.format(start_date)
    print 'end date: {}'.format(end_date)
    print 'num topics: {}'.format(num_topics)

    conn = connect()

    articles = util.load_articles(conn, start_date, end_date)
    documents = articles['text']
    topic_pipeline = topics.TopicPipeline(num_topics=num_topics)
    topic_pipeline.fit(documents)

    assigned_topics = topic_pipeline.topics.argmax(axis=1)
    articles['topic'] = assigned_topics
    articles = articles.drop(['text'], axis=1)
    topic_pipeline.articles = articles

    store_nmf_results(conn, num_topics, start_date, end_date, articles, topic_pipeline)

    conn.close()

def store_nmf_results(conn, num_topics, start_date, end_date, articles, topic_pipeline):
    nmf_model_id = store_nmf_model(conn, num_topics, start_date, end_date)

    for url,topic in zip(articles['url'], articles['topic']):
        store_nmf_article_topics(conn, nmf_model_id, url, topic)

    for topic in range(num_topics):
        words = topic_pipeline.get_topic_words(topic, num_words=100)
        store_nmf_topic_words(conn, nmf_model_id, topic, words)
    print 'finished storing'

def store_nmf_model(conn, num_topics, start_date, end_date):
    cursor = conn.cursor()
    q = '''
        INSERT INTO nmf_models (num_topics,start_date,end_date)
        VALUES (%s,%s,%s)
        RETURNING id;
        '''
    cursor.execute(q, (num_topics,start_date,end_date))
    nmf_model_id = cursor.fetchone()[0]
    conn.commit()
    return nmf_model_id

def store_nmf_article_topics(conn, nmf_model, url, topic):
    cursor = conn.cursor()
    q = '''
        INSERT INTO nmf_article_topics (nmf_model,article,topic)
        VALUES (
            %s,
            (SELECT id FROM urls WHERE url=%s),
            %s
        );
        '''
    cursor.execute(q, (nmf_model, url, topic))
    conn.commit()

def store_nmf_topic_words(conn, nmf_model, topic, words):
    cursor = conn.cursor()
    q = '''
        INSERT INTO nmf_topic_words (nmf_model,topic,words)
        VALUES (%s,%s,%s)
        '''
    cursor.execute(q, (nmf_model, topic, words))
    conn.commit()
