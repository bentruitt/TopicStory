class Articles:

  def __init__(self, conn):
    self.conn = conn

  def get_all_articles(self):
    cursor = self.conn.cursor()
    q = '''
      SELECT DISTINCT articles.url,articles.title,articles.text,articles.date
        FROM articles JOIN article_labels ON articles.url=article_labels.url
        WHERE article_labels.is_article=TRUE
        ORDER BY articles.url;'''
    cursor.execute(q)
    infos = cursor.fetchall()
    articles = [Article(*info) for info in infos]
    return articles

class Article:

  def __init__(self, url, title, text, publish_date):
    self.url = url
    self.title = title
    self.text = text
    self.publish_date = publish_date
