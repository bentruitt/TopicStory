import numpy as np
import psycopg2.extras
import models

class Score:

    def __init__(self, base_url, conn):
        self.base_url = base_url
        self.conn = conn

    def decide_next_visit(self):
        scores = self.compute_scores()
        urls,probs = zip(*scores)
        probs = np.array(probs).astype(float)
        probs /= np.sum(probs)
        next_url = np.random.choice(urls,p=probs)
        return next_url

    def compute_scores(self):
        internal_urls = self.fetch_internal_urls()
        return  [(url,self.score(url)) for url in internal_urls]

    # TODO: move this function to models
    def fetch_internal_urls(self):
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        q = '''SELECT id,url FROM urls WHERE url LIKE %s;'''
        cursor.execute(q, (self.base_url['url']+'%',))
        urls = cursor.fetchall()
        urls = [dict(url) for url in urls]
        return urls

    def score(self, url):
        score = 0
        if not self.allowed_by_robots(url):
            score = 0
        elif not self.visited(url):
            score = 5
        else:
            score = 1
        return score

    # TODO: move this function to models
    def allowed_by_robots(self, url):
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        q = '''
          SELECT allowed FROM robots
            WHERE url=%s;'''
        cursor.execute(q, (url['id'],))
        allowed = cursor.fetchone()
        return allowed

    # TODO: move this function to models
    def visited(self, url):
        cursor = self.conn.cursor()
        q = '''
          SELECT EXISTS (
            SELECT * FROM visits
              WHERE visit_url=%s
            );'''
        cursor.execute(q, (url['id'],))
        return cursor.fetchone()[0]
