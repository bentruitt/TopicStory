import psycopg2.extras

class Articles:

    def __init__(self, conn):
        self.conn = conn

    def count_articles(self):
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        q = '''SELECT COUNT(*) AS num_articles FROM articles;'''
        cursor.execute(q)
        num_articles = cursor.fetchone()['num_articles']
        return num_articles
    
    def count_articles_by_source(self):
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        q = '''
            SELECT sources.name AS source_name, COUNT(*) AS num_articles
            FROM articles JOIN sources ON articles.source = sources.id
            GROUP BY sources.name
            ORDER BY sources.name ASC;
            '''
        cursor.execute(q)
        articles_by_source = cursor.fetchall()
        return articles_by_source

    def count_articles_by_date(self):
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        q = '''
            SELECT articles.date AS publish_date, COUNT(*) AS num_articles
            FROM articles
            GROUP BY date
            ORDER BY publish_date DESC;
            '''
        cursor.execute(q)
        articles_by_date = cursor.fetchall()
        return articles_by_date

    def lookup_recent_articles(self, conn):
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        q = '''
            SELECT sources.name, articles.title, urls.url
                FROM urls
                    JOIN articles ON urls.id=articles.url
                    JOIN sources ON urls.
            '''
        return None


    def insert(self, url, article):
        self._insert(url['id'], article.title, article.text, article.publish_date)

    def _insert(self, url, title, text, date):
        cursor = self.conn.cursor()
        q = '''
          INSERT INTO articles (url,title,text,date)
            SELECT %s, %s, %s, %s WHERE NOT EXISTS (
              SELECT url FROM articles WHERE url=%s
            );'''
        cursor.execute(q, (url, title, text, date, url))
        self.conn.commit()
