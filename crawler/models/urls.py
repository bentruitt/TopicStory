import util

class Urls:

  def __init__(self, conn):
    self.conn = conn

  def insert_many(self, url_strings):
    return [self.insert(url_string) for url_string in url_strings]

  def insert(self, url_string):
    url_string = util.clean_url(url_string)
    url = self._lookup(url_string)
    if url is None:
      url = self._insert(url_string)
    return url

  def _lookup(self, url_string):
    cursor = self.conn.cursor()
    q = '''SELECT id FROM urls WHERE url=%s;'''
    cursor.execute(q, (url_string,))
    url_id = cursor.fetchone()
    if url_id is None:
      return None
    else:
      return Url(url_id[0],url_string)

  def _insert(self, url_string):
    cursor = self.conn.cursor()
    q = '''
      INSERT INTO urls (url)
        SELECT %s WHERE NOT EXISTS (
          SELECT url FROM urls WHERE url=%s
        ) RETURNING id;'''
    cursor.execute(q, (url_string,url_string))
    url_id = cursor.fetchone()[0]
    url = Url(url_id,url_string)
    self.conn.commit()
    return url

class Url:

  def __init__(self, id, url):
    self.id = id
    self.url = url
