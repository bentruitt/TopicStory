class ArticleLabels:

    def __init__(self, conn):
        self.conn = conn

    def insert_many(self, urls, labels):
        for url,label in zip(urls,labels):
            self._insert(url.id, label)

    def _insert(self, url, is_article):
        cursor = self.conn.cursor()
        q = '''
          INSERT INTO article_labels (url,is_article)
            SELECT %s,%s WHERE NOT EXISTS (
              SELECT url FROM article_labels WHERE url=%s
            );'''
        cursor.execute(q, (url,is_article,url))
        self.conn.commit()
