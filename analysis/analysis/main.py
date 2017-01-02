import psycopg2
import argparse
import re
import itertools

from cosine import calculate_similarities
import labels
import cosine

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Interact with the crawler database')
  parser.add_argument('--label', help='create labels for all the built-in news sources', action='store_true')
  parser.add_argument('--cosine', help='create cosine similarities for all pairs of articles', action='store_true')
  args = parser.parse_args()

  if args.label:
    labels.add_labels()

  elif args.cosine:
    cosine.calculate_cosine_similarities()
