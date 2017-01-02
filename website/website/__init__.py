import psycopg2
from flask import Flask, g
app = Flask(__name__)

import website.views
import website.config

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
