import psycopg2

TIME_BETWEEN_REQUESTS = 10

# 5 mins less than 24 hours
MAX_CRAWL_TIME = 60*60*24 - 60*5
