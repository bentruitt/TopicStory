# This module contains helper functions for deciding which site to visit next.
import psycopg2.extras

def find_internal_urls(conn, base_url_string):
    '''
    Two inputs:
        conn - database connection
        base_url - string
    Returns a list of dictionaries, each dictionary has two elements:
        id - the url id in the database
        url - the url string
    Finds all internal urls in the database for a given base url.
    '''
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    q = '''SELECT id,url FROM urls WHERE url LIKE %s;'''
    cursor.execute(q, (base_url_string+'%',))
    urls = cursor.fetchall()
    urls = [dict(url) for url in urls]
    return urls

def allowed_by_robots(conn, url_id):
    '''
    Two inputs:
        conn - database connection
        url - integer, the url id in the database
    Returns a Boolean, True if allowed by robots.txt, False otherwise.
    '''
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    q = '''
      SELECT allowed FROM robots
        WHERE url=%s;'''
    cursor.execute(q, (url_id,))
    allowed = cursor.fetchone()[0]
    return allowed

def visited(conn, url_id):
    '''
    Two inputs:
        conn - database connection
        url_id - integer, the url id in the database
    Returns a boolean, True if already visited, False otherwise.
    '''
    cursor = conn.cursor()
    q = '''
      SELECT EXISTS (
        SELECT * FROM visits
          WHERE visit_url=%s
        );'''
    cursor.execute(q, (url_id,))
    return cursor.fetchone()[0]
