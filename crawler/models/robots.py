import robotparser as rp

import util

class Robots:

  def __init__(self, base_url, conn):
    robots_url = util.robots_url(base_url.url)
    self.robotparser = rp.RobotFileParser()
    self.robotparser.set_url(robots_url)
    self.robotparser.read()
    self.conn = conn

  def insert_many(self, urls):
    for url in urls:
      self.insert(url)

  def insert(self, url):
    url_string = util.add_prefix(url.url)
    allowed = self.is_allowed(url_string)
    self._insert(url.id, allowed)

  def _insert(self, url_id, allowed):
    cursor = self.conn.cursor()
    q = '''
      INSERT INTO robots (url,allowed)
        SELECT %s,%s
        WHERE NOT EXISTS
          (SELECT url FROM robots WHERE url=%s);'''
    cursor.execute(q, (url_id, allowed, url_id))
    self.conn.commit()

  def is_allowed(self, url):
    return self.robotparser.can_fetch("*", url)
