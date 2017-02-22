from flask import render_template, request, abort
from website import app
import datetime

from database import get_db
import models
import analysis.nlp as nlp
import analysis.entailment.predict_news_entailment as predict
import analysis.topic_modeling.topic_modeling as topic_modeling

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

@app.route('/clustering', methods=['GET'])
def clustering():
    if request.args.get('publish_date'):
        try:
            publish_date = datetime.datetime.strptime(request.args.get('publish_date'), '%Y-%m-%d').date()
        except ValueError:
            return abort(404)
    else:
        publish_date = datetime.datetime.strptime('2017-01-20', '%Y-%m-%d').date()
    if request.args.get('threshold'):
        try:
            threshold = float(request.args.get('threshold'))
        except ValueError:
            return abort(404)
    else:
        threshold = 0.18

    from_table = 'spacy_text_vectors'
    from_field = 'spacy_text_vector'

    conn = get_db()
    article_clusters = nlp.compute_clusters_by_date(conn, publish_date=publish_date, threshold=threshold, from_table=from_table, from_field=from_field)
    return render_template('clustering.html', publish_date=publish_date, threshold=threshold, article_clusters=article_clusters)

@app.route('/topics', methods=['GET'])
def topics():
    if request.args.get('publish_date'):
        try:
            publish_date = datetime.datetime.strptime(request.args.get('publish_date'), '%Y-%m-%d').date()
        except ValueError:
            return abort(404)
    else:
        publish_date = datetime.datetime.strptime('2017-01-20', '%Y-%m-%d').date()
    conn = get_db()
    topics = topic_modeling.find_topics(conn, publish_date)
    return render_template('topics.html', publish_date=publish_date, topics=topics)

@app.route('/disagreements', methods=['GET'])
def disagreements():
    if request.args.get('publish_date'):
        try:
            publish_date = datetime.datetime.strptime(request.args.get('publish_date'), '%Y-%m-%d').date()
        except ValueError:
            return abort(404)
    else:
        publish_date = datetime.datetime.strptime('2017-01-20', '%Y-%m-%d').date()

    conn = get_db()
    disagreements = predict.find_disagreements(conn, publish_date)
    return render_template('disagreements.html', disagreements=disagreements, publish_date=publish_date)
