import numpy as np
from sklearn.base import BaseEstimator
from sklearn.preprocessing import StandardScaler
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers.core import Dense
from keras.optimizers import Adadelta

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
