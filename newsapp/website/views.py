import pandas as pd
from flask import render_template, request, abort
from website import app
import datetime

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

@app.route('/topics', methods=['GET'])
def topics():
    publish_date = get_publish_date()
    articles_by_source = plot_articles_by_source(publish_date)
    articles_by_topic = plot_articles_by_topic(publish_date)
    return render_template('topics.html', publish_date=publish_date, articles_by_source=articles_by_source, articles_by_topic=articles_by_topic)

@app.route('/view-all-topics', methods=['GET'])
def view_all_topics():
    conn = get_db()
    model = get_model()
    start_date = datetime.date(2017, 02, 20)
    end_date = datetime.date(2017, 02, 26)
    df = load_articles(conn, start_date, end_date)
    articles = df['text']
    topic_names, topic_counts = model.get_prevalent_topics(articles, num_topics=model.num_topics, num_words=20)
    topics = list(enumerate(zip(topic_names, topic_counts)))

    total_articles_by_topic = plot_total_articles_by_topic()
    return render_template('view_all_topics.html', total_articles_by_topic=total_articles_by_topic, topics=topics)

@app.route('/view-single-topic', methods=['GET'])
def view_single_topic():
    topic = get_topic()
    topic_popularity = plot_topic_popularity_over_time(topic)
    return render_template('view_single_topic.html', topic=topic, topic_popularity=topic_popularity)
