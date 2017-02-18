from conn import connect
import spacy

def compute_headline_vectors():
    conn = connect()
    nlp = spacy.load('en')
    num_articles = count_remaining_headlines(conn)
    i = 1
    while count_remaining_headlines(conn) > 0:
        print '{} out of {}'.format(i*1000, num_articles)
        compute_headline_vector_batch(conn, nlp)
        i += 1
    conn.close()

def count_remaining_headlines(conn):
    '''
    Count how many article headlines are in the database which aren't in article_headline_vectors.
    '''
    cursor = conn.cursor()
    q = '''
        SELECT COUNT(*)
        FROM articles
        WHERE articles.url NOT IN (SELECT url FROM article_headline_vectors);
        '''
    cursor.execute(q)
    num_articles_left = cursor.fetchone()[0]
    return num_articles_left

def compute_headline_vector_batch(conn, nlp):
    url_headline_pairs = lookup_headlines(conn)
    for url,headline in url_headline_pairs:
        X = nlp(unicode(headline)).vector
        insert_headline_vector(conn, url, X.tolist())

def lookup_headlines(conn):
    '''
    Look up headlines from the database which are not already in article_headline_vectors.
    Limits to 1000, unless there aren't any.
    '''
    cursor = conn.cursor()
    q = '''
        SELECT url,title
        FROM articles
        WHERE articles.url NOT IN (SELECT url FROM article_headline_vectors)
        LIMIT 1000;
        '''
    cursor.execute(q)
    results = cursor.fetchall()
    return results

def insert_headline_vector(conn, url, X):
    '''
    Insert a headline vector for a given article into the database.
    '''
    cursor = conn.cursor()
    q = '''
        INSERT INTO article_headline_vectors (url, headline_vector)
        VALUES (%s,%s);
        '''
    cursor.execute(q, (url, X))
    conn.commit()
