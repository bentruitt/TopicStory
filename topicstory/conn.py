import psycopg2
import json
import os

def connect():
    curr_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(curr_path, 'config.json')
    
    with open(config_path) as f:
        config = json.load(f)
    
    user = config['NEWS_DB_USER']
    password = config['NEWS_DB_PASSWORD']
    database = config['NEWS_DB_DATABASE']
    host = config['NEWS_DB_HOST']

    conn = psycopg2.connect(user=user, password=password, database=database, host=host)
    return conn
