# -*- coding: utf-8 -*-
"""Tsunami_Prediction_Model_REGION_CODE_NN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YNEWuM3HFM4aDqb1Y5E8379MbIvx7Lw8
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mp
from sklearn.preprocessing import StandardScaler
import sklearn as sk
from sklearn.decomposition import PCA

from google.colab import files
uploaded=files.upload()

import io
su=pd.read_csv(io.BytesIO(uploaded['sources.csv']))

from google.colab import files
uploaded=files.upload()

su1=pd.read_csv(io.BytesIO(uploaded['waves.csv']))

su=pd.concat([su,su1],axis=1)

from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
su.iloc[:,0] = le.fit_transform(su.iloc[:,0]).astype('float64')

corr = su.corr()
import seaborn as sns
sns.heatmap(corr)

su.fillna(0,inplace=True)
su=su.drop(['COUNTRY','LOCATION','STATE/PROVINCE','FIRST_MOTION'],axis=1)
tsu=su.drop(['VALIDITY'],axis=1)

su = su.loc[:,~su.columns.duplicated()]
su.dtypes

#Data preprocessing
from sklearn.model_selection import train_test_split
X=su.iloc[:,:-1]
y=su['REGION_CODE']
scale=StandardScaler()
Xn=scale.fit_transform(X)
pca=PCA(n_components=10)
Xs=pca.fit_transform(Xn)
X_train, X_test, y_train, y_test = train_test_split(Xs, y, test_size = 0.33, random_state=42)

#decisiontree classification
from sklearn.tree import DecisionTreeClassifier
loanTree = DecisionTreeClassifier(criterion="entropy", max_depth = 4)
loanTree.fit(X_train,y_train)
print("Accuracy",loanTree.score(X_test, y_test))

#classification report
y_predicted=loanTree.predict(X_test)
from sklearn.metrics import classification_report
print(classification_report(y_test,y_predicted))

from sklearn.metrics import confusion_matrix
results = confusion_matrix(y_test, y_predicted)
print(results)

#ANN implementation
import random
from keras.models import Sequential
from numpy.random import seed
from tensorflow import set_random_seed
def create_model(lyrs=[8], act='linear', opt='Adam', dr=0.0):
    seed(42)
    set_random_seed(42)
   
    model = Sequential()
    
    # create first hidden layer
    model.add(Dense(lyrs[0], input_dim=X_train.shape[1], activation=act))
    
    # create additional hidden layers
    for i in range(1,len(lyrs)):
        model.add(Dense(lyrs[i], activation=act))
    
    # add dropout, default is none
    model.add(Dense(1, activation='sigmoid'))
    
    model.compile(loss='binary_crossentropy', optimizer=opt, metrics=['accuracy'])
    
    return model

from keras.layers import Activation, Dense
model = create_model()
print(model.summary())

training = model.fit(X_train, y_train, epochs=100, batch_size=32, validation_split=0.2, verbose=0)

val_acc = np.mean(training.history['val_acc'])
print("\n%s: %.2f%%" % ('val_acc', val_acc*100))

plt.plot(training.history['acc'])
plt.plot(training.history['val_acc'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'validation'], loc='upper left')
plt.show()

from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import GridSearchCV
model = KerasClassifier(build_fn=create_model, verbose=0)
batch_size = [32,64]
epochs = [50]
param_grid = dict(batch_size=batch_size, epochs=epochs)

# search the grid
grid = GridSearchCV(estimator=model, 
                    param_grid=param_grid,
                    cv=3,
                    verbose=2)  # include n_jobs=-1 if you are using CPU

grid_result = grid.fit(X_train, y_train)

print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
means = grid_result.cv_results_['mean_test_score']
stds = grid_result.cv_results_['std_test_score']
params = grid_result.cv_results_['params']
for mean, stdev, param in zip(means, stds, params):
    print("%f (%f) with: %r" % (mean, stdev, param))

model = KerasClassifier(build_fn=create_model, epochs=50, batch_size=32, verbose=0)

# define the grid search parameters
optimizer = ['Adagrad', 'Adadelta', 'Adam']
param_grid = dict(opt=optimizer)

# search the grid
grid = GridSearchCV(estimator=model, param_grid=param_grid, verbose=2)
grid_result = grid.fit(X_train, y_train)

print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
means = grid_result.cv_results_['mean_test_score']
stds = grid_result.cv_results_['std_test_score']
params = grid_result.cv_results_['params']
for mean, stdev, param in zip(means, stds, params):
    print("%f (%f) with: %r" % (mean, stdev, param))

model = create_model(lyrs=[8], dr=0.2)

print(model.summary())

training = model.fit(X_train, y_train, epochs=50, batch_size=32, 
                     validation_split=0.2, verbose=0)

# evaluate the model
scores = model.evaluate(X_train, y_train)
print("\n%s: %.2f%%" % (model.metrics_names[1], scores[1]*100))

plt.plot(training.history['acc'])
plt.plot(training.history['val_acc'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'validation'], loc='upper left')
plt.show()

