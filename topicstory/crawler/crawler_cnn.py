from crawler import Crawler
import time
import datetime
import decide
import re
import numpy as np
import calendar

def crawl():
    base_url_string = 'cnn.com'
    cnn_crawler = CnnCrawler(base_url_string)
    cnn_crawler.crawl()

class CnnCrawler(Crawler):

    def sleep(self):
        time.sleep(1)
    
    def is_article(self, url):
        article_regex = r'cnn.com/[0-9]{4,4}/[0-9]{2,2}/[0-9]{2,2}/'
        return bool(re.search(article_regex, url))

    def extract_date_from_url(self, url):
        date_regex = r'cnn.com/([0-9]{4,4})/([0-9]{2,2})/([0-9]{2,2})/'
        match = re.search(date_regex, url)
        year, month, day = match.groups()
        year, month, day = int(year), int(month), int(day)
        date = datetime.date(year, month, day)
        return date
