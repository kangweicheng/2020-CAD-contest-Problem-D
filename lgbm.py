import lightgbm as lgb
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GridSearchCV
import yaml
import argparse
import os
import numpy as np
import matplotlib.pyplot as plt
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

    # create dataset for lightgbm
    lgb_train = lgb.Dataset(X_train, y_train, categorical_feature=['type'])
    lgb_eval = lgb.Dataset(X_test, y_test, categorical_feature=['type'], reference=lgb_train)

    # specify your configurations as a dict
    if opt.grid_search:
        param_grid = {
            'boosting_type': cfg['HYPERPARAMETER']['LGBM']['boosting_type'],
            'objective': cfg['HYPERPARAMETER']['LGBM']['objective'],
            'metric': cfg['HYPERPARAMETER']['LGBM']['metric'],
            'num_leaves': cfg['HYPERPARAMETER']['LGBM']['num_leaves'],
            'learning_rate': cfg['HYPERPARAMETER']['LGBM']['learning_rate'],
            'feature_fraction': cfg['HYPERPARAMETER']['LGBM']['feature_fraction'],
            'bagging_fraction': cfg['HYPERPARAMETER']['LGBM']['bagging_fraction'],
            'bagging_freq': cfg['HYPERPARAMETER']['LGBM']['bagging_freq'],
            'verbose': cfg['HYPERPARAMETER']['LGBM']['verbose'],
            'min_sum_hessian_in_leaf': cfg['HYPERPARAMETER']['LGBM']['min_sum_hessian_in_leaf'],
            'min_data_in_leaf': cfg['HYPERPARAMETER']['LGBM']['min_data_in_leaf'],
            'seed': cfg['HYPERPARAMETER']['LGBM']['seed']
        }

        print('Starting training...')
        # train
        estimator = lgb.LGBMRegressor(num_leaves=cfg['HYPERPARAMETER']['LGBM']['num_leaves'])
        gbm = GridSearchCV(estimator, param_grid, cv=3)
        gbm.fit(X_train, y_train, eval_set=[(X_test, y_test)], eval_metric=competition_score)

        print('Best parameters found by grid search are:', gbm.best_params_)

    else:
        params = {
        'boosting_type': 'dart',
        'objective': 'regression',
        'metric': 'l1',
        'num_leaves': 13,
        'learning_rate': 0.1,
        'feature_fraction': 0.9,
        'bagging_fraction': 0.8,
        'bagging_freq': 5,
        'verbose': 0,
        'min_sum_hessian_in_leaf': 10.0,
        'min_data_in_leaf': 80,
        'seed': 44000
    }
        gbm = lgb.train(params, lgb_train, num_boost_round=100, \
            valid_sets=lgb_eval, early_stopping_rounds=5)

    print('Saving model...')
    # save model to file
    gbm.save_model(cfg['SAVED']['model_fn'])

    print('Plotting feature importances...')
    ax = lgb.plot_importance(gbm, max_num_features=10, figsize=(10,6))
    plt.savefig('saved/importance.png')

    # print('Plotting split value histogram...')
    # ax = lgb.plot_split_value_histogram(gbm, feature='f26', bins='auto')
    # plt.savefig('saved/histogram.png')


    print('Starting predicting...')
    # predict
    y_pred = gbm.predict(X_test, num_iteration=gbm.best_iteration)
    # eval
    print('The error rate of prediction is:', competition_score(y_test, y_pred))
    print(y_test[:5], y_pred[:5])
