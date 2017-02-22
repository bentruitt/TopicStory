import os
import datetime
import itertools
import cPickle as pickle
import numpy as np
from conn import connect
from analysis.nlp import lookup_vectors_by_date, lookup_article_info
import nn_model

def find_disagreements(conn, publish_date):
    entailment_dir = os.path.dirname(os.path.realpath(__file__))
    model_filename = os.path.join(entailment_dir, 'model.pkl')
    with open(model_filename, 'r') as f:
        model = pickle.load(f)
    from_table = 'spacy_title_vectors'
    from_field = 'spacy_title_vector'
    url_ids, vectors = lookup_vectors_by_date(conn, from_table, from_field, publish_date)
    disagreements = []
    for (url1, v1), (url2, v2) in itertools.combinations(zip(url_ids, vectors), 2):
        X = np.hstack((v1,v2))[np.newaxis,:]
        result = model.predict(X)
        if result == 0:
            disagreements.append( (url1, url2) )
    article_infos = [(lookup_article_info(conn, url1), lookup_article_info(conn, url2)) for (url1, url2) in disagreements]
    return article_infos
