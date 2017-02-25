import psycopg2.extras
# import robotparser as rp
import numpy as np

import util

def insert_urls(conn, url_strings):
    '''
    Inserts many urls into the database.
    Returns a list of url_ids
    '''
    url_ids = []
    for url_string in url_strings:
        url_id = insert_url(conn, url_string)
        url_ids.append(url_id)
    return url_ids

def insert_url(conn, url_string):
    '''
    Inserts a url into the database, unless it already exists.
    Always returns the corresponding url_id in the database,
        regardless if it already existed or was just inserted.
    '''
    url_string = util.clean_url(url_string)

    cursor = conn.cursor()
    # borrowed much of this query from a stackoverflow post
    # http://stackoverflow.com/questions/18192570/insert-if-not-exists-else-return-id-in-postgresql
    q = '''
        WITH s AS (
            SELECT id
            FROM urls
            WHERE url=%s
        ), i AS (
            INSERT INTO urls (url)
            SELECT %s WHERE NOT EXISTS
                (SELECT 1 FROM s)
            RETURNING id
        )
        SELECT id FROM i
        UNION ALL
        SELECT id from s;
        '''
    cursor.execute(q, (url_string,url_string))
    url_id = cursor.fetchone()[0]
    conn.commit()
    return url_id

def insert_source(conn, base_url_string):
    '''
    Inserts a source into the database, unless it already exists.
    Always returns the corresponding source_id in the database,
        regardless if it already existed or was just inserted.
    Gets the name of the source from the base_url_string,
        looks for anything between the www. and the first dot.
    '''
    source_name = util.extract_source(base_url_string)

    cursor = conn.cursor()
    # borrowed much of this query from a stackoverflow post
    # http://stackoverflow.com/questions/18192570/insert-if-not-exists-else-return-id-in-postgresql
    q = '''
        WITH s AS (
            SELECT id
            FROM sources
            WHERE name=%s
        ), i AS (
            INSERT INTO sources (base_url,name)
            SELECT (SELECT id FROM urls WHERE url=%s),%s WHERE NOT EXISTS
                (SELECT 1 FROM s)
            RETURNING id
        )
        SELECT id FROM i
        UNION ALL
        SELECT id from s;
        '''
    cursor.execute(q, (source_name,base_url_string,source_name))
    source_id = cursor.fetchone()[0]
    conn.commit()
    return source_id

def insert_crawl(conn, base_url_string):
    '''
    Inserts a crawl into the database.
    Will always be a new crawl.
    Returns the corresponding crawl_id in the database
    '''
    source_name = util.extract_source(base_url_string)

    cursor = conn.cursor()
    # borrowed much of this query from a stackoverflow post
    # http://stackoverflow.com/questions/18192570/insert-if-not-exists-else-return-id-in-postgresql
    q = '''
        INSERT INTO crawls (source)
        SELECT (SELECT id FROM sources WHERE name=%s)
        RETURNING id;
        '''
    cursor.execute(q, (source_name,))
    crawl_id = cursor.fetchone()[0]
    conn.commit()
    return crawl_id

def insert_visit(conn, crawl_id, visit_url_id):
    '''
    Inserts a visit into the database.
    Will always be a new visit.
    Returns the corresponding visit_id in the database.
    '''
    cursor = conn.cursor()
    q = '''
        INSERT INTO visits (crawl, visit_url, visit_time)
        VALUES (%s, %s, NOW())
        RETURNING id;
        '''
    cursor.execute(q, (crawl_id, visit_url_id))
    visit_id = cursor.fetchone()[0]
    conn.commit()
    return visit_id

def insert_links(conn, visit_id, to_url_ids):
    '''
    Inserts many links into the database.
    Takes three parameters:
        conn - database connection
        visit_id - id of this visit
        to_url_ids - list of found links from visited url
    Does not return any values
    '''
    for to_url_id in to_url_ids:
        insert_link(conn, visit_id, to_url_id)

def insert_link(conn, visit_id, to_url_id):
    '''
    Inserts a link into the database.
    Does not return any values.
    '''
    cursor = conn.cursor()
    q = '''
        INSERT INTO links (visit, to_url)
        VALUES (%s, %s)
        '''
    cursor.execute(q, (visit_id, to_url_id))
    conn.commit()

def insert_article(conn, url_id, article_title, article_text, article_date, article_source):
    '''
    Inserts an article into the database if the article has not already been inserted.
    Does not return any values.
    '''
    cursor = conn.cursor()
    q = '''
        INSERT INTO articles (url, title, text, date, source)
        SELECT %s, %s, %s, %s, %s WHERE NOT EXISTS (
            SELECT url FROM articles WHERE url=%s
        );
        '''
    cursor.execute(q, (url_id, article_title, article_text, article_date, article_source, url_id))
    conn.commit()
