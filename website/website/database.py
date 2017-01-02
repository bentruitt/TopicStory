from website import app
from flask import g
from config import connect

def get_db():
  db = getattr(g, '_database', None)
  if db is None:
    db = connect()
    g._database = db
  return db

@app.teardown_appcontext
def close_db(error):
  db = getattr(g, '_database', None)
  if db is not None:
    db.close()
