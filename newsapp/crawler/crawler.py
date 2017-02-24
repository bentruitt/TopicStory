import time
import threading
import logging
import traceback
import datetime
import os
import sys
import re

import util
import models
from config import MAX_CRAWL_TIME, TIME_BETWEEN_REQUESTS
from conn import connect

def crawl(base_url_string):
    crawler = Crawler(base_url_string)
    crawler.crawl()

class Crawler:
    '''
    Abstract class for crawling a news source.
    '''

    def __init__(self):
        '''
        Abstract function for initializing crawlers.
        Needs to define:
            -> self.base_url_string (eg, 'foxnews.com')
            -> self.article_regex (regular expression which matches article urls)
        '''
        return NotImplemented

    def sleep(self):
        '''
        Abstract function for waiting between requests.
        Can add additional functionality, such as random sleep times.
        '''
        return NotImplemented

    def decide_next_visit(self, conn):
        '''
        Abstract function for deciding which url to visit next.
        Returns the url as a string.
        '''
        return NotImplemented

    def is_article(self, url):
        '''
        Not abstract.
        Returns True if the url is an article, false otherwise.
        '''
        article_regex = self.article_regex
        return bool(re.search(article_regex, url))

    def crawl(self):
        base_url_string = self.base_url_string

        conn = connect()
        start_time = time.time()
        initialize_logging(base_url_string)
        logging.info('STARTING CRAWL AT TIME: {0}'.format(util.time_string(start_time)))
    
        urls = models.Urls(conn)
        base_url = urls.insert(base_url_string)
    
        sources = models.Sources(conn)
        source_name = util.extract_source(base_url_string)
        source = sources.insert(base_url, source_name)
    
        robots = models.Robots(base_url, conn)
        robots.insert(base_url)
    
        visits = models.Visits(source,conn)
        links = models.Links(conn)
        articles = models.Articles(conn)
    
        while (time.time() - start_time < MAX_CRAWL_TIME):
            visit_url = self.decide_next_visit(conn)
            logging.info('VISIT: {0}, {1}'.format(util.time_string(time.time()), visit_url['url']))
    
            try:
                article = util.download_article(visit_url['url'])
                html_text = article.html
                found_links = util.extract_links(html_text, base_url['url'])
                found_urls = urls.insert_many(found_links)
                robots.insert_many(found_urls)
                visit = visits.insert(visit_url)
                links.insert_many(visit, found_urls)
                if self.is_article(visit_url['url']):
                    articles.insert(visit_url, article, source)
            except Exception as e:
                logging.error('Error when downloading {0}'.format(visit_url['url']))
                logging.error(traceback.format_exc())
    
            self.sleep()

def initialize_logging(base_url):
    log_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    source_str = util.extract_source(base_url)
    log_filename = 'LOG_{0}.log'.format(source_str)
    log_path = os.path.join(log_dir, log_filename)
    logging.basicConfig(filename=log_path, filemode='a', level=logging.INFO)
    stderrLogger=logging.StreamHandler()
    stderrLogger.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
    logging.getLogger().addHandler(stderrLogger)
    sys.excepthook = log_unchecked_exception

def log_unchecked_exception(exctype, value, tb):
    log_str = '''
UNCHECKED EXCEPTION
    Type: {}
    Value: {}
    Traceback: {}'''.format(exctype, value, tb)
    logging.error(log_str)
