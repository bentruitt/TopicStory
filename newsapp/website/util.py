import datetime
import pandas as pd
from bokeh.charts import TimeSeries
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html, components, autoload_static
from bokeh.charts.attributes import CatAttr, cat

from analysis.util import load_articles
from variables import get_db, get_model
from flask import request

def get_publish_date():
    if request.args.get('publish_date'):
        try:
            publish_date = datetime.datetime.strptime(request.args.get('publish_date'), '%Y-%m-%d').date()
        except ValueError:
            publish_date = datetime.date.today()
    else:
        publish_date = datetime.date.today()
    return publish_date

def get_topic():
    if request.args.get('topic'):
        try:
            topic = request.args.get('topic')
            topic = int(topic)
        except ValueError:
            topic = 0
    else:
        topic = 0
    model = get_model()
    if topic < 0 or topic > model.num_topics:
        topic = 0
    return topic

def plot_total_topic_popularity():
    num_topics_plot = 10
    num_words_plot = 5
    model = get_model()
    article_counts = model.articles.groupby('topic')['text'].count().sort_values()[::-1][:num_topics_plot][::-1]
    article_names = [' '.join(model.get_topic_words(topic, num_words=num_words_plot)) for topic in article_counts.index]
    article_counts.index = article_names
    p = horizontal_bar_plot(article_counts)

    script, div = components(p)
    plot = {}
    plot['script'] = script
    plot['div'] = div
    return plot

def plot_topic_popularity_over_time(topic):
    model = get_model()
    articles = model.articles
    article_counts = articles[articles['topic']==topic].groupby('date')['text'].count().sort_index()
    dates = article_counts.index
    data = { 'date': map(str,dates), 'count': article_counts }
    p = TimeSeries(
            data,
            x='date',
            y='count',
            title='Topic Popularity Over Time'
    )
    script, div = components(p)
    plot = {}
    plot['script'] = script
    plot['div'] = div
    return plot

def plot_topic_popularity_single_date(date):
    articles = get_model()
    articles[articles['date']==date].groupby('topic').count()
    pass

def horizontal_bar_plot(series, xlabel=''):
    p = figure(width=800, height=400, y_range=series.index.tolist())
    p.background_fill = "#EAEAF2"
    p.grid.grid_line_alpha=1.0
    p.grid.grid_line_color = "white"
    p.title.text = 'Articles by Source'
    p.xaxis.axis_label = xlabel
    p.xaxis.axis_label_text_font_style = 'normal'
    p.xaxis.axis_label_text_font_size = '14pt'
    p.xaxis.major_label_text_font_size = '14pt'
    p.yaxis.major_label_text_font_size = '14pt'
    p.yaxis.axis_label_text_font_size = '14pt'
    j = 1
    for k,v in series.iteritems():
        p.rect(x=float(v)/2, y=j, width=abs(v), height=0.8,color=(76,114,176),
            width_units="data", height_units="data")
        j += 1
    return p
