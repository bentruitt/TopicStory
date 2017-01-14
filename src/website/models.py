import psycopg2.extras
import datetime
import string

class Articles:

    def __init__(self, conn):
        self.conn = conn

    def count_articles(self, by=None, source_name=None, publish_date=None):
        '''Counts articles in the database.
        INPUT:
            by: str
                Groups the counts by a certain property.
                If 'source', then groups by source name.
                If 'date', then groups by publish date.
                If None, then returns a total count.
            source_name: unicode
                Constrains the count for a given source.
                If None, then returns a total count over all the sources.
            publish_date: datetime.date object
                Constrains the count for a given date.
                If None, then returns a total count over all the dates.
        OUTPUT: int or list of dicts
            int, if by is None
            dict list, if by is present. Keys are source names or dates, values are ints.
        '''

        # validate inputs
        if (by is not None) and (type(by) != str):
            raise ValueError('Argument `by` must either be `None` or of type `str`')
        if (source_name is not None) and (type(source_name) != unicode):
            raise ValueError('Argument `source_name` must either be `None` or of type `unicode`')
        if (publish_date is not None) and (type(publish_date) != datetime.date):
            raise ValueError('Argument `publish_date` must either be `None` or of type `datetime.date`')
        if (by is not None) and (by not in ['source', 'date']):
            raise ValueError('If argument `by` is provided, must either be `source` or `date`')
        if by=='source' and source_name is not None:
            raise ValueError('By cannot be `source` when `source_name` is provided.')
        if by=='publish_date' and publish_date is not None:
            raise ValueError('By cannot be `date` when `publish_date` is provided.')

        # build base query
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        q_select = '''SELECT COUNT(*) AS num_articles '''
        q_from = '''FROM articles JOIN sources ON articles.source=sources.id '''
        q_where = '''''';
        q_group = '''''';
        q_order = '''''';
        query_args = []

        # add constraints
        if source_name and publish_date:
            q_where += '''WHERE sources.name=%s AND articles.date=%s'''
            query_args.append(source_name)
            query_args.append(publish_date)
        elif source_name:
            q_where += '''WHERE sources.name=%s'''
            query_args.append(source_name)
        elif publish_date:
            q_where += '''WHERE articles.date=%s'''
            query_args.append(publish_date)

        # add group by clauses
        if by=='source':
            q_select += ''', sources.name AS source_name'''
            q_group += '''GROUP BY source_name'''
            q_order += '''ORDER BY source_name ASC'''
        elif by=='date':
            q_select += ''', articles.date AS publish_date'''
            q_group += '''GROUP BY publish_date'''
            q_order += '''ORDER BY publish_date DESC'''

        # putting everything together
        q = string.join([q_select, q_from, q_where, q_group, q_order, ';'], sep='\n')
        cursor.execute(q, tuple(query_args))
        if by is None:
            result = cursor.fetchone()['num_articles']
        else:
            result = cursor.fetchall()
        return result


    def lookup_recent_articles(self, conn):
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        q = '''
            SELECT sources.name, articles.title, urls.url
                FROM urls
                    JOIN articles ON urls.id=articles.url
                    JOIN sources ON urls.
            '''
        return None

    def insert(self, url, article):
        self._insert(url['id'], article.title, article.text, article.publish_date)

    def _insert(self, url, title, text, date):
        cursor = self.conn.cursor()
        q = '''
          INSERT INTO articles (url,title,text,date)
            SELECT %s, %s, %s, %s WHERE NOT EXISTS (
              SELECT url FROM articles WHERE url=%s
            );'''
        cursor.execute(q, (url, title, text, date, url))
        self.conn.commit()

class Sources:

    def __init__(self, conn):
        self.conn = conn

    def lookup_exists(self, source_name):
        cursor = self.conn.cursor()
        q = '''SELECT EXISTS(SELECT 1 FROM sources WHERE name=%s);'''
        cursor.execute(q, (source_name,))
        exists = cursor.fetchone()[0]
        return exists

