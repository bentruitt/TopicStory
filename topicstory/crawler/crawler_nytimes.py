from crawler import Crawler
import time
import datetime
import decide
import re
import numpy as np

def crawl():
    base_url_string = 'nytimes.com'
    nytimes_crawler = NytimesCrawler(base_url_string)
    nytimes_crawler.crawl()

class NytimesCrawler(Crawler):

    def sleep(self):
        # start with 10
        time.sleep(1)
    
    def is_article(self, url):
        article_regex = r'nytimes.com/[0-9]{4,4}/[0-9]{1,2}/[0-9]{1,2}/'
        return bool(re.search(article_regex, url))

    def extract_date_from_url(self, url):
        date_regex = r'/([0-9]{4,4})/([0-9]{1,2})/([0-9]{1,2})/'
        match = re.search(date_regex, url)
        year, month, day = match.groups()
        year, month, day = int(year), int(month), int(day)
        date = datetime.date(year, month, day)
        return date
