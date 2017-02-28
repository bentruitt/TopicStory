import pandas as pd
import numpy as np
import string
import matplotlib.pyplot as plt
import nltk
import re
import spacy
import gc
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics import silhouette_score
from nltk.stem.snowball import EnglishStemmer

plt.style.use('fivethirtyeight')

class LdaPipeline:
    '''
    Class for running LDA on a group of text documents.
    The pipeline consists of three main steps:
        -> cleaning each document
        -> turning each document into tf-idf matrix
        -> running the tf-idf matrix through LDA
    Also includes helper functions for finding words
    associated with each topic and making plots.
    '''

    def __init__(self, num_topics=100, method='batch'):
        self.num_topics = num_topics
        self.method = method
        self.documents = None
        self.tfidf_model = None
        self.tfidf = None
        self.lda_model = None
        self.lda = None

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
        self.lda_model = other.lda_model
        self.lda = other.lda

    def fit(self, documents):
        '''
        Cleans the documents, creates a tf-idf matrix, and fits LDA.
        Stores all the resulting models as instance variables.
        '''
        print 'cleaning documents'
        gc.collect()
        #nlp = spacy.load('en')
        documents = [self.clean_document(doc) for doc in documents]
        # nlp takes up a lot of memory, delete once we're done with it
        gc.collect()

        print 'creating tfidf matrix'
        tfidf_model = TfidfVectorizer(max_features=5000)
        tfidf_model.fit(documents)
        tfidf = tfidf_model.transform(documents)

        print 'fitting lda'
        lda_model = LatentDirichletAllocation(n_topics=self.num_topics, learning_method=self.method)
        lda_model.fit(tfidf)
        lda = lda_model.transform(tfidf)

        self.documents = documents
        self.tfidf_model = tfidf_model
        self.tfidf = tfidf
        self.lda_model = lda_model
        self.lda = lda

        self.compute_top_topics()
        self.compute_silhouette_score()

    def predict(self, documents):
        gc.collect()
        #nlp = spacy.load('en')
        documents = [self.clean_document(doc) for doc in documents]
        # nlp takes up a lot of memory, delete once we're done with it
        gc.collect()

        tfidf = self.tfidf_model.transform(documents)
        lda = self.lda_model.transform(tfidf)
        return lda

    def get_topic_words(self, topic, num_words=10):
        '''
        Input:
            topic - int, the number label of the topic
            num_words - int, the number of words to return for this topic
        Output:
            List of strings - the top words in this topic
        '''
        vocab = self.tfidf_model.get_feature_names()
        components = self.lda_model.components_
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
        self.top_topics = self.lda.argmax(axis=1)

    def compute_silhouette_score(self):
        '''
        Input: None
        Output: None

        Computes the silhouette score, stores the result as a float.
        Uses tfidf vectors as the features, and cosine distance as the metric.
        '''
        self.silhouette_score = silhouette_score(X=self.tfidf, labels=self.top_topics, metric='cosine')
    
    def compute_empty_topics(self, documents):
        lda = self.predict(documents)
        topics = lda.argmax(axis=1)
        topic_counts = np.array([sum(topics==i) for i in range(self.num_topics)])
        num_zero = np.count_nonzero(topic_counts==0)
        return num_zero

    def plot_prevalent_topics_by_avg(self, documents, num_plot_topics=10, num_words=7, title=''):
        '''
        Input: group element from groupby, int, int
        Output: None

        Plots the most prevalent topics for a given set of documents.
        Uses average over the document's lda vectors.
        '''
        num_topics = self.num_topics
        lda_pred = self.predict(documents)

        avg_topics = self.lda.mean(axis=0)
        topic_prevalences = lda_pred.mean(axis=0) / avg_topics
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
        lda_pred = self.predict(documents)
        topics = lda_pred.argmax(axis=1)
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
        score = self.lda_model.score(X)
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

# use TDD
if __name__ == '__main__':
    # df = load_data()
    lda = LdaPipeline(num_topics=20)
    lda.fit(df['content'].values)

    # use these when running 'run -i lda.py' from ipython to avoid rerunning script each time
    # lda_copy = LdaPipeline()
    # lda_copy.clone(lda)
    # lda = lda_copy

    lda.groupby(df['pub_date'])
    lda.plot_prevalent_topics(sorted(df['pub_date'].unique())[-1], num_plot_topics=7, num_words=5)
    plt.tight_layout()
    plt.savefig('lda_batch_20.png')
    plt.show()
