'''
Downloads articles for which the publish date was not be found through the crawler,
and re-download them through the newspaper API to see if the default newspaper
can find the publish date.
If so, then alter the crawler to download via the newspaper API by default
to have better chance of getting the publish date.
'''

from __future__ import division
import psycopg2
from newspaper import Article
import time

DB_USER = 'scott'
DB_PASSWORD = 'BZXa8ksLIGRAKwhmR4p6Eodcl'
DB_DATABASE = 'news'

def connect():
    conn = psycopg2.connect(database=DB_DATABASE, user=DB_USER, password=DB_PASSWORD)
    return conn

def find_articles_without_publish_date(conn):
    cursor = conn.cursor()
    q = '''
        SELECT urls.url
        FROM urls JOIN articles
            ON urls.id=articles.url
            JOIN article_labels
            ON urls.id=article_labels.url
        WHERE articles.date IS NULL
            AND article_labels.is_article=True
        LIMIT 10;'''
    cursor.execute(q)
    urls = cursor.fetchall()
    return urls

def test_download_publish_date(url):
    article = Article(url)
    article.download()
    article.parse()
    print 'url: {0}, beginning text: {1}, publish date: {2}'.format(url, article.text[:20], article.publish_date)

def test_download_simple():
    conn = connect()
    articles_without_publish_date = find_articles_without_publish_date(conn)
    print 'ARTICLES WITH NO PUBLISH DATE'
    print '-----------------------------'
    for url in articles_without_publish_date:
        print url[0]

    print ''
    print 'TESTING WITH NEWSPAPER'
    print '----------------------'
    for url in articles_without_publish_date:
        test_download_publish_date('http://www.' + url[0])
        time.sleep(20)

def fraction_with_publish_date(conn):
    cursor = conn.cursor()
    q_with_publish_date = '''
        SELECT sources.name AS source, COUNT(articles.url) as num_with_date
        FROM articles JOIN sources
            ON articles.source=sources.id
        WHERE articles.date IS NOT NULL
        GROUP BY sources.name;'''
    cursor.execute(q_with_publish_date)
    sources_with_publish_date = cursor.fetchall()
    print sources_with_publish_date

    q_without_publish_date = '''
        SELECT sources.name AS source, COUNT(articles.url) as num_with_date
        FROM articles JOIN sources
            ON articles.source=sources.id
        WHERE articles.date IS NULL
        GROUP BY sources.name;'''
    sources_without_publish_date = cursor.fetchall()
    print sources_without_publish_date

def test_fraction_with_publish_date():
    conn = connect()
    fraction_with_publish_date(conn)

if __name__ == '__main__':
    # test_download_simple()
    test_fraction_with_publish_date()
