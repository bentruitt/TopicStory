from conn import connect
import spacy
import scipy.spatial.distance as distance
import scipy.cluster.hierarchy as hcluster
import numpy as np
import psycopg2.extras

#############################################
###                                       ###
###  Store spacy vectors in the database. ###
###                                       ###
#############################################

def compute_spacy_text_vectors():
    from_table = 'articles'
    from_field = 'text'
    to_table = 'spacy_text_vectors'
    to_field = 'spacy_text_vector'
    nlp = spacy.load('en')
    func = lambda text: nlp(unicode(text)).vector.tolist()
    map_database_elements(from_table, from_field, to_table, to_field, func=func)

def compute_spacy_title_vectors():
    from_table = 'articles'
    from_field = 'title'
    to_table = 'spacy_title_vectors'
    to_field = 'spacy_title_vector'
    nlp = spacy.load('en')
    func = lambda text: nlp(unicode(text)).vector.tolist()
    map_database_elements(from_table, from_field, to_table, to_field, func=func)

###################################################################################
###                                                                             ###
###  The next several functions are helper functions for map_database_elements  ###
###                                                                             ###
###################################################################################

def map_database_elements(from_table, from_field, to_table, to_field, func):
    '''
    Maps old elements in the database to new elements in the database using
    a user-supplied function named func. Assumes the key is 'url' and to_table
    only has two fields, 'url' and to_field.

    Be careful when calling this function, since the first four parameters
    (from_table, from_field, to_table, and to_field) are NOT escaped,
    and will allow for sql injections if the user can access them. However,
    by always hard-coding strings when calling this function, there is
    no security risk.
    '''
    conn = connect()
    num_total = count_remaining(conn, from_table, to_table)
    num_remaining = num_total
    i = 1
    while num_remaining > 0:
        print '{} out of {}'.format(min(i*1000, num_total), num_total)
        map_database_batch(conn, from_table, from_field, to_table, to_field, func)
        num_remaining = count_remaining(conn, from_table, to_table)
        i += 1
    conn.close()

def count_remaining(conn, from_table, to_table):
    '''
    Count how many urls are in from_table which aren't in to_table.
    '''
    cursor = conn.cursor()
    q = '''
        SELECT COUNT(*)
        FROM '''+from_table+'''
        WHERE '''+from_table+'''.url NOT IN
        (SELECT url FROM '''+to_table+''');'''
    cursor.execute(q)
    num_remaining = cursor.fetchone()[0]
    return num_remaining

def map_database_batch(conn, from_table, from_field, to_table, to_field, func):
    '''
    Lookup 1000 elements of from_field in from_table, map using func, and store
    in to_field in to_table.
    '''
    url_fromvalue_pairs = lookup_fromvalues(conn, from_table, from_field, to_table)
    for url,fromvalue in url_fromvalue_pairs:
        tovalue = func(fromvalue)
        insert_tovalue(conn, url, to_table, to_field, tovalue)

def lookup_fromvalues(conn, from_table, from_field, to_table):
    cursor = conn.cursor()
    q = '''
        SELECT url,'''+from_field+'''
        FROM '''+from_table+'''
        WHERE '''+from_table+'''.url NOT IN
            (SELECT url FROM '''+to_table+''')
        LIMIT 1000;
        '''
    cursor.execute(q)
    results = cursor.fetchall()
    return results

def insert_tovalue(conn, url, to_table, to_field, tovalue):
    cursor = conn.cursor()
    q = '''
        INSERT INTO '''+to_table+''' (url, '''+to_field+''')
        VALUES (%s,%s);
        '''
    cursor.execute(q, (url, tovalue))
    conn.commit()

######################################################################################
###                                                                                ###
###  The next several functions are helper functions for compute_clusters_by_date  ###
###                                                                                ###
######################################################################################

def compute_clusters_by_date(conn, publish_date, threshold, from_table, from_field):
    url_ids, vectors = lookup_vectors_by_date(conn, from_table, from_field, publish_date)
    to_drop = vectors.mean(axis=1)==0
    vectors = vectors[~to_drop,:]
    url_ids = np.array(url_ids)[~to_drop].tolist()
    url_clusters = find_clusters(url_ids, vectors*10, threshold)
    url_infos = [[lookup_article_info(conn, url_id) for url_id in url_cluster] for url_cluster in url_clusters]
    return url_infos

def lookup_vectors_by_date(conn, from_table, from_field, publish_date):
    '''
    Lookup url ids and vectors, where the vectors are stored as from_field in from_table.
    Returns a list of url ids and a numpy array of vectors, where each row is an article
    and each column is a feature.

    Be careful when calling this function, since the two parameters
    (from_table, from_field) are NOT escaped,
    and will allow for sql injections if the user can access them. However,
    by always hard-coding strings when calling this function, there is
    no security risk.
    '''
    cursor = conn.cursor()
    q = '''
        SELECT vec.url,'''+from_field+'''
        FROM '''+from_table+''' AS vec
            JOIN articles
                ON vec.url=articles.url
                AND articles.date=%s;
        '''
    cursor.execute(q, (publish_date,))
    results = cursor.fetchall()
    url_ids, vectors = zip(*results)
    vectors = np.array(vectors)
    return url_ids, vectors

def find_clusters(url_ids, vectors, threshold):
    '''
    Clusters the url ids given corresponding vectors and a threshold.
    Returns the result as a list of lists, where each outer list is a cluster,
    and each inner list are the url ids in that cluster. Returns the outer
    list sorted in order of most-elements to least-elements per cluster.
    '''
    clusters = hcluster.fclusterdata(vectors, threshold, metric='cosine', criterion='distance', method='complete')
    cluster_ids, cluster_counts = np.unique(clusters, return_counts=True)
    sorted_cluster_ids = np.argsort(-cluster_counts)
    cluster_groups = [(clusters==cluster).nonzero()[0] for cluster in cluster_ids[sorted_cluster_ids]]
    url_groups = [[url_ids[idx] for idx in group] for group in cluster_groups]
    return url_groups

def lookup_article_info(conn, url_id):
    '''
    Looks up relevant information for a given url id.
    Returns the url string, article title, and name of the source.
    Returns the result as a dictionary with keys 'url', 'title', and 'source'.
    Assumes the url id exists in articles.
    '''
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    q = '''
        SELECT urls.url AS url, articles.title AS title, sources.name AS source
        FROM urls
            JOIN articles ON urls.id=articles.url
            JOIN sources ON articles.source=sources.id
        WHERE urls.id=%s;
        '''
    cursor.execute(q, (url_id,))
    results = dict(cursor.fetchone())
    return results
