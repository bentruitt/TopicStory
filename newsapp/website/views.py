import pandas as pd
from flask import render_template, request, abort
from website import app
import datetime
import time

from variables import get_db, get_model
import models
from util import *

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/articles')
def articles():
    conn = get_db()
    articles = models.Articles(conn)
    num_articles = articles.count_articles()
    num_articles_by_source = articles.count_articles(by='source')
    num_articles_by_date = articles.count_articles(by='date')
    return render_template(
            'articles.html',
            num_articles=num_articles,
            num_articles_by_source=num_articles_by_source,
            num_articles_by_date=num_articles_by_date
    )

@app.route('/articles/source=<source_name>')
def articles_by_source(source_name):
    conn = get_db()

    sources = models.Sources(conn)
    source_exists = sources.lookup_exists(source_name)
    if not source_exists:
        return abort(404)
    
    articles = models.Articles(conn)
    num_articles = articles.count_articles(source_name=source_name)
    num_articles_by_date = articles.count_articles(by='date', source_name=source_name)
    return render_template(
            'articles_by_source.html',
            source=source_name,
            num_articles=num_articles,
            num_articles_by_date=num_articles_by_date
    )

@app.route('/articles/date=<publish_date>')
def articles_by_date(publish_date):
    publish_date = str(publish_date)
    try:
        publish_date = datetime.datetime.strptime(publish_date, '%Y-%m-%d').date()
    except ValueError:
        return abort(404)
    conn = get_db()

    articles = models.Articles(conn)
    num_articles = articles.count_articles(publish_date=publish_date)
    num_articles_by_source = articles.count_articles(by='source', publish_date=publish_date)
    return render_template(
            'articles_by_date.html',
            date=publish_date,
            num_articles=num_articles,
            num_articles_by_source=num_articles_by_source
    )

@app.route('/articles/source=<source_name>/date=<publish_date>')
def articles_by_source_and_date(source_name, publish_date):
    conn = get_db()

    sources = models.Sources(conn)
    source_exists = sources.lookup_exists(source_name)
    if not source_exists:
        return abort(404)

    publish_date = str(publish_date)
    try:
        publish_date = datetime.datetime.strptime(publish_date, '%Y-%m-%d').date()
    except ValueError:
        return abort(404)

    articles = models.Articles(conn)
    num_articles = articles.count_articles(source_name=source_name, publish_date=publish_date)
    article_infos = articles.retrieve_articles(source_name=source_name, publish_date=publish_date)
    return render_template(
            'articles_by_source_and_date.html',
            source=source_name,
            date=publish_date,
            num_articles=num_articles,
            articles=article_infos
    )

@app.route('/view-all-topics', methods=['GET'])
def view_all_topics():
    num_words = 20
    model = get_model()
    topic_counts = model.articles.groupby('topic')['title'].count().sort_values(ascending=False)
    topic_words = [model.get_topic_words(topic, num_words=num_words) for topic in topic_counts.index]
    topic_inds = topic_counts.index
    topics = zip(topic_inds, topic_counts, topic_words)

    articles_by_topic = plot_topic_popularity()
    return render_template('view_all_topics.html', articles_by_topic=articles_by_topic, topics=topics)

@app.route('/view-single-topic', methods=['GET'])
def view_single_topic():
    start = time.time()
    print 'start: {}'.format(time.time()-start)
    num_words = 20
    model = get_model()
    print 'get_model: {}'.format(time.time()-start)
    topic = get_topic()
    print 'get_topic: {}'.format(time.time()-start)
    topic_popularity = plot_topic_popularity_over_time(topic)
    print 'topic_popularity: {}'.format(time.time()-start)
    topic_words = model.get_topic_words(topic, num_words=num_words)
    print 'topic_words: {}'.format(time.time()-start)
    articles = model.articles
    articles = articles[articles['topic']==topic]
    articles = articles.sort_values(['date', 'source', 'title'])
    articles.index = range(len(articles))
    # each row is a dctionary with keys 'url', 'source', 'date', etc.
    articles_dates = [(d,articles[articles['date']==d].T.to_dict().values()) for d in articles['date'].unique()]
    print 'article_dates: {}'.format(time.time()-start)
    return render_template('view_single_topic.html', topic=topic, topic_words=topic_words, topic_popularity=topic_popularity, articles_dates=articles_dates)

@app.route('/view-daily-topics', methods=['GET'])
def topics():
    model = get_model()
    publish_date = get_publish_date()
    articles_by_topic_over_represented = plot_topic_popularity(date=publish_date, method='over-represented')
    topics = get_topic_popularity(publish_date, method='over-represented')
    topics = topics.sort_values(ascending=False).index
    articles = [get_articles(topic=topic, date=publish_date).T.to_dict().values() for topic in topics]
    topic_words = [model.get_topic_words(t, num_words=10) for t in topics]
    topics = zip(topics, articles, topic_words)
    return render_template(
            'view_daily_topics.html',
            topics = topics,
            publish_date=publish_date,
            articles_by_topic_over_represented=articles_by_topic_over_represented
    )
