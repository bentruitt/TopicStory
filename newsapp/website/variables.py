import cPickle as pickle
import os
import glob
import datetime
import re
import numpy as np
from website import app
from flask import g
from conn import connect

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = connect()
        g._database = db
    return db

def get_model():
    website_dir = os.path.dirname(os.path.realpath(__file__))
    models_dir = os.path.join(website_dir, '..', 'analysis', 'models')
    model_filenames = os.listdir(models_dir)
    end_dates = [extract_end_date(m) for m in model_filenames]
    end_dates = filter(lambda d: d is not None, end_dates)
    end_dates = np.array(end_dates)
    latest_model_ind = end_dates.argmax()
    latest_model_filename = model_filenames[latest_model_ind]
    model_name = '_{}'.format(latest_model_filename)
    model = getattr(g, model_name, None)
    if model is None:
        filepath = os.path.join(models_dir, latest_model_filename)
        with open(filepath, 'r') as f:
            model = pickle.load(f)
        setattr(g, model_name, model)
    return model

def extract_end_date(model_filename):
    m = re.match(r'model_([0-9]{4,4}-[0-9]{2,2}-[0-9]{2,2})_([0-9]{4,4}-[0-9]{2,2}-[0-9]{2,2})_([0-9]*)\.pkl', model_filename)
    if m:
        end_date = m.groups()[1]
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        return end_date
    return None

@app.teardown_appcontext
def close_db(error):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
