import datetime
import cPickle as pickle
import os

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

    df = util.load_articles(conn, start_date, end_date)
    articles = df['text']
    topic_pipeline = topics.TopicPipeline(num_topics=num_topics, method='nmf')
    topic_pipeline.fit(articles)

    analysis_dir = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(analysis_dir, filename)
    with open(filepath, 'w') as f:
        pickle.dump(topic_pipeline, f)

    conn.close()
