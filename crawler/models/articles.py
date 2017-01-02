class Articles:

  def __init__(self, conn):
    self.conn = conn

  def insert(self, url, article):
    self._insert(url.id, article.title, article.text, article.publish_date)

  def _insert(self, url, title, text, date):
    cursor = self.conn.cursor()
    q = '''
      INSERT INTO articles (url,title,text,date)
        SELECT %s, %s, %s, %s WHERE NOT EXISTS (
          SELECT url FROM articles WHERE url=%s
        );'''
    cursor.execute(q, (url, title, text, date, url))
    self.conn.commit()
