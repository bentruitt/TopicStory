from crawler import Crawler
import time
import datetime
import decide
import re
import numpy as np

def crawl():
    foxnews_crawler = FoxNewsCrawler()
    foxnews_crawler.crawl()

class FoxNewsCrawler(Crawler):

    def __init__(self):
        self.base_url_string = 'foxnews.com'
        self.article_regex = r'/[0-9]{4,4}/[0-9]{1,2}/[0-9]{1,2}/'

    def sleep(self):
        time.sleep(1)

    def decide_next_visit(self, conn):
        urls = decide.find_internal_urls(conn, self.base_url_string)
        urls = filter(lambda url: decide.allowed_by_robots(conn, url['id']), urls)
        urls = filter(lambda url: not decide.visited(conn, url['id']), urls)
        urls = filter(lambda url: self.is_article(url['url']), urls)
        dates = map(lambda url: self.extract_date_from_url(url['url']), urls)
        reverse_sorted_dates = np.argsort(np.array(dates))[::-1]
        last_date_index = reverse_sorted_dates[0]
        visit_url = urls[last_date_index]
        return visit_url
    
    def extract_date_from_url(self, url):
        date_regex = r'/([0-9]{4,4})/([0-9]{1,2})/([0-9]{1,2})/'
        match = re.search(date_regex, url)
        year, month, day = match.groups()
        year, month, day = int(year), int(month), int(day)
        date = datetime.date(year, month, day)
        return date
