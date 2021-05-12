# -*- coding: utf-8 -*-
import sys, datetime
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
from stock_app.model.day_trading import DayTrading
from stock_app.model.stock import Stock
from stock_app.api.request_api import api_stock_day_trading_info, api_stock_base_indicator
import talib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import lightgbm as lgb
import numpy as np
import pandas as pd

# 计算日涨跌幅
def statistics_all_stock_day_trading(start_date, end_date):
    all_stocks = get_all_stocks()
    frames = []
    count = 1
    for item in all_stocks:
        try:
            df = get_stock_special_indicators(item.code, start_date, end_date)
            df['code'] = item.code
            df = get_KDJ(get_MACD(df), plus=True)
            today_date = pd.to_datetime(datetime.datetime.strptime("2021-05-11", '%Y-%m-%d').date())
            new_df = df[(df['MACD_buy']==1) & (df['KDJ_buy']==1) & (df.index == today_date)]
            if not new_df.empty:
                print(count, item.code, new_df, "......")
                frames.append(new_df)
            count = count + 1
            # for index, row in df.iterrows():
            #     kwargs = {
            #         'trading_date': index,
            #         'stock_code': item.code,
            #         'close_price': row['close'],
            #         'high_price': row['high'],
            #         'low_price': row['low'],
            #         'open_price': row['open'],
            #         'volume': row['volume'],
            #         'outstanding_share': row['outstanding_share'],
            #         'turnover': row['turnover'],
            #         'chg_pct': row['chg_pct']
            #     }
            #     DayTrading.add_trading_info(item.code, **kwargs)
        except Exception:
            print("异常:", Exception)
    result = pd.concat(frames)
    print(result['code'])
    print(result)



# 获取股票各种指标
def get_stock_special_indicators(code, start_date, end_date):
    df = api_stock_day_trading_info(code, start_date, end_date)
    df['pre_close'] = df['close'].shift(1)
    df['chg_pct'] = round((df['close'] - df['pre_close']) / df['pre_close'] * 100, 6)
    # 震幅
    df['close_open_pct'] = round((df['close'] - df['open']) / df['open'] * 100, 6)
    # 今日涨跌
    df['close_diff'] = df['close'] - df['pre_close']

    df = df.fillna(0)


    df['RSI6'] = talib.RSI(df['close'], timeperiod=6)
    df['RSI12'] = talib.RSI(df['close'], timeperiod=12)
    df['RSI24'] = talib.RSI(df['close'], timeperiod=24)

    df['EMA12'] = talib.EMA(df['close'], timeperiod=12)
    df['EMA26'] = talib.EMA(df['close'], timeperiod=26)

    return df


def get_MACD(df):
    # 5日均线，下同
    df['MA5'] = talib.SMA(df['close'], timeperiod=5)
    df['MA10'] = talib.SMA(df['close'], timeperiod=10)
    df['MA20'] = talib.SMA(df['close'], timeperiod=20)

    # macd = 12 天 EMA - 26 天 EMA
    df['DIFF'], df['DEA'], df['MACD'] = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    df['MACD'] = df['MACD'] * 2
    df['MACD_buy'] = 0
    macd_position = df['DIFF'] > df['DEA']
    df.loc[macd_position[(macd_position == True) & (macd_position.shift() == False)].index, 'MACD_buy'] = 1
    df.loc[macd_position[(macd_position == False) & (macd_position.shift() == True)].index, 'MACD_buy'] = -1

    # 5日线上穿10日线：
    df['M5_cross_M10'] = 0
    ma_position = df['MA5'] > df['MA10']
    df.loc[ma_position[(ma_position == True) & (ma_position.shift() == False)].index, 'M5_cross_M10'] = 1
    return df

# kdj金叉
def get_KDJ(df, plus=False):
    low_list = df['low'].rolling(window=9).min()
    low_list.fillna(value=df['low'].expanding().min(), inplace=True)
    high_list = df['high'].rolling(window=9).max()
    high_list.fillna(value=df['high'].expanding().max(), inplace=True)
    rsv = (df['close'] - low_list) / (high_list - low_list) * 100
    df['KDJ_K'] = rsv.ewm(com=2).mean()
    df['KDJ_D'] = df['KDJ_K'].ewm(com=2).mean()
    df['KDJ_J'] = 3 * df['KDJ_K'] - 2 * df['KDJ_D']
    df['KDJ_buy'] = 0
    kdj_position = df['KDJ_K'] > df['KDJ_D']
    kdj_position_plus = (df['KDJ_J'].shift(2) < 20) & (df['KDJ_J'].shift(1) < 20)
    if plus:
        # day(-2).{KDJ_J}<20 and day(-1).{KDJ_J}<20 and day(0).{KDJ_J}-day(-1).{KDJ_J}>=40 and day(0).{Vol_Change}>=1
        kdj_position_plus = (df['KDJ_J'].shift(2) < 20) & (df['KDJ_J'].shift(1) < 20) & ((df['KDJ_J']-df['KDJ_J'].shift(1)) >= 40)
    df.loc[kdj_position[(kdj_position == True) & (kdj_position_plus == True) & (kdj_position.shift() == False)].index, 'KDJ_buy'] = 1
    df.loc[kdj_position[(kdj_position == False) & (kdj_position.shift() == True)].index, 'KDJ_buy'] = -1
    return df

# A股个股指标
def sync_stock_base_indicator(code, date):
    indicator_df = api_stock_base_indicator(code)
    tmp_df = indicator_df[indicator_df['trade_date'] == date]
    return indicator_df

# 暂时用talib公式代替
def get_dif_dea(df):
    data = np.array(df.close)
    ndata = len(data)
    m, n, T = 12, 26, 9
    EMA1 = np.copy(data)
    EMA2 = np.copy(data)
    f1 = (m - 1) / (m + 1)
    f2 = (n - 1) / (n + 1)
    f3 = (T - 1) / (T + 1)
    for i in range(1, ndata):
        EMA1[i] = EMA1[i - 1] * f1 + EMA1[i] * (1 - f1)
        EMA2[i] = EMA2[i - 1] * f2 + EMA2[i] * (1 - f2)
    DIF = EMA1 - EMA2
    df['DIF'] = DIF
    DEA = np.copy(DIF)
    for i in range(1, ndata):
        DEA[i] = DEA[i - 1] * f3 + DEA[i] * (1 - f3)
    df['DEA'] = DEA


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



# 获取所有股票代码
def get_all_stocks():
    stock = Stock()
    return stock.get_all_stock_codes()


if __name__ == "__main__":
    statistics_all_stock_day_trading("20100101", "20210511")

    # df['pre_close'] = df.shift(-1)['close']
    # df['chg_pct'] = df.apply(lambda x: (x.close-x.pre_close)/x.pre_close, axis=1)
    # print(df)
    # statistics_all_stock_day_trading("20100101", "20100510")
    # df = get_stock_indicators('sz300236', "20190310", "20210510")
    # get_light_GBM(df)

    # get_KDJ(df)
    # get_MACD(df)
    #
    # df.fillna(0, inplace=True)
    #
    # print(df[df['MACD_buy']==1])
    # print(df[df['KDJ_buy']==1])
    # print(df)

    # 测试指标
    # df = sync_stock_base_indicator("sz300236", "2021-05-11")
    # print(df[df['trade_date']=="2021-05-11"])


