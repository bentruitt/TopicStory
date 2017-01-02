class Visits:

  def __init__(self, base_url, conn):
    self.base_url = base_url
    self.conn = conn

  def insert(self, visit_url):
    return self._insert(self.base_url.id, visit_url.id)

  def _insert(self, base_url_id, visit_url_id):
    cursor = self.conn.cursor()
    q = '''
      INSERT INTO visits (base_url,visit_url,visit_time)
        VALUES (%s,%s,NOW())
        RETURNING id,visit_time;'''
    cursor.execute(q, (base_url_id, visit_url_id))
    visit_id,visit_time = cursor.fetchone()
    visit = Visit(visit_id, base_url_id, visit_url_id, visit_time)
    self.conn.commit()
    return visit

class Visit:

  def __init__(self, id, base_url, visit_url, visit_time):
    self.id = id
    self.base_url = base_url
    self.visit_url = visit_url
    self.visit_time = visit_time
