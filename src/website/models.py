import psycopg2.extras

class Articles:

    def __init__(self, conn):
        self.conn = conn

    def lookup_recent_articles(self, conn):
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        q = '''
            SELECT sources.name, articles.title, urls.url
                FROM urls
                    JOIN articles ON urls.id=articles.url
                    JOIN sources ON urls.
            '''


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
