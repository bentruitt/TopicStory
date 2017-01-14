import argparse

import crawler.crawler as crawler
import analysis.labels as labels
import analysis.cosine as cosine
import website.test_server as test_server

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Interact with the crawler database')
    parser.add_argument('--crawl', help='spawn a continuous crawler for a given base url', nargs=1)
    parser.add_argument('--label', help='create labels for all the built-in news sources', action='store_true')
    parser.add_argument('--cosine', help='create cosine similarities for all pairs of articles', action='store_true')
    parser.add_argument('--test-server', help='run a local test server', action='store_true')
    parser.add_argument('--deploy-server', help='deploy the actual server', action='store_true')
    args = parser.parse_args()

    if args.crawl:
        base_url = args.crawl[0]
        crawler.crawl(base_url)

    elif args.label:
        labels.add_labels()

    elif args.cosine:
        cosine.calculate_cosine_similarities()

    elif args.test_server:
        test_server.run()
