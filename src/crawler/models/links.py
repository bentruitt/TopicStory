class Links:

  def __init__(self, conn):
    self.conn = conn

  def insert_many(self, visit, urls):
    for url in urls:
      self.insert(visit, url)

  def insert(self, visit, url):
    self._insert(visit.id, url.id)

  def _insert(self, visit_id, url_id):
    cursor = self.conn.cursor()
    q = '''
      INSERT INTO links (visit,to_url)
        VALUES (%s, %s);'''
    cursor.execute(q, (visit_id, url_id))
    self.conn.commit()
