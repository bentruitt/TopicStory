import cPickle as pickle
import os
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
    model = getattr(g, '_model', None)
    if model is None:
        website_dir = os.path.dirname(os.path.realpath(__file__))
        model_filename = os.path.join(website_dir, '..', 'analysis', 'model.pkl')
        with open(model_filename, 'r') as f:
            model = pickle.load(f)
        g._model = model
    return model

@app.teardown_appcontext
def close_db(error):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
