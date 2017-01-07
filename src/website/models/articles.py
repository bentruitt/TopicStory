from urls import Url

class Articles:

    def __init__(self, conn):
        self.conn = conn

    def get_random_article(self):
        cursor = self.conn.cursor()
        q = '''
          SELECT urls.url,urls.id,articles.title,articles.text,articles.date
            FROM urls JOIN articles ON articles.url=urls.id
                              JOIN article_labels ON articles.url=article_labels.url
            WHERE article_labels.is_article=TRUE
            ORDER BY random()
            LIMIT 1;'''
        cursor.execute(q)
        info = cursor.fetchone()
        article = Article(*info)
        return article

    def get_all_articles(self):
        cursor = self.conn.cursor()
        q = '''
          SELECT urls.url,urls.id,articles.title,articles.text,articles.date
            FROM urls JOIN articles ON articles.url=urls.id
                              JOIN article_labels ON articles.url=article_labels.url
            WHERE article_labels.is_article=TRUE
            ORDER BY urls.url;'''
        cursor.execute(q)
        infos = cursor.fetchall()
        articles = [Article(*info) for info in infos]
        return articles

    def lookup_article(self, article_id):
        cursor = self.conn.cursor()
        q = '''
          SELECT urls.url,urls.id,articles.title,articles.text,articles.date
            FROM urls JOIN articles ON urls.id=articles.url
            WHERE articles.url=%s;'''
        cursor.execute(q,(article_id,))
        info = cursor.fetchone()
        article = Article(*info)
        return article

class Article:

    def __init__(self, url, url_id, title, text, date):
        # note, url is the string, not the id (this is a more useful abstraction)
        # the url_id is stored anyway
        self.url = url
        self.url_id = url_id
        self.title = title
        self.text = text
        self.date = date
