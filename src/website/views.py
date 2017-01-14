from flask import render_template, request, abort
from website import app

from database import get_db
import models

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

# @app.route('/articles/source=<source_name>/date=<publish_date>')
# def articles_by_source_and_date(source_name, publish_date):
#     conn = get_db()
# 
#     sources = models.Sources(conn)
#     source_exists = sources.lookup_exists(source_name)
#     if not source_exists:
#         return abort(404)
# 
#     articles = models.Articles(conn)
#     num_articles = articles.count_articles(source_name=source_name)
#     num_articles_by_date = articles.count_articles(by='date', source_name=source_name)
#     return render_template(
#             'articles_by_source.html',
#             source=source_name,
#             num_articles=num_articles,
#             num_articles_by_date=num_articles_by_date
#     )

@app.route('/topics')
def topics():
    return render_template('topics.html')

@app.route('/clustering')
def clustering():
    return render_template('clustering.html')
