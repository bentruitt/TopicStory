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
        self.tfidf_model = None
        self.tfidf = None
        self.topic_model = None
        self.topics = None

    def fit(self, documents):
        '''
        Cleans the documents, creates a tf-idf matrix, and fits NMF.
        Stores all the resulting models as instance variables.
        '''
        # documents = [self.clean_document(doc) for doc in documents]
        print 'loading spacy'
        nlp = spacy.load('en')
        print 'cleaning documents'
        docs = []
        for i,doc in enumerate(documents):
            print i
            clean_doc = self.clean_document(doc, nlp)
            docs.append(clean_doc)
        print 'deleting spacy'
        del nlp
        documents = docs

        print 'creating tfidf matrix'
        tfidf_model = TfidfVectorizer(max_features=5000)
        tfidf_model.fit(documents)
        tfidf = tfidf_model.transform(documents)
        vocab = tfidf_model.get_feature_names()

        print 'fitting topics'
        topic_model = NMF(n_components=self.num_topics)
        topic_model.fit(tfidf)
        topics = topic_model.transform(tfidf)
        components = topic_model.components_

        # reorder most common topics first
        assigned_topics = topics.argmax(axis=1)
        topic_inds, topic_counts = np.unique(assigned_topics, return_counts=True)
        new_topic_order = topic_inds[topic_counts.argsort()][::-1]
        missing_topics = set(range(self.num_topics)) - set(new_topic_order)
        new_topic_order = np.array(list(new_topic_order) + list(missing_topics))

        topics = topics[:,new_topic_order]
        components = components[new_topic_order,:]

        self.tfidf = tfidf
        self.vocab = vocab
        self.topics = topics
        self.components = components

    def get_topic_words(self, topic, num_words=10):
        '''
        Input:
            topic - int, the number label of the topic
            num_words - int, the number of words to return for this topic
        Output:
            List of strings - the top words in this topic
        '''
        vocab = self.vocab
        components = self.components
        print topic
        topic_word_inds = components.argsort(axis=1)[topic,::-1]
        topic_words = [vocab[i] for i in topic_word_inds[:num_words]]
        return topic_words

    def clean_document(self, document, nlp):
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
        document = document.decode('utf-8', 'ignore')
        document = filter(lambda c: c in string.whitespace + string.letters, document)
        document = document.lower()

        parsed = nlp(document)
        lemmas = [word.lemma_ for word in parsed]
        document = ' '.join(lemmas)

        words = document.split()
        words = filter(lambda w: str(w) not in ENGLISH_STOP_WORDS, words)
        words = filter(lambda w: w != u'', words)
        document = ' '.join(words)
        return document

    # def clean_document(self, document):
    #     '''
    #     Input: String
    #     Output: String
    # 
    #     Cleans the input document. Includes:
    #         -> converts to unicode
    #         -> lowercase
    #         -> remove non-letters
    #         -> remove stop words
    #         -> stemming
    #     '''
    #     document = document.decode('utf-8', 'ignore')
    #     document = filter(lambda c: c in string.whitespace + string.letters, document)
    #     document = document.lower()
    #     words = document.split()
    #     words = filter(lambda w: str(w) not in ENGLISH_STOP_WORDS, words)
    #     words = filter(lambda w: w != u'', words)
    #     document = ' '.join(words)
    #     return document
