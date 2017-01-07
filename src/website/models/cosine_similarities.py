from articles import Articles

class CosineSimilarities:

    def __init__(self, conn):
        self.conn = conn

    def get_article_similarities(self, article_id):
        cursor = self.conn.cursor()
        q = '''
        SELECT sims.article_id,sims.similarity
          FROM
            (SELECT article_1 AS article_id,similarity
              FROM cosine_similarities
              WHERE article_2=%s
            UNION SELECT article_2,similarity
              FROM cosine_similarities
              WHERE article_1=%s) AS sims
        ORDER BY similarity DESC
        LIMIT 100;
            '''
        cursor.execute(q,(article_id,article_id))
        infos = cursor.fetchall()

        articles = Articles(self.conn)
        main_article = articles.lookup_article(article_id)
        compared_articles = [articles.lookup_article(info[0]) for info in infos]
        for article,info in zip(compared_articles,infos):
            article.similarity = info[1]
        return compared_articles
