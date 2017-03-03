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
    topic_pipeline.articles = articles

    filename = 'model_{}_{}_{}.pkl'.format(start_date, end_date, num_topics)
    analysis_dir = os.path.dirname(os.path.realpath(__file__))
    models_dir = os.path.join(analysis_dir, 'models')
    filepath = os.path.join(models_dir, filename)

    with open(filepath, 'w') as f:
        pickle.dump(topic_pipeline, f)
    conn.close()
