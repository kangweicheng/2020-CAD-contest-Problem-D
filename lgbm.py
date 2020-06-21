import lightgbm as lgb
import pandas as pd
from sklearn.metrics import mean_squared_error
import yaml
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--cfg_path', type=str, default='config/default.yaml')
parser.add_argument('--eval_only', action='store_true', default=False)
opt = parser.parse_args()

with open(opt.cfg_path, 'r') as f:
    cfg = yaml.safe_load(f)

def parse_dataset(fn):
    dataset = pd.read_csv(train_fn, names=['id', 'ans', 'type', 'transition', \
        'capacitance', 'process', 'voltage', 'temperature', 'rise_capacitance', 'fall_capacitance'])
    # dataset['type'] = dataset['type'].astype('int32')
    return dataset

def ensure_dir(dir):
    os.makedirs(dir, exist_ok=True)

if __name__ == '__main__':
    ensure_dir('saved/')
    ensure_dir('config/')


    train_fn = 'data/train/' + cfg['DATA']['fn']
    test_fn = 'data/test/' + cfg['DATA']['fn']
    df_train = parse_dataset(train_fn)
    # df_test = parse_dataset(test_fn)

    y_train = df_train['ans']
    # y_test = df_test.iloc[:, 2]
    X_train = df_train.drop(labels=['id', 'ans'], axis=1)
    # X_test = df_test.drop(labels=['id', 'ans'], axis=1)

    # create dataset for lightgbm
    lgb_train = lgb.Dataset(X_train, y_train, categorical_feature=['type'])
    # lgb_eval = lgb.Dataset(X_test, y_test, categorical_feature=['type'], reference=lgb_train)

    # specify your configurations as a dict
    params = {
        'boosting_type': cfg['HYPERPARAMETER']['LGBM']['boosting_type'],
        'objective': cfg['HYPERPARAMETER']['LGBM']['objective'],
        'metric': cfg['HYPERPARAMETER']['LGBM']['metric'],
        'num_leaves': cfg['HYPERPARAMETER']['LGBM']['num_leaves'],
        'learning_rate': cfg['HYPERPARAMETER']['LGBM']['learning_rate'],
        'feature_fraction': cfg['HYPERPARAMETER']['LGBM']['feature_fraction'],
        'bagging_fraction': cfg['HYPERPARAMETER']['LGBM']['bagging_fraction'],
        'bagging_freq': cfg['HYPERPARAMETER']['LGBM']['bagging_freq'],
        'verbose': cfg['HYPERPARAMETER']['LGBM']['verbose']
    }

    print('Starting training...')
    # train
    gbm = lgb.train(params, lgb_train, num_boost_round=cfg['HYPERPARAMETER']['LGBM']['epoch'], \
        valid_sets=lgb_train, early_stopping_rounds=5)

    print('Saving model...')
    # save model to file
    gbm.save_model(cfg['SAVED']['model_fn'])

    print('Starting predicting...')
    # predict
    y_pred = gbm.predict(X_train, num_iteration=gbm.best_iteration)
    # eval
    print('The rmse of prediction is:', mean_squared_error(y_train, y_pred) ** 0.5)
    print(y_train[:5], y_pred[:5])
