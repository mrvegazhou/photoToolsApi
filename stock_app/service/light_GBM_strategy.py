# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
import lightgbm as lgb
from sklearn.metrics import accuracy_score
import numpy as np

def get_light_GBM(df):
    df['post_close'] = df['close'].shift(-1)  # 明日收盘价
    df['target'] = df['post_close'] - df['close']

    target = 'target'
    X = df.loc[:, df.columns != target]
    y = df.loc[:, df.columns == target]
    y.loc[y['target'] >= 0, 'target'] = 1
    y.loc[y['target'] < 0, 'target'] = 0
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    # 转换为Dataset数据格式
    lgb_train = lgb.Dataset(X_train, label=y_train)
    lgb_eval = lgb.Dataset(X_test, label=y_test)
    # 参数
    params = {
        'boosting_type': 'gbdt',  # 设置提升类型
        'objective': 'multiclass',  # 目标函数
        'num_class': 2,
        'metric': 'multi_logloss',  # 评估函数
        'num_leaves': 31,  # 叶子节点数
        'learning_rate': 0.01,  # 学习速率
        'feature_fraction': 0.8,  # 建树的特征选择比例
        'bagging_fraction': 0.8,  # 建树的样本采样比例
        'bagging_freq': 5,  # k 意味着每 k 次迭代执行bagging
        'seed': 100,
        'n_jobs': -1,
        'verbose': -1,
        'lambda_l1': 0.1,
        'lambda_l2': 0.2,
    }

    # 模型训练
    gbm = lgb.train(params, lgb_train, num_boost_round=500)
    y_pred_prob = gbm.predict(X_test, num_iteration=gbm.best_iteration)
    # print(y_pred_prob)
    y_pred = np.argmax(y_pred_prob, axis=1)
    # print(y_pred)

    score = accuracy_score(y_pred, y_test)
    print('准确率： ' + str(round(score * 100, 2)) + '%')