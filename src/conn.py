import psycopg2

DB_USER = 'scott'
DB_PASSWORD = 'BZXa8ksLIGRAKwhmR4p6Eodcl'
DB_DATABASE = 'news'

def connect():
  conn = psycopg2.connect(database=DB_DATABASE, user=DB_USER, password=DB_PASSWORD)
  return conn
