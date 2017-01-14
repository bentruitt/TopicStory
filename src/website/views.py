from flask import render_template, request, abort
from website import app

#import models.articles
#import models.cosine_similarities
from database import get_db

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/articles')
def articles():
    return render_template('articles.html')

@app.route('/topics')
def topics():
    return render_template('topics.html')

@app.route('/clustering')
def clustering():
    return render_template('clustering.html')

# @app.route('/article')
# def article():
#     articles = models.articles.Articles(get_db())
#     article = articles.get_random_article()
#     return render_template('article.html', article=article)

# @app.route('/list-all')
# def list_all():
#     articles = models.articles.Articles(get_db())
#     articles = articles.get_all_articles()
#     return render_template('list.html', articles=articles)
# 
# @app.route('/cosine/<int:article_id>')
# def cosine(article_id=None):
#     articles = models.articles.Articles(get_db())
#     cosine_similarities = models.cosine_similarities.CosineSimilarities(get_db())
#     try:
#         main_article = articles.lookup_article(article_id)
#     except ValueError:
#         abort(404)
#     compared_articles = cosine_similarities.get_article_similarities(article_id)
#     return render_template('cosine.html', main_article=main_article, articles=compared_articles)
