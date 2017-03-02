import datetime
import os
import cPickle as pickle

import topics
import util
from conn import connect

def run_topics(start_date=datetime.date(2017,02,20), end_date=datetime.date(2017,02,26), num_topics=50, filename='model.pkl'):
    print 'creating topics...'
    print 'start date: {}'.format(start_date)
    print 'end date: {}'.format(end_date)
    print 'num topics: {}'.format(num_topics)
    print 'filename: {}'.format(filename)

    conn = connect()

    articles = util.load_articles(conn, start_date, end_date)
    documents = articles['text']
    topic_pipeline = topics.TopicPipeline(num_topics=num_topics)
    topic_pipeline.fit(documents)

    assigned_topics = topic_pipeline.topics.argmax(axis=1)
    articles['topic'] = assigned_topics
    topic_pipeline.articles = articles

    analysis_dir = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(analysis_dir, filename)

    with open(filepath, 'w') as f:
        pickle.dump(topic_pipeline, f)
    conn.close()
