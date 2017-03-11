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
    # total takes about 0.336 secs (much better! could still be improved)
    conn = get_db()
    articles, topic_words = load_nmf_data(conn)

    topic_counts = get_all_topics_count(articles)

    list_topic_counts = topic_counts
    list_topic_inds = list_topic_counts.index.tolist()
    list_topic_names = get_topic_names(list_topic_inds, topic_words, num_words=20)
    list_topics = zip(list_topic_inds, list_topic_counts, list_topic_names)

    plot_topic_counts = topic_counts[:10]
    plot_topic_names = get_topic_names(plot_topic_counts.index, topic_words, num_words=5)
    plot_topic_counts.index = plot_topic_names
    plot_topics = horizontal_bar_plot(plot_topic_counts)

    return render_template('view_all_topics.html', list_topics=list_topics, plot_topics=plot_topics)

@app.route('/view-single-topic', methods=['GET'])
def view_single_topic():
    conn = get_db()
    topic = get_topic()
    articles, topic_words = load_nmf_data(conn)

    topic_counts = get_single_topic_count(articles, topic)

    topic_name = get_topic_name(topic, topic_words, num_words=20)
    
    dates = topic_counts.index.tolist()
    topic_articles = articles[articles['topic']==topic]
    topic_articles = topic_articles.sort_values(['date', 'source', 'title'])
    topic_articles.index = range(len(topic_articles))
    topic_articles_by_date = [topic_articles[topic_articles['date']==d] for d in dates]
    topic_articles_by_date = map(lambda df: df.T.to_dict().values(), topic_articles_by_date)
    dates_articles = zip(dates, topic_articles_by_date)

    plot_time = time_series_plot(topic_counts.index.tolist(), topic_counts.values, xlabel='Date', ylabel='Number of Articles', title='Topic Popularity over Time')

    return render_template('view_single_topic.html', topic=topic, topic_name=topic_name, dates_articles=dates_articles, plot_time=plot_time)

@app.route('/view-daily-topics', methods=['GET'])
def view_daily_topics():
    conn = get_db()
    articles, topic_words = load_nmf_data(conn)
    date = get_date(articles)

    topic_popularities = get_daily_topics_popularity(articles, date)

    topics = topic_popularities.index.tolist()
    topic_names = [get_topic_name(t, topic_words, num_words=10) for t in topics]
    date_articles = articles[articles['date']==date]
    date_articles = date_articles.sort_values(['topic', 'source', 'title'])
    date_articles.index = range(len(date_articles))
    date_articles_by_topic = [date_articles[date_articles['topic']==t] for t in topics]
    date_articles_by_topic = map(lambda df: df.T.to_dict().values(), date_articles_by_topic)
    topics_articles = zip(topics, topic_names, date_articles_by_topic)

    plot_topic_popularities = topic_popularities[:10]
    plot_topic_names = get_topic_names(plot_topic_popularities.index, topic_words, num_words=5)
    plot_topic_popularities.index = plot_topic_names
    plot_topics = horizontal_bar_plot(plot_topic_popularities, xlabel='Articles Today / Articles on Average', title='Topic Popularity')

    return render_template('view_daily_topics.html', date=date, topics_articles=topics_articles, plot_topics=plot_topics)

@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')
