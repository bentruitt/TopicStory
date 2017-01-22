import psycopg2.extras
import itertools
import datetime

class Urls:

    def __init__(self, conn):
        self.conn = conn

    def internal_urls(self, base_url):
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        q = '''SELECT id,url FROM urls WHERE url LIKE %s;'''
        cursor.execute(q, (base_url+'%',))
        urls = cursor.fetchall()
        return urls

class ArticleLabels:

    def __init__(self, conn):
        self.conn = conn

    def insert_many(self, urls, labels):
        for url,label in zip(urls,labels):
            self._insert(url['id'], label)

    def _insert(self, url, is_article):
        cursor = self.conn.cursor()
        q = '''
          INSERT INTO article_labels (url,is_article)
            SELECT %s,%s WHERE NOT EXISTS (
              SELECT url FROM article_labels WHERE url=%s
            );'''
        cursor.execute(q, (url,is_article,url))
        self.conn.commit()

class Articles:

    def __init__(self, conn):
        self.conn = conn

    def get_all_articles(self):
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        q = '''
            SELECT DISTINCT articles.url,articles.title,articles.text,articles.date
            FROM articles JOIN article_labels ON articles.url=article_labels.url
            WHERE article_labels.is_article=TRUE
            ORDER BY articles.url;'''
        cursor.execute(q)
        articles = cursor.fetchall()
        return articles

    def get_articles_by_date(self, date):
        if type(date) != datetime.date:
            raise ValueError('Argument `date` must be of type `datetime.date`')
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        q = '''
            SELECT articles.url,articles.title,articles.text,articles.date,sources.name
            FROM articles JOIN article_labels ON articles.url=article_labels.url
                JOIN sources ON articles.source=sources.id
            WHERE article_labels.is_article=TRUE
                AND articles.date=%s
            ORDER BY articles.url;'''
        cursor.execute(q, (date,))
        articles = cursor.fetchall()
        return articles

class CosineSimilarities:

    def __init__(self, conn):
        self.conn = conn

    def insert_similarities(self, articles, sims):
        # assumes order of indices in articles matches that of sims
        for (i1,i2) in itertools.combinations(range(len(articles)),2):
            self._insert(articles[i1]['url'], articles[i2]['url'], float(sims[i1][i2]))

    def _insert(self, u1, u2, sim):
        cursor = self.conn.cursor()
        (u1,u2) = sorted([u1,u2])
        q = '''
          INSERT INTO cosine_similarities (article_1,article_2,similarity)
            SELECT %s,%s,%s WHERE NOT EXISTS (
              SELECT article_1,article_2 FROM cosine_similarities
                WHERE article_1=%s
                  AND article_2=%s
            );
          '''
        cursor.execute(q, (u1,u2,sim,u1,u2))
        self.conn.commit()
