import re

# import models.urls
# import models.article_labels
from config import ARTICLE_URL_REGEXPS
from conn import connect
import models

def add_labels():
    conn = connect()

    # urls = models.urls.Urls(conn)
    # article_labels = models.article_labels.ArticleLabels(conn)
    urls = models.Urls(conn)
    article_labels = models.ArticleLabels(conn)
    for base_url, regexp in ARTICLE_URL_REGEXPS:
        source_urls = urls.internal_urls(base_url)
        # labels = [bool(re.search(regexp,u.url)) for u in source_urls]
        labels = [bool(re.search(regexp,u['url'])) for u in source_urls]
        article_labels.insert_many(source_urls,labels)

    conn.close()
