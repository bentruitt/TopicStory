import argparse
import datetime

import crawler.crawler_foxnews as crawler_foxnews
import crawler.crawler_nytimes as crawler_nytimes
import crawler.crawler_theguardian as crawler_theguardian
import crawler.crawler_npr as crawler_npr
import crawler.crawler_cnn as crawler_cnn
import analysis.labels as labels
import analysis.cosine as cosine
import analysis.clustering as clustering
import analysis.nlp as nlp
import analysis.entailment.train_nn as train_nn
import analysis.entailment.predict_news_entailment as predict_news_entailment
import website.test_server as test_server
import website.deploy_server as deploy_server

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Interact with the crawler database')
    parser.add_argument('--crawl-foxnews', help='spawn a continuous crawler for foxnews', action='store_true')
    parser.add_argument('--crawl-nytimes', help='spawn a continuous crawler for the new york times', action='store_true')
    parser.add_argument('--crawl-theguardian', help='spawn a continuous crawler for The Guardian', action='store_true')
    parser.add_argument('--crawl-npr', help='spawn a continuous crawler for NPR', action='store_true')
    parser.add_argument('--crawl-cnn', help='spawn a continuous crawler for CNN', action='store_true')

    parser.add_argument('--label', help='create labels for all the built-in news sources', action='store_true')
    parser.add_argument('--cosine', help='create cosine similarities for all pairs of articles', action='store_true')
    parser.add_argument('--cluster', help='cluster articles for a given date, input as yyyy-mm-dd', nargs=1)
    parser.add_argument('--thresh', help='if using --cluster, use --tresh to change the clustering threshold (defaults to 0.7)', nargs=1)
    parser.add_argument('--spacy-title-vectors', help='compute and store spacy vectors for every title in the database', action='store_true')
    parser.add_argument('--spacy-text-vectors', help='compute and store spacy vectors for every text in the database', action='store_true')
    parser.add_argument('--nn-grid-search', help='train the neural network over a grid search, pickles the result', action='store_true')
    parser.add_argument('--predict-news-entailment', help='predict entailment pairs for news articles', action='store_true')

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

    elif args.label:
        labels.add_labels()

    elif args.cosine:
        cosine.calculate_cosine_similarities()

    elif args.cluster:
        date = args.cluster[0]
        date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        if args.thresh:
            thresh = args.thresh[0]
        else:
            thresh = 0.7
        clustering.cluster_date(date, thresh=thresh)

    elif args.spacy_title_vectors:
        nlp.compute_spacy_title_vectors()

    elif args.spacy_text_vectors:
        nlp.compute_spacy_text_vectors()

    elif args.nn_grid_search:
        train_nn.nn_grid_search()

    elif args.predict_news_entailment:
        predict_news_entailment.predict_entailment_by_date()

    elif args.test_server:
        test_server.run()

    elif args.deploy_server:
        deploy_server.run()
