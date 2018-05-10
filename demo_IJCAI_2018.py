from MLFeatureSelection import FeatureSelection as fs
from sklearn.metrics import log_loss
import lightgbm as lgbm
import pandas as pd
import numpy as np


def prepare_data():
    """prepare you dataset here"""
    df = pd.read_csv('data/train/trainb.csv')
    df = df[~pd.isnull(df.is_trade)]
    item_category_list_unique = list(np.unique(df.item_category_list))
    df.item_category_list.replace(item_category_list_unique, list(np.arange(len(item_category_list_unique))),
                                  inplace=True)
    return df


def model_score(y_test, y_pred):
    """set up the evaluation score"""
    return log_loss(y_test, y_pred)


def validation(X, y, features, clf, lossfunction):
    """set up your validation method"""
    totaltest = 0
    for D in [24]:
        T = (X.day != D)
        X_train, X_test = X[T], X[~T]
        X_train, X_test = X_train[features], X_test[features]
        y_train, y_test = y[T], y[~T]
        clf.fit(X_train, y_train, eval_set=[(X_train, y_train), (X_test, y_test)], eval_metric='logloss', verbose=False,
                early_stopping_rounds=200)
        totaltest += lossfunction(y_test, clf.predict_proba(X_test)[:, 1])
    totaltest /= 1.0
    return totaltest


def add(x, y):
    return x + y


def substract(x, y):
    return x - y


def times(x, y):
    return x * y


def divide(x, y):
    return (x + 0.001) / (y + 0.001)


cross_method = {'+': add,
                '-': substract,
                '*': times,
                '/': divide, }


def main():
    sf = fs.Selector(sequence=True, random=True, cross=False)  # select the way you want to process searching
    sf.import_df(prepare_data(), label='is_trade')
    sf.import_loss_function(model_score, direction='descend')
    sf.import_cross_method(cross_method)
    sf.initial_non_trainable_features(
        ['used', 'instance_id', 'item_property_list', 'context_id', 'context_timestamp', 'predict_category_property',
         'is_trade'])
    sf.initial_features(
        ['item_category_list', 'item_price_level', 'item_sales_level', 'item_collected_level', 'item_pv_level', 'day'])
    sf.generate_col(key='mean', selectstep=2)
    sf.set_sample(0.1, sample_state=0, sample_mode=0)
    #    sf.SetFeaturesLimit(5)
    sf.set_time_limit(1)
    sf.clf = lgbm.LGBMClassifier(random_state=1, num_leaves=6, n_estimators=5000, max_depth=3, learning_rate=0.05,
                                 n_jobs=8)
    sf.set_log_file('recordml.log')
    sf.run(validation)


if __name__ == "__main__":
    main()
