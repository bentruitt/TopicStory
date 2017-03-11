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

# keep
def get_date(articles):
    last_date = articles['date'].unique().max()
    if request.args.get('date'):
        try:
            date = datetime.datetime.strptime(request.args.get('date'), '%Y-%m-%d').date()
        except ValueError:
            date = last_date
    else:
        date = last_date
    return date

# keep
def get_topic():
    if request.args.get('topic'):
        try:
            topic = request.args.get('topic')
            topic = int(topic)
        except ValueError:
            topic = 0
    else:
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

# new - keep
def get_all_topics_count(articles):
    '''
    Counts the number of articles for each topic.
    Input:
        articles - Dataframe
            rows are articles
            column 'topic' is that article's topic
            column 'title' is that article's title
    Output:
        topic_counts - Series 
            index - integers (representing topics)
            values - integers (representing counts)
            sorted by counts from highest to lowest
    '''
    topic_counts = articles.groupby('topic')['title'].count().sort_values(ascending=False)
    return topic_counts

# new - keep
def get_single_topic_count(articles, topic):
    '''
    Counts the number of articles on each day for a given topic.
    Input:
        articles - Dataframe
            rows are articles
            column 'topic' is that article's topic
            column 'title' is that article's title
        topic - topic to count
    Output:
        topic_counts - Series
            index - datetime.date (representing dates)
            values - integers (representing counts)
            sorted by date from lowest to highest
    '''
    topic_counts = articles[articles['topic']==topic].groupby('date')['title'].count()
    dates = articles['date'].unique()
    missing_dates = set(dates) - set(topic_counts.index)
    for date in missing_dates:
        topic_counts[date] = 0
    topic_counts = topic_counts.sort_index()
    return topic_counts

# keep
def get_daily_topics_popularity(articles, date):
    '''
    Measures the popularity of each topic for a single date.
    Calculated using (num articles for topic today) / (num articles for topic on average day)
    Input:
        articles - Dataframe
            rows are articles
            column 'topic' is that article's topic
            column 'title' is that article's title
        topic - topic to count
    Output:
        topic_popularities - Series
            index - integers (representing topics)
            values - floats (representing popularities)
            Sorted by values from highest to lowest
    '''
    num_dates = articles['date'].nunique()
    topic_counts_total = articles.groupby('topic')['title'].count()
    topic_counts_avg = topic_counts_total / num_dates

    articles_today = articles[articles['date']==date]
    topic_counts_today = articles_today.groupby('topic')['title'].count()

    topic_popularities = topic_counts_today / topic_counts_avg
    topic_popularities = topic_popularities.fillna(0)
    topic_popularities = topic_popularities.sort_values(ascending=False)

    return topic_popularities

# new - keep
def get_topic_names(topics, topic_words, num_words=5):
    '''
    Gets topic names by concatenating the top words for each topic.
    Input:
        topics - Iterable list of integers representing topics
        topic_words - Dataframe with two columns
            'topic' - integer representing topic
            'words' - list of top words for that topic
        num_words - integer, number of words to concatenate
    Output:
        topic_names - List of strings representing the new name for each topic.
    '''
    topic_names = [get_topic_name(t, topic_words, num_words=num_words) for t in topics]
    return topic_names

def get_topic_name(topic, topic_words, num_words=5):
    '''
    Gets topic name by concatenating the top words for a given topic.
    Input:
        topic - Integer representing a topic
        topic_words - Dataframe with two columns
            'topic' - integer representing topic
            'words' - list of top words for that topic
        num_words - integer, number of words to concatenate
    Output:
        topic_names - List of strings representing the new name for each topic.
    '''
    topic_name = topic_words.copy()
    topic_name['words'] = topic_name['words'].apply(lambda words: ' '.join(words[:num_words]))
    topic_name = topic_name[topic_name['topic']==topic]['words'].values[0]
    return topic_name

def plot_total_topic_counts(articles, topic_words):
    '''
    Plots the popularity of each topic as a horizontal bar plot using Bokeh.
    Inputs:
        articles - dataframe
        topic_words - dataframe
    Outputs:
        plot - a dictionary containing two items.
            The keys are 'div' and 'script', the values are html blocks to insert into the webpage.
    '''

    num_topics_plot = 10
    num_words_plot = 5

    # after these lines of code, topic_counts is series, length 10, index is top 10 topics (ints), values are article counts for each topic
    topic_counts = articles.groupby('topic')['title'].count()
    topic_counts = topic_counts.sort_values(ascending=False)[:num_topics_plot]

    # after these lines of code, topic_names is list, length 10, each value is string of top 5 words concatenated
    topic_names = topic_words.copy()
    topic_names['words'] = topic_names['words'].apply(lambda words: ' '.join(words[:num_words_plot]))
    topic_names = [topic_names[topic_names['topic']==t]['words'].values[0] for t in topic_counts.index]

    # set the index to add labels for the plot
    topic_counts.index = topic_names
    p = horizontal_bar_plot(topic_counts)

    script, div = components(p)
    plot = {}
    plot['script'] = script
    plot['div'] = div
    return plot

def get_topic_popularity(articles, date=None, method='total'):
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

    if date is not None:
        articles = articles[articles['date']==date]
    topic_counts = articles.groupby('topic')['title'].count().sort_index()

    if method=='total':
        topic_popularity = topic_counts
    elif method=='over-represented':
        num_dates = articles['date'].nunique()
        topic_counts_total = articles.groupby('topic')['title'].count().sort_index()
        topic_counts_avg = topic_counts_total / num_dates
        topic_popularity = topic_counts / topic_counts_avg
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

def time_series_plot(dates, values, xlabel='', ylabel='', title=''):
    data = { 'dates': map(str,dates), 'values': values }
    p = TimeSeries(
            data,
            x='dates',
            y='values',
            xlabel=xlabel,
            ylabel=ylabel,
            title=title
    )
    p.y_range.start = 0
    script, div = components(p)
    plot = {}
    plot['script'] = script
    plot['div'] = div
    return plot

def horizontal_bar_plot(series, xlabel='', ylabel='', title=''):
    # plot from top to bottom
    series = series[::-1]

    p = figure(
            width=800,
            height=400,
            y_range=series.index.tolist(),
            title=title
    )
    p.background_fill = "#EAEAF2"
    p.grid.grid_line_alpha=1.0
    p.grid.grid_line_color = "white"
    p.xaxis.axis_label = xlabel
    p.xaxis.axis_label_text_font_style = 'bold'
    p.xaxis.major_label_text_font_size = '14pt'
    p.xaxis.axis_label_text_font_size = '10pt'
    p.yaxis.axis_label = ylabel
    p.yaxis.major_label_text_font_size = '14pt'
    p.yaxis.axis_label_text_font_size = '14pt'
    j = 1
    for k,v in series.iteritems():
        p.rect(x=float(v)/2, y=j, width=abs(v), height=0.8,color=(76,114,176),
            width_units="data", height_units="data")
        j += 1
    script, div = components(p)
    plot = {}
    plot['script'] = script
    plot['div'] = div
    return plot

def load_nmf_data(conn):
    nmf_model = load_last_nmf_model(conn)
    articles = load_nmf_articles(conn, nmf_model)
    topic_words = load_nmf_topic_words(conn, nmf_model)
    return articles, topic_words

def load_last_nmf_model(conn):
    cursor = conn.cursor()
    q = '''
        SELECT MAX(id)
        FROM nmf_models
        '''
    cursor.execute(q)
    nmf_model = cursor.fetchone()[0]
    return nmf_model

def load_nmf_articles(conn, nmf_model):
    cursor = conn.cursor()
    q = '''
        SELECT urls.url, title, date, sources.name, topic
        FROM nmf_article_topics
            JOIN articles
                ON nmf_article_topics.nmf_model=%s
                AND nmf_article_topics.article=articles.url
            JOIN urls
                ON articles.url=urls.id
            JOIN sources
                ON articles.source=sources.id;
        '''
    cursor.execute(q, (nmf_model,))
    results = cursor.fetchall()
    articles = pd.DataFrame(results, columns=['url', 'title', 'date', 'source', 'topic'])
    return articles

def load_nmf_topic_words(conn, nmf_model):
    cursor = conn.cursor()
    q = '''
        SELECT topic,words
        FROM nmf_topic_words
        WHERE nmf_model=%s;
        '''
    cursor.execute(q, (nmf_model,))
    results = cursor.fetchall()
    topic_words = pd.DataFrame(results, columns=['topic', 'words'])
    return topic_words
