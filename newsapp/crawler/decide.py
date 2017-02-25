# This module contains helper functions for deciding which site to visit next.
import psycopg2.extras

def visited_base_url(conn, crawl_id):
    '''
    Two inputs:
        conn - database connection
        crawl_id - id for a given crawl
    Returns True if this crawl visited the base_url, False otherwise.
    '''
    cursor = conn.cursor()
    q = '''
        SELECT EXISTS
            (SELECT 1
            FROM crawls
                JOIN sources ON crawls.source=sources.id
                JOIN visits ON crawls.id=visits.crawl
                AND visits.visit_url=sources.base_url
                AND crawls.id=%s);
        '''
    cursor.execute(q, (crawl_id,))
    result = cursor.fetchone()[0]
    return result

def find_unvisited_internal_urls(conn, crawl_id, base_url_string):
    '''
    Two inputs:
        conn - database connection
        base_url - string
    Returns a list of dictionaries, each dictionary has two elements:
        id - the url id in the database
        url - the url string
    Finds all internal urls in the database for a given base url,
        which haven't been visited during this crawl yet.
    '''
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    q = '''
        WITH already_visited AS (
            SELECT visit_url
            FROM visits
            WHERE crawl=%s
        )
        SELECT id,url
        FROM urls
        WHERE url LIKE %s
            AND id NOT IN (SELECT visit_url FROM already_visited);'''
    cursor.execute(q, (crawl_id, base_url_string+'%',))
    urls = cursor.fetchall()
    urls = [dict(url) for url in urls]
    return urls
