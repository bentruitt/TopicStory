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
    articles_by_source = articles.count_articles_by_source()
    articles_by_date = articles.count_articles_by_date()
    return render_template(
            'articles.html',
            num_articles=num_articles,
            articles_by_source=articles_by_source,
            articles_by_date=articles_by_date
    )

@app.route('/topics')
def topics():
    return render_template('topics.html')

@app.route('/clustering')
def clustering():
    return render_template('clustering.html')
