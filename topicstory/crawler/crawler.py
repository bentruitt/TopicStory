import time
import threading
import logging
import traceback
import datetime
import os
import sys
import re
import robotparser as rp
import numpy as np
import random

import util
import decide
import queries
from conn import connect

class Crawler:
    '''
    Abstract class for crawling a news source.
    '''

    ########################
    #                      #
    #  Abstract functions  #
    #                      #
    ########################

    def sleep(self):
        '''
        Abstract function for waiting between requests.
        Can add additional functionality, such as random sleep times.
        '''
        return NotImplemented

    def is_article(self, url):
        '''
        Abstract function for determining if a url is an article or not.
        Returns True if the url is an article, false otherwise.
        '''
        return NotImplemented

    def extract_date_from_url(self, url):
        '''
        Abstract function for parsing a date from a url.
        Currently crawler only works for sources with dates in their urls.
        Takes a url as a string, returns a datetime.date object.
        '''
        return NotImplemented

    ############################
    #                          #
    #  Non-Abstract functions  #
    #                          #
    ############################

    def __init__(self, base_url_string):
        '''
        Not abstract.
        Parameters:
            base_url_string, a string representing the base url for a source (eg, foxnews.com)
            article_regex, a string representing a regex which only matches for articles
        '''
        self.base_url_string = base_url_string
        self.initialize_robots()

    def initialize_robots(self):
        '''
        Not abstract.
        Initializes a robot parser for the crawler.
        Use self.robot_parser.can_fetch("*", url) to decide if allowed or not.
        '''
        base_url_string = self.base_url_string
        robot_url = util.robots_url(base_url_string)
        robot_parser = rp.RobotFileParser()
        robot_parser.set_url(robot_url)
        robot_parser.read()
        self.robot_parser = robot_parser

    def decide_next_visit(self, conn, crawl_id, bad_urls):
        '''
        Not abstract.
        Decides which url to visit next.
        Returns a dictionary visit_url with two keys
            visit_url['id'] - database if of the url to visit
            visit_url['url'] - string representation of the url to visit
        Returns None if no urls left to visit.
        Strategy is to visit anything not visited this crawl, with the following priority:
            1) base url
            2) internal pages linked from the base url
            2) articles which haven't been visited yet, sorted by date
        Currently only implemented 1) and 2)
        '''
        base_url_string = self.base_url_string

        # strategy 1 - visit base url if not visited yet (ignore previous crawls)
        base_url_id = queries.insert_url(conn, base_url_string)
        base_url = {'id': base_url_id, 'url': base_url_string}
        visited_base = decide.visited_base_url(conn, crawl_id)
        if not visited_base:
            return base_url
        
        # strategy 2 - visit any urls linked by the base url that haven't been visited yet (ignore previous crawls)
        urls = decide.find_unvisited_links_from_base(conn, crawl_id, base_url_string)
        urls = filter(lambda url: self.robot_parser.can_fetch("*", url['url']), urls)
        urls = filter(lambda url: url['id'] not in bad_urls, urls)
        if len(urls) > 0:
            visit_url = random.choice(urls)
            return visit_url

        # strategy 3 - visit any articles not visited yet (including previous crawls), starting with the most recent
        urls = decide.find_unvisited_internal_urls(conn, base_url_string)
        urls = filter(lambda url: self.robot_parser.can_fetch("*", url['url']), urls)
        urls = filter(lambda url: url['id'] not in bad_urls, urls)
        urls = filter(lambda url: self.is_article(url['url']), urls)
        if len(urls) > 0:
            dates = map(lambda url: self.extract_date_from_url(url['url']), urls)
            reverse_sorted_dates = np.argsort(np.array(dates))[::-1]
            last_date_index = reverse_sorted_dates[0]
            visit_url = urls[last_date_index]
            return visit_url

        return None

    def crawl(self):
        '''
        Not abstract. Begins a crawl.
        Crawls forever, unless:
            - self.decide_next_visit(conn) returns None
            - Five exceptions in a row
        '''
        # initialize variables
        visits = 0
        MAX_VISITS = 1000 # so we don't just keep crawling forever
        bad_urls = set() # when a url doesn't work, add url_id to bad_urls, ignore in future
        error_count = 0
        base_url_string = self.base_url_string
        conn = connect()

        # initialize logging
        initialize_logging(base_url_string)
        start_time = time.time()
        logging.info('STARTING CRAWL AT TIME: {0}'.format(util.time_string(start_time)))

        # initlialize database for this crawl
        base_url_id = queries.insert_url(conn, base_url_string)
        source_id = queries.insert_source(conn, base_url_string)
        crawl_id = queries.insert_crawl(conn, base_url_string)

        while True:
            if error_count == 5:
                logging.error('Too many exceptions in a row, exiting.')
                break
            visit_url = self.decide_next_visit(conn, crawl_id, bad_urls)
            if visit_url is None:
                logging.info('Finished crawling, no more urls to visit.')
                break
            try:
                logging.info('Visiting {}'.format(visit_url['url']))
                self.visit(conn, crawl_id, source_id, visit_url)
                error_count = 0
            except Exception as e:
                logging.error('Error when downloading {0}'.format(visit_url['url']))
                logging.error(traceback.format_exc())
                bad_urls.add(visit_url['id'])
                error_count += 1
            visits += 1
            if visits == MAX_VISITS:
                logging.info('Finished crawling, reached max visits of {}'.format(MAX_VISITS))
                break
            self.sleep()

    def visit(self, conn, crawl_id, source_id, visit_url):
        '''
        Not abstract. Visits a url during a crawl.
        Inserts all relevant information to the database for a single visit.
        Inserts article information if the url matches the article regex.
        '''
        visit_url_id = visit_url['id']
        visit_url_string = visit_url['url']

        base_url_string = self.base_url_string
        html = util.download_html(visit_url_string)
        found_links = util.extract_links(html, base_url_string)
        visit_id = queries.insert_visit(conn, crawl_id, visit_url_id)
        new_url_ids = queries.insert_urls(conn, found_links)
        queries.insert_links(conn, visit_id, new_url_ids)

        if self.is_article(visit_url_string):
            article = util.extract_article(html, visit_url_string)
            article_title = article.title
            article_text = article.text
            article_date = self.extract_date_from_url(visit_url_string)
            queries.insert_article(conn, visit_url_id, article_title, article_text, article_date, source_id)

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
    traceback.print_tb(tb)
    log_str = '''
UNCHECKED EXCEPTION
    Type: {}
    Value: {}
    Traceback: {}'''.format(exctype, value, traceback.print_tb(tb))
    logging.error(log_str)
