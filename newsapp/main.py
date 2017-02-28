import argparse
import datetime

import crawler.crawler_foxnews as crawler_foxnews
import crawler.crawler_nytimes as crawler_nytimes
import crawler.crawler_theguardian as crawler_theguardian
import crawler.crawler_npr as crawler_npr
import crawler.crawler_cnn as crawler_cnn
import website.test_server as test_server
import website.deploy_server as deploy_server

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Interact with the crawler database')
    parser.add_argument('--crawl-foxnews', help='spawn a continuous crawler for foxnews', action='store_true')
    parser.add_argument('--crawl-nytimes', help='spawn a continuous crawler for the new york times', action='store_true')
    parser.add_argument('--crawl-theguardian', help='spawn a continuous crawler for The Guardian', action='store_true')
    parser.add_argument('--crawl-npr', help='spawn a continuous crawler for NPR', action='store_true')
    parser.add_argument('--crawl-cnn', help='spawn a continuous crawler for CNN', action='store_true')

    parser.add_argument('--test-server', help='run a local test server', action='store_true')
    parser.add_argument('--deploy-server', help='deploy the actual server', action='store_true')
    args = parser.parse_args()

    if args.crawl_foxnews:
        crawler_foxnews.crawl()

    elif args.crawl_nytimes:
        crawler_nytimes.crawl()

    elif args.crawl_theguardian:
        crawler_theguardian.crawl()

    elif args.crawl_npr:
        crawler_npr.crawl()

    elif args.crawl_cnn:
        crawler_cnn.crawl()

    elif args.test_server:
        test_server.run()

    elif args.deploy_server:
        deploy_server.run()
