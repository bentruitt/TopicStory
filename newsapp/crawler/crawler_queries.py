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

# class Urls:
# 
#     def __init__(self, conn):
#         self.conn = conn
# 
#     def insert_many(self, url_strings):
#         return [self.insert(url_string) for url_string in url_strings]
# 
#     def insert(self, url_string):
#         url_string = util.clean_url(url_string)
#         url = self._lookup(url_string)
#         if url is None:
#             url = self._insert(url_string)
#         return url
# 
#     def _lookup(self, url_string):
#         cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
#         q = '''SELECT id,url FROM urls WHERE url=%s;'''
#         cursor.execute(q, (url_string,))
#         url = cursor.fetchone()
#         return url
# 
#     def _insert(self, url_string):
#         cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
#         q = '''
#           INSERT INTO urls (url)
#             SELECT %s WHERE NOT EXISTS (
#               SELECT url FROM urls WHERE url=%s
#             ) RETURNING id,url;'''
#         cursor.execute(q, (url_string,url_string))
#         url = cursor.fetchone()
#         self.conn.commit()
#         return url
# 
# class Sources:
# 
#     def __init__(self, conn):
#         self.conn = conn
# 
#     def insert(self, source_url, source_name):
#         source = self._lookup(source_url['id'])
#         if source is None:
#             source = self._insert(source_url['id'], source_name)
#         return source
# 
#     def _lookup(self, source_url_id):
#         cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
#         q = '''SELECT id,name,base_url FROM sources WHERE base_url=%s;'''
#         cursor.execute(q, (source_url_id,))
#         source = cursor.fetchone()
#         return source
# 
#     def _insert(self, base_url_id, source_name):
#         cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
#         q = '''
#             INSERT INTO sources (name, base_url)
#                 VALUES (%s,%s)
#                 RETURNING id,name,base_url;'''
#         cursor.execute(q, (source_name, base_url_id))
#         source = cursor.fetchone()
#         self.conn.commit()
#         return source
# 
# class Robots:
# 
#     def __init__(self, base_url, conn):
#         robots_url = util.robots_url(base_url['url'])
#         self.robotparser = rp.RobotFileParser()
#         self.robotparser.set_url(robots_url)
#         self.robotparser.read()
#         self.conn = conn
# 
#     def insert_many(self, urls):
#         for url in urls:
#             self.insert(url)
# 
#     def insert(self, url):
#         url_string = util.add_prefix(url['url'])
#         allowed = self.is_allowed(url_string)
#         self._insert(url['id'], allowed)
# 
#     def _insert(self, url_id, allowed):
#         cursor = self.conn.cursor()
#         q = '''
#           INSERT INTO robots (url,allowed)
#             SELECT %s,%s
#             WHERE NOT EXISTS
#               (SELECT url FROM robots WHERE url=%s);'''
#         cursor.execute(q, (url_id, allowed, url_id))
#         self.conn.commit()
# 
#     def is_allowed(self, url):
#         return self.robotparser.can_fetch("*", url)
# 
# class Visits:
# 
#     def __init__(self, source, conn):
#         self.source = source
#         self.conn = conn
# 
#     def insert(self, visit_url):
#         return self._insert(self.source['base_url'], visit_url['id'])
# 
#     def _insert(self, source_id, visit_url_id):
#         cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
#         q = '''
#           INSERT INTO visits (source,visit_url,visit_time)
#             VALUES (%s,%s,NOW())
#             RETURNING id,visit_time;'''
#         cursor.execute(q, (source_id, visit_url_id))
#         visit = cursor.fetchone()
#         self.conn.commit()
#         return visit
# 
# class Links:
# 
#     def __init__(self, conn):
#         self.conn = conn
# 
#     def insert_many(self, visit, urls):
#         for url in urls:
#             self.insert(visit, url)
# 
#     def insert(self, visit, url):
#         self._insert(visit['id'], url['id'])
# 
#     def _insert(self, visit_id, url_id):
#         cursor = self.conn.cursor()
#         q = '''
#           INSERT INTO links (visit,to_url)
#             VALUES (%s, %s);'''
#         cursor.execute(q, (visit_id, url_id))
#         self.conn.commit()
# 
# class Articles:
# 
#     def __init__(self, conn):
#         self.conn = conn
# 
#     def insert(self, url, article, source):
#         self._insert(url['id'], article.title, article.text, article.publish_date, source['id'])
# 
#     def _insert(self, url_id, title, text, date, source_id):
#         cursor = self.conn.cursor()
#         q = '''
#           INSERT INTO articles (url,title,text,date,source)
#             SELECT %s, %s, %s, %s, %s WHERE NOT EXISTS (
#               SELECT url FROM articles WHERE url=%s
#             );'''
#         cursor.execute(q, (url_id, title, text, date, source_id, url_id))
#         self.conn.commit()
