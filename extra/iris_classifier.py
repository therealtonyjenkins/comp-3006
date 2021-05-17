from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

## 1. IMPORT THE DATA

# unpack the dataset with return_X_y so that we only get the tuple (data, target) (i.e. predictors and responses)
X, y = load_iris(return_X_y = True)

## 2. SPLIT TEST/TRAIN

# split into testing and training data; returns numpy arrays
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = .3)

## 3. MODEL GENERATION

# create a LogisticRegression and SVM model and fit it against our data
lrm = LogisticRegression().fit(X_train, y_train)
svm = SVC(kernel= 'linear').fit(X_train, y_train)
# store model information so we can loop quickly
models = { 'LogisticRegression': lrm, 'SupportVectorMachines': svm }

## 4. PREDICTION

for name, model in models.items():
    # predict responses using the linear model on the X_train set
    y_train_predict = model.predict(X_train)
    # calculate root means squared error
    rmse = (np.sqrt(mean_squared_error(y_train, y_train_predict)))
    # calculate r-squared
    r2 = r2_score(y_train, y_train_predict)

    print('{} model performance for training set'.format(name))
    print('--------------------------------------')
    print('RMSE is {}'.format(rmse))
    print('R2 score is {}'.format(r2))
    print('\n')

    # model evaluation for testing set
    y_test_predict = model.predict(X_test)
    rmse = (np.sqrt(mean_squared_error(y_test, y_test_predict)))
    r2 = r2_score(y_test, y_test_predict)

    print('{} model performance for training set'.format(name))
    print('--------------------------------------')
    print('RMSE is {}'.format(rmse))
    print('R2 score is {}'.format(r2))
    print('\n')