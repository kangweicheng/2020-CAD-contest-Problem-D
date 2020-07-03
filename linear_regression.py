import lightgbm as lgb
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GridSearchCV
from sklearn import linear_model
import yaml
import argparse
import os
import numpy as np
import matplotlib.pyplot as plt
import math
import pickle

parser = argparse.ArgumentParser()
parser.add_argument('--cfg_path', type=str, default='config/default.yaml')
parser.add_argument('--eval_only', action='store_true', default=False)
parser.add_argument('--grid_search', action='store_true', default=False)
opt = parser.parse_args()

with open(opt.cfg_path, 'r') as f:
    cfg = yaml.safe_load(f)

def parse_dataset(fn):
    with open(fn, 'rb') as file:
        dataset = pickle.load(file).iloc[:, :10]
    # dataset['type'] = dataset['type'].astype('int32')
    return dataset

def ensure_dir(dir):
    os.makedirs(dir, exist_ok=True)

def competition_score(gt, pred):
    return 'Error Rate', np.sum(np.abs(pred-gt) / gt, axis=0) / len(gt), False

if __name__ == '__main__':
    ensure_dir('saved/')
    ensure_dir('config/')


    train_fn = 'data/train/' + cfg['DATA']['fn']
    test_fn = 'data/test/' + cfg['DATA']['fn']
    df_train = parse_dataset(train_fn)
    df_test = parse_dataset(test_fn)

    y_train = df_train['ans']
    y_test = df_test['ans']
    X_train = df_train.drop(labels=['id', 'ans'], axis=1)
    X_test = df_test.drop(labels=['id', 'ans'], axis=1)

    regr = linear_model.LinearRegression()
    regr.fit(X_train, y_train)

    print('Starting predicting...')
    # predict
    y_pred = regr.predict(X_test)
    # eval
    print('The error rate of prediction is:', competition_score(y_test, y_pred))
    print(y_test[:5], y_pred[:5])
