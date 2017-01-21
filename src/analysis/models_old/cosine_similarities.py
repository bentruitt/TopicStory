import itertools

class CosineSimilarities:

    def __init__(self, conn):
        self.conn = conn

    def insert_similarities(self, articles, sims):
        # assumes order of indices in articles matches that of sims
        for (i1,i2) in itertools.combinations(range(len(articles)),2):
            self._insert(articles[i1].url, articles[i2].url, float(sims[i1][i2]))

    def _insert(self, u1, u2, sim):
        cursor = self.conn.cursor()
        (u1,u2) = sorted([u1,u2])
        q = '''
          INSERT INTO cosine_similarities (article_1,article_2,similarity)
            SELECT %s,%s,%s WHERE NOT EXISTS (
              SELECT article_1,article_2 FROM cosine_similarities
                WHERE article_1=%s
                  AND article_2=%s
            );
          '''
        cursor.execute(q, (u1,u2,sim,u1,u2))
        self.conn.commit()
