import psycopg2

TIME_BETWEEN_REQUESTS = 10

# 5 mins less than 24 hours
MAX_CRAWL_TIME = 60*60*24 - 60*5

DB_USER = 'scott'
DB_PASSWORD = 'BZXa8ksLIGRAKwhmR4p6Eodcl'
DB_DATABASE = 'news'

def connect():
  conn = psycopg2.connect(database=DB_DATABASE, user=DB_USER, password=DB_PASSWORD)
  return conn
