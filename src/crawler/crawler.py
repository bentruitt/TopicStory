import time
import threading
import logging
import traceback
import datetime
import os

import score as s
import util
import models
from config import MAX_CRAWL_TIME, TIME_BETWEEN_REQUESTS
from conn import connect

def crawl(base_url_string):
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
    score = s.Score(base_url, conn)

    while (time.time() - start_time < MAX_CRAWL_TIME):
        visit_url = score.decide_next_visit()
        logging.info('VISIT: {0}, {1}'.format(util.time_string(time.time()), visit_url['url']))

        try:
            html_text = util.download_html(visit_url['url'])
        except Exception as e:
            logging.error('Error when downloading {0}'.format(visit_url['url']))
            logging.error(traceback.format_exc())
            raise

        found_links = util.extract_links(html_text, base_url['url'])
        article = util.extract_article(html_text, base_url['url'])

        found_urls = urls.insert_many(found_links)
        robots.insert_many(found_urls)
        visit = visits.insert(visit_url)
        links.insert_many(visit, found_urls)
        articles.insert(visit_url, article, source)

        time.sleep(TIME_BETWEEN_REQUESTS)

def initialize_logging(base_url):
    log_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    source_str = util.extract_source(base_url)
    log_filename = 'LOG_{0}.log'.format(source_str)
    log_path = os.path.join(log_dir, log_filename)
    logging.basicConfig(filename=log_path, filemode='a', level=logging.INFO)
