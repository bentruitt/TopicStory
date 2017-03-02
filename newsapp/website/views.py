from flask import render_template, request, abort
from website import app
import datetime
import bokeh.charts as bkp
from bokeh.charts import Bar, show
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html, components, autoload_static
from bokeh.charts.attributes import CatAttr, cat

from database import get_db
import models
from analysis.util import load_articles

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
    if request.args.get('publish_date'):
        try:
            publish_date = datetime.datetime.strptime(request.args.get('publish_date'), '%Y-%m-%d').date()
        except ValueError:
            return abort(404)
    else:
        publish_date = datetime.date.today()
    conn = get_db()
    date = datetime.date(2017, 02, 27)
    data = load_articles(conn, date, date)
    source_counts = data.groupby('source')['text'].count().sort_values()
    data = {}
    data['source'] = source_counts.index.tolist()
    data['articles'] = source_counts.values
    # bar = bkp.Bar(data,
    #         label=CatAttr(columns=['source'], sort=False),
    #         values='articles',
    #         title='Articles by Source on {}'.format(publish_date),
    #         xlabel='',
    #         ylabel='number of articles', legend=False
    # )
    bar = horizontal_bar_plot(source_counts, xlabel='number of articles')
    script, div = components(bar)
    return render_template('topics.html', publish_date=publish_date, script=script, div=div)

@app.route('/d3', methods=['GET'])
def d3():
    data = [3, 4, 17, 12, 5]
    return render_template('d3.html', data=data, x="hello")

def horizontal_bar_plot(series, xlabel=''):
    p = figure(width=800, height=400, y_range=series.index.tolist())
    p.background_fill = "#EAEAF2"
    p.grid.grid_line_alpha=1.0
    p.grid.grid_line_color = "white"
    p.title='Articles by Source'
    p.xaxis.axis_label = xlabel
    p.xaxis.axis_label_text_font_style = 'normal'
    p.xaxis.axis_label_text_font_size = '14pt'
    p.xaxis.major_label_text_font_size = '14pt'
    p.yaxis.major_label_text_font_size = '14pt'
    p.yaxis.axis_label_text_font_size = '14pt'
    j = 1
    for k,v in series.iteritems():
        print k,v,j
        p.rect(x=v/2, y=j, width=abs(v), height=0.8,color=(76,114,176),
            width_units="data", height_units="data")
        j += 1
    return p
