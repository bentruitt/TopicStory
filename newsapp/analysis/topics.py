import pandas as pd
import numpy as np
import string
import matplotlib.pyplot as plt
import nltk
import re
import spacy
import gc
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.decomposition import LatentDirichletAllocation, NMF
from sklearn.metrics import silhouette_score
from nltk.stem.snowball import EnglishStemmer

plt.style.use('ggplot')

class TopicPipeline:
    '''
    Class for running a topic modeling pipeline.
    The pipeline consists of three main steps:
        -> cleaning each document
        -> turning each document into tf-idf matrix
        -> running the tf-idf matrix through NMF
    Also includes helper functions for finding words
    associated with each topic and making plots.
    '''

    def __init__(self, num_topics=100):
        self.num_topics = num_topics
        self.documents = None
        self.tfidf_model = None
        self.tfidf = None
        self.topic_model = None
        self.topics = None

    def fit(self, documents):
        '''
        Cleans the documents, creates a tf-idf matrix, and fits NMF.
        Stores all the resulting models as instance variables.
        '''
        print 'cleaning documents'
        documents = [self.clean_document(doc) for doc in documents]

        print 'creating tfidf matrix'
        tfidf_model = TfidfVectorizer(max_features=5000)
        tfidf_model.fit(documents)
        tfidf = tfidf_model.transform(documents)

        print 'fitting topics'
        topic_model = NMF(n_components=self.num_topics)
        topic_model.fit(tfidf)
        topics = topic_model.transform(tfidf)

        self.documents = documents
        self.tfidf_model = tfidf_model
        self.tfidf = tfidf
        self.topic_model = topic_model
        self.topics = topics

    def get_topic_words(self, topic, num_words=10):
        '''
        Input:
            topic - int, the number label of the topic
            num_words - int, the number of words to return for this topic
        Output:
            List of strings - the top words in this topic
        '''
        vocab = self.tfidf_model.get_feature_names()
        components = self.topic_model.components_
        topic_word_inds = components.argsort(axis=1)[topic,::-1]
        topic_words = [vocab[i] for i in topic_word_inds[:num_words]]
        return topic_words

    def clean_document(self, document):
        '''
        Input: String
        Output: String
    
        Cleans the input document. Includes:
            -> converts to unicode
            -> lowercase
            -> remove non-letters
            -> remove stop words
            -> stemming
        '''
        # convert to unicode
        document = document.decode('utf-8', 'ignore')
        # remove non-letters
        document = filter(lambda c: c in string.whitespace + string.letters, document)
        # lowercase
        document = document.lower()
        # remove stop words
        words = document.split()
        words = filter(lambda w: w not in ENGLISH_STOP_WORDS, words)
        # # run spacy
        # words = nlp(document)
        # # remove non-nouns
        # words = filter(lambda word: word.pos_ not in ['NOUN', 'PROPN'], words)
        # # get lemma
        # words = [word.lemma_ for word in words]
        # combine words back into a document
        words = filter(lambda w: w != u'', words)
        document = ' '.join(words)
        return document
