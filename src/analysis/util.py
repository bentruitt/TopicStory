from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from nltk.stem.snowball import EnglishStemmer
import string

def clean_docs(docs):
    '''
    INPUT:
        docs: List of strings
    OUTPUT:
        docs: List of strings
    Cleans a set of input documents as raw strings,
    returns a list of words for each doc.
    Does the following:
        - converts to utf-8
        - splits words on any whitespace
        - lowercase each word
        - removes non-letters from each word
        - applies stemming
        - removes words from sklearns's ENGLISH_STOP_WORDS
        - filters any remaining empty words
        - converts list of words back to a string
    '''
    docs = [doc.encode('utf-8', 'ignore') for doc in docs]
    docs = [doc.split() for doc in docs]
    docs = [[word.lower() for word in doc] for doc in docs]
    docs = [[filter(lambda c: c in string.letters, word) for word in doc] for doc in docs]
    es = EnglishStemmer()
    docs = [filter(lambda w: w not in ENGLISH_STOP_WORDS,doc) for doc in docs]
    docs = [[es.stem(word) for word in doc] for doc in docs]
    docs = [filter(lambda w: w != '',doc) for doc in docs]
    docs = [string.join(doc, ' ') for doc in docs]
    return docs
