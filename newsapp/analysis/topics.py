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
    Allows for both LDA and NMF.
    The pipeline consists of three main steps:
        -> cleaning each document
        -> turning each document into tf-idf matrix
        -> running the tf-idf matrix through LDA
    Also includes helper functions for finding words
    associated with each topic and making plots.
    '''

    def __init__(self, num_topics=100, method='lda'):
        '''
        method can either be 'lda' or 'nmf'.
        '''
        self.num_topics = num_topics
        self.method = method
        self.documents = None
        self.tfidf_model = None
        self.tfidf = None
        self.topic_model = None
        self.topics = None

    def clone(self, other):
        '''
        Clones most of the instance variables from another instance of this class.
        Useful during development if running fit() takes a long time, and want to
        develop other instance functions while using ipython.
        '''
        self.num_topics = other.num_topics
        self.method = other.method
        self.documents = other.documents
        self.tfidf_model = other.tfidf_model
        self.tfidf = other.tfidf
        self.topic_model = other.topic_model
        self.topics = other.topics

    def fit(self, documents):
        '''
        Cleans the documents, creates a tf-idf matrix, and fits LDA.
        Stores all the resulting models as instance variables.
        '''
        print 'cleaning documents'
        documents = [self.clean_document(doc) for doc in documents]

        print 'creating tfidf matrix'
        tfidf_model = TfidfVectorizer(max_features=5000)
        tfidf_model.fit(documents)
        tfidf = tfidf_model.transform(documents)

        print 'fitting topics'
        if self.method=='lda':
            topic_model = LatentDirichletAllocation(n_topics=self.num_topics)
        elif self.method=='nmf':
            topic_model = NMF(n_components=self.num_topics)
        else:
            raise ValueError("method must either be 'nmf' or 'lda'")
        topic_model.fit(tfidf)
        topics = topic_model.transform(tfidf)

        self.documents = documents
        self.tfidf_model = tfidf_model
        self.tfidf = tfidf
        self.topic_model = topic_model
        self.topics = topics

    def predict(self, documents):
        documents = [self.clean_document(doc) for doc in documents]
        tfidf = self.tfidf_model.transform(documents)
        topics = self.topic_model.transform(tfidf)
        return topics

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

    def compute_top_topics(self):
        '''
        Input: None
        Output: None

        Finds the top topic associated with each document.
        Stores the result as a 1D numpy array,
        where each element is a document and each value is the topic number.
        '''
        self.top_topics = self.topics.argmax(axis=1)

    def compute_silhouette_score(self):
        '''
        Input: None
        Output: None

        Computes the silhouette score, stores the result as a float.
        Uses tfidf vectors as the features, and cosine distance as the metric.
        '''
        self.silhouette_score = silhouette_score(X=self.tfidf, labels=self.top_topics, metric='cosine')
    
    def compute_empty_topics(self, documents):
        topics = self.predict(documents)
        topics = topics.argmax(axis=1)
        topic_counts = np.array([sum(topics==i) for i in range(self.num_topics)])
        num_zero = np.count_nonzero(topic_counts==0)
        return num_zero

    def count_topic(self, documents, topic):
        '''
        Input:
            documents - list of strings
            topic - integer
        Output:
            topic_count - integer
        Counts the number of strings in documents which belong to topic number topic.
        '''
        topics = self.predict(documents)
        topics = topics.argmax(axis=1)
        topic_count = sum(topics==topic)
        return topic_count

    def get_prevalent_topics(self, documents, num_topics, num_words):
        '''
        Input:
            documents - list of strings
            num_topics - number of topics to return
            num_words - number of words to put in topic names
        Output:
            topic_names - list of strings
            topic_counts - list of integers (number of articles for each topic)
        '''
        total_topics = self.num_topics
        topics = self.predict(documents)
        topics = topics.argmax(axis=1)
        topic_counts = np.array([sum(topics==i) for i in range(num_topics)])
        top_topics = topic_counts.argsort()[:-(num_topics+1):-1]
        topic_names = [' '.join(self.get_topic_words(topic, num_words)) for topic in top_topics]
        topic_counts = topic_counts[top_topics]
        return topic_names, topic_counts

    def plot_prevalent_topics_by_avg(self, documents, num_plot_topics=10, num_words=7, title=''):
        '''
        Input: group element from groupby, int, int
        Output: None

        Plots the most prevalent topics for a given set of documents.
        Uses average over the document's lda vectors.
        '''
        num_topics = self.num_topics
        topics = self.predict(documents)

        avg_topics = self.topics.mean(axis=0)
        topic_prevalences = topics.mean(axis=0) / avg_topics
        top_topics = topic_prevalences.argsort()[(num_topics-num_plot_topics):]
        topic_names = [' '.join(self.get_topic_words(topic, num_words)) for topic in top_topics]

        ind = np.arange(num_plot_topics)-0.5
        fig = plt.figure(figsize=(10,6))
        ax = fig.add_subplot(111)
        ax.barh(ind, topic_prevalences[top_topics])
        ax.set_yticks(np.arange(len(topic_names)))
        ax.set_yticklabels(topic_names)
        ax.set_title(title)

    def plot_prevalent_topics_by_count(self, documents, num_plot_topics=10, num_words=7, title=''):
        '''
        Input: group element from groupby, int, int
        Output: None

        Plots the most prevalent topics for a given set of documents.
        Counts how many articles are in each topic, orders from most to least.
        '''
        num_topics = self.num_topics
        topics = self.predict(documents)
        topics = topics.argmax(axis=1)
        topic_counts = np.array([sum(topics==i) for i in range(num_topics)])

        top_topics = topic_counts.argsort()[(num_topics-num_plot_topics):]
        topic_names = [' '.join(self.get_topic_words(topic, num_words)) for topic in top_topics]

        ind = np.arange(num_plot_topics)
        fig = plt.figure(figsize=(10,6))
        ax = fig.add_subplot(111)
        ax.barh(ind, topic_counts[top_topics])
        ax.set_yticks(np.arange(len(topic_names)))
        ax.set_yticklabels(topic_names)
        ax.set_title(title)

    def score(self, docs):
        '''
        Returns the log-likelihood score for a series of documents.
        '''
        docs = [self.clean_document(doc) for doc in docs]
        X = self.tfidf_model.transform(docs)
        score = self.topic_model.score(X)
        return score


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
