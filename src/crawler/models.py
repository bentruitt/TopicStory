import psycopg2.extras
import robotparser as rp

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
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        q = '''SELECT id,url FROM urls WHERE url=%s;'''
        cursor.execute(q, (url_string,))
        url = cursor.fetchone()
        return url

    def _insert(self, url_string):
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        q = '''
          INSERT INTO urls (url)
            SELECT %s WHERE NOT EXISTS (
              SELECT url FROM urls WHERE url=%s
            ) RETURNING id,url;'''
        cursor.execute(q, (url_string,url_string))
        url = cursor.fetchone()
        self.conn.commit()
        return url

class Sources:

    def __init__(self, conn):
        self.conn = conn

    def insert(self, source_url, source_name):
        source = self._lookup(source_url['id'])
        if source is None:
            source = self._insert(source_url['id'], source_name)
        return source

    def _lookup(self, source_url_id):
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        q = '''SELECT name,base_url FROM sources WHERE base_url=%s;'''
        cursor.execute(q, (source_url_id,))
        source = cursor.fetchone()
        return source

    def _insert(self, base_url_id, source_name):
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        q = '''
            INSERT INTO sources (name, base_url)
                VALUES (%s,%s)
                RETURNING name,base_url;'''
        cursor.execute(q, (source_name, base_url_id))
        source = cursor.fetchone()
        self.conn.commit()
        return source

class Robots:

    def __init__(self, base_url, conn):
        robots_url = util.robots_url(base_url['url'])
        self.robotparser = rp.RobotFileParser()
        self.robotparser.set_url(robots_url)
        self.robotparser.read()
        self.conn = conn

    def insert_many(self, urls):
        for url in urls:
            self.insert(url)

    def insert(self, url):
        url_string = util.add_prefix(url['url'])
        allowed = self.is_allowed(url_string)
        self._insert(url['id'], allowed)

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

class Visits:

    def __init__(self, source, conn):
        self.source = source
        self.conn = conn

    def insert(self, visit_url):
        return self._insert(self.source['base_url'], visit_url['id'])

    def _insert(self, source_id, visit_url_id):
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        q = '''
          INSERT INTO visits (source,visit_url,visit_time)
            VALUES (%s,%s,NOW())
            RETURNING id,visit_time;'''
        cursor.execute(q, (source_id, visit_url_id))
        visit = cursor.fetchone()
        self.conn.commit()
        return visit

class Links:

    def __init__(self, conn):
        self.conn = conn

    def insert_many(self, visit, urls):
        for url in urls:
            self.insert(visit, url)

    def insert(self, visit, url):
        self._insert(visit['id'], url['id'])

    def _insert(self, visit_id, url_id):
        cursor = self.conn.cursor()
        q = '''
          INSERT INTO links (visit,to_url)
            VALUES (%s, %s);'''
        cursor.execute(q, (visit_id, url_id))
        self.conn.commit()

class Articles:

    def __init__(self, conn):
        self.conn = conn

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
