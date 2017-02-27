from crawler import Crawler
import time
import datetime
import decide
import re
import numpy as np
import calendar

def crawl():
    base_url_string = 'theguardian.com'
    theguardian_crawler = TheGuardianCrawler(base_url_string)
    theguardian_crawler.crawl()

class TheGuardianCrawler(Crawler):

    def sleep(self):
        time.sleep(1)
    
    def is_article(self, url):
        if re.search(r'/all$', url):
            return False
        if re.search(r'/altdate$', url):
            return False
        article_regex = r'(?<!/live)(?<!/video)/[0-9]{4,4}/[a-z]{3,3}/[0-9]{1,2}' # this one was annoying to get rid of videos/lives
        return bool(re.search(article_regex, url))

    def extract_date_from_url(self, url):
        date_regex = r'(?<!/live)(?<!/video)/([0-9]{4,4})/([a-z]{3,3})/([0-9]{1,2})'
        month_abbr2int = {v.lower(): k for k,v in enumerate(calendar.month_abbr)}
        match = re.search(date_regex, url)
        year, month, day = match.groups()
        year, month, day = int(year), month_abbr2int[month], int(day)
        date = datetime.date(year, month, day)
        return date
