class Urls:

  def __init__(self, conn):
    self.conn = conn

  def internal_urls(self, base_url):
    cursor = self.conn.cursor()
    q = '''SELECT id,url FROM urls WHERE url LIKE %s;'''
    cursor.execute(q, (base_url+'%',))
    results = cursor.fetchall()
    urls = [Url(*row) for row in results]
    return urls

class Url:

  def __init__(self, id, url):
    self.id = id
    self.url = url
