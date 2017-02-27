import pandas as pd
import psycopg2.extras

def load_articles(conn, start_date, end_date):
    # cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor = conn.cursor()
    q = '''
        SELECT urls.url AS url, title, text, date, sources.name AS source
        FROM articles
            JOIN urls ON articles.url=urls.id
            JOIN sources ON articles.source=sources.id
        WHERE date >= %s
            AND date <= %s;
        '''
    cursor.execute(q, (start_date, end_date))
    results = cursor.fetchall()
    articles = pd.DataFrame(results, columns=['url', 'title', 'text', 'date', 'source'])
    return articles
