import os
import numpy as np
import pandas as pd
import cPickle as pickle
from sklearn.grid_search import GridSearchCV, ParameterGrid
from sklearn.preprocessing import StandardScaler
from sklearn.base import BaseEstimator, clone
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers.core import Dense
from keras.optimizers import Adadelta

def nn_grid_search():
    '''
    Runs a grid search over the data. To change the parameters the of the
    grid search, change the params variable below. Pickles the
    GridSearchCV python object to a file 'grid_search.pkl', pickles the best
    model to 'model.pkl', saves in this file's directory.
    '''
    params = {
            'num_train': [5, 50, 500, 5000, 50000],
            'num_hidden': [10, 30, 100],
            'nb_epoch': [10]
    }

    # up num_train to all data once I get MVP locally
    df = load_data(num_train=5000)
    # get X,y
    X_cols = ['feature_{}'.format(i) for i in range(600)]
    y_col = 'y'
    X = df.loc[:, X_cols].values
    y = df.loc[:,y_col].values
    X_train = X[df['split']=='train']
    y_train = y[df['split']=='train']
    X_dev = X[df['split']=='dev']
    y_dev = y[df['split']=='dev']

    model = NNModel(nb_classes=3)
    grid_search = CustomGridSearch(
            estimator=model,
            param_grid=params
    )
    grid_search.fit(X_train, y_train, X_dev, y_dev)
    return grid_search

    entailment_dir = os.path.dirname(os.path.realpath(__file__))
    grid_search_filename = os.path.join(entailment_dir, 'grid_search.pkl')
    best_model_filename = os.path.join(entailment_dir, 'model.pkl')
    with open(grid_search_filename, 'w') as f:
        pickle.dump(grid_search, f)
    with open(best_model_filename, 'w') as f:
        pickle.dump(grid_search.best_estimator_, f)

def load_data(num_train):
    entailment_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(entailment_dir, 'data')

    train_file = os.path.join(data_dir, 'snli_X_y_train.csv')
    dev_file = os.path.join(data_dir, 'snli_X_y_dev.csv')
    test_file = os.path.join(data_dir, 'snli_X_y_test.csv')

    df_train = pd.read_csv(train_file, encoding='utf-8', nrows=num_train)
    df_dev = pd.read_csv(dev_file, encoding='utf-8')
    df_test = pd.read_csv(test_file, encoding='utf-8')

    # create one dataframe with all the data, (use df['split']=='train'/'dev'/'test' to get split)
    df = pd.concat([df_train, df_dev, df_test], axis=0, ignore_index=True)
    return df

class CustomGridSearch():

    def __init__(self, estimator, param_grid):
        self.estimator = estimator
        self.param_grid = param_grid

    def fit(self, X_train, y_train, X_cv, y_cv):
        search_results = []
        param_sets = ParameterGrid(self.param_grid)
        for params in param_sets:
            print params
            estimator = clone(self.estimator)
            estimator.set_params(**params)
            estimator.fit(X_train, y_train)
            score = estimator.score(X_cv, y_cv)
            params['score'] = score
            params['estimator'] = estimator
            search_results.append(params)
        scores = np.array([result['score'] for result in search_results])
        best_estimator = search_results[scores.argmax()]['estimator']
        self.search_results_ = search_results
        self.best_estimator_ = best_estimator

class NNModel(BaseEstimator):

    def __init__(self, num_train=5000, num_hidden=100, nb_epoch=10, nb_classes=3):
        self.num_train = num_train
        self.num_hidden = num_hidden
        self.nb_epoch = nb_epoch
        self.nb_classes = nb_classes
    
    # def fit(self, X_train, y_train, num_hidden=100, nb_epoch=10):
    def fit(self, X_train, y_train):
        X_train = X_train[:self.num_train]
        y_train = y_train[:self.num_train]
        self.scaler = StandardScaler()
        self.scaler.fit(X_train)
        X_train = self.scaler.transform(X_train)
        y_train_ohe = np_utils.to_categorical(y_train, nb_classes=self.nb_classes)
        model = self.build_model(num_inputs=X_train.shape[1], num_hidden=self.num_hidden)
        model.fit(X_train, y_train_ohe, nb_epoch=self.nb_epoch)
        self.model = model

    def build_model(self, num_inputs, num_hidden):
        layer1 = Dense(
                input_dim=num_inputs,
                output_dim=num_hidden,
                init='uniform',
                activation='tanh'
                )
        layer2 = Dense(
                input_dim=num_hidden,
                output_dim=self.nb_classes,
                init='uniform',
                activation='softmax'
                )
        opt = Adadelta()

        model = Sequential() # sequence of layers
        model.add(layer1)
        model.add(layer2)
        model.compile(loss='categorical_crossentropy', optimizer=opt)
        return model

    def predict(self, X_test):
        X_test = self.scaler.transform(X_test)
        return self.model.predict_classes(X_test)

    def score(self, X_test, y_test):
        y_pred = self.predict(X_test)
        acc = np.mean(y_test == y_pred)
        return acc
