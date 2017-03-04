import datetime
import pandas as pd
from bokeh.models import Range1d
from bokeh.charts import TimeSeries
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html, components, autoload_static
from bokeh.charts.attributes import CatAttr, cat

from analysis.util import load_articles
from variables import get_db, get_model
from flask import request

def get_publish_date():
    model = get_model()
    last_date = model.articles['date'].unique().max()
    if request.args.get('publish_date'):
        try:
            publish_date = datetime.datetime.strptime(request.args.get('publish_date'), '%Y-%m-%d').date()
        except ValueError:
            publish_date = last_date
    else:
        publish_date = last_date
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

def plot_topic_popularity_over_time(topic):
    '''
    Plots the topic popularity as a function of time.
    Values on the y-axis represent daily article counts for that topic.
    Inputs:
        topic - integer
    Outputs:
        plot dictionary with script and div elements
    '''
    model = get_model()
    articles = model.articles
    article_counts = articles[articles['topic']==topic].groupby('date')['title'].count().sort_index()
    dates = articles['date'].unique()
    missing_dates = set(dates) - set(article_counts.index)
    for date in missing_dates:
        article_counts[date] = 0
    article_counts = article_counts.sort_index()
    dates = article_counts.index
    data = { 'date': map(str,dates), 'count': article_counts }
    p = TimeSeries(
            data,
            x='date',
            y='count',
            title='Topic Popularity Over Time'
    )
    p.y_range.start = 0
    script, div = components(p)
    plot = {}
    plot['script'] = script
    plot['div'] = div
    return plot

def plot_topic_popularity(date=None, method='total'):
    '''
    Plots the popularity of each topic as a horizontal bar plot using Bokeh.
    Inputs:
        date - datetime.date. If None, use all the dates.
        method - string. Takes two possible values.
            If 'total', use the (total number of articles)
            If 'over-represented', use (subset of articles) / (daily average number of articles)
    Outputs:
        plot - a dictionary containing two items.
            The keys are 'div' and 'script', the values are html blocks to insert into the webpage.
    '''

    num_topics_plot = 10
    num_words_plot = 5
    model = get_model()

    topic_popularity = get_topic_popularity(date, method)
    topic_popularity = topic_popularity.sort_values()
    topic_popularity = topic_popularity[::-1][:num_topics_plot][::-1]
    topic_names = [' '.join(model.get_topic_words(topic, num_words=num_words_plot)) for topic in topic_popularity.index]
    topic_popularity.index = topic_names
    p = horizontal_bar_plot(topic_popularity)

    script, div = components(p)
    plot = {}
    plot['script'] = script
    plot['div'] = div
    return plot

def get_topic_popularity(date=None, method='total'):
    '''
    Returns the topic popularities with a given method.
    Inputs:
        date - datetime.date. If None, use all the dates.
        method - string. Takes two possible values.
            If 'total', use the (total number of articles)
            If 'over-represented', use (subset of articles) / (daily average number of articles)
    Outputs:
        topic_popularity - Pandas Series, index are the top topics, values are the popularity measures.
    '''
    model = get_model()
    articles = model.articles

    if date is not None:
        articles = articles[articles['date']==date]
    article_counts = articles.groupby('topic')['title'].count().sort_index()

    if method=='total':
        topic_popularity = article_counts
    elif method=='over-represented':
        num_dates = model.articles['date'].nunique()
        article_counts_total = model.articles.groupby('topic')['title'].count().sort_index()
        article_counts_avg = article_counts_total / num_dates
        topic_popularity = article_counts / article_counts_avg
        topic_popularity = topic_popularity.fillna(0)

    return topic_popularity

def get_articles(topic=None, date=None):
    '''
    Retrieves articles.
    Inputs:
        topic - integer, if None then uses all topics
        date - datetime.date, if None the uses all dates
    Outputs:
        articles
        
    '''
    model = get_model()
    articles = model.articles
    if topic is not None:
        articles = articles[articles['topic']==topic]
    if date is not None:
        articles = articles[articles['date']==date]
    articles = articles.sort_values(['date', 'source', 'title'])
    articles.index = range(len(articles))
    return articles

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
