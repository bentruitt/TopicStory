import psycopg2

DB_USER = 'scott'
DB_DATABASE = 'website'

def connect():
    conn = psycopg2.connect(database=DB_DATABASE, user=DB_USER)
    return conn
