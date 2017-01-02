import argparse

import crawler

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Interact with the crawler database')
  parser.add_argument('--crawl', help='spawn a continuous crawler for a given base url', nargs=1)
  args = parser.parse_args()

  if args.crawl:
    base_url = args.crawl[0]
    crawler.crawl(base_url)
