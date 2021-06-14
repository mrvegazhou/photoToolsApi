# -*- coding: utf-8 -*-
import sys, datetime
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
import pandas as pd

# ==========计算海龟交易法则的买卖点
# 设定海龟交易法则的两个参数，当收盘价大于最近N1天的最高价时买入，当收盘价低于最近N2天的最低价时卖出
# 这两个参数可以自行调整大小，但是一般N1 > N2

N1 = 20
N2 = 10

def get_TTA(df):
    # 通过rolling_max方法计算最近N1个交易日的最高价
    df['n1_high'] = pd.rolling_max(df['high'], N1)
    # 对于上市不足N1天的数据，取上市至今的最高价
    df['n1_high'].fillna(value=pd.expanding_max(df['high']), inplace=True)

    # 通过相似的方法计算最近N2个交易日的最低价
    df['n2_low'] = pd.rolling_min(df['low'], N1)
    df['n2_low'].fillna(value=pd.expanding_min(df['low']), inplace=True)

    # 当当天的【close】> 昨天的【最近N1个交易日的最高点】时，将【收盘发出的信号】设定为1
    buy_index = df[df['close'] > df['n1_high'].shift(1)].index
    df.loc[buy_index, 'TTA_sign'] = 1
    # 当当天的【close】< 昨天的【最近N2个交易日的最低点】时，将【收盘发出的信号】设定为0
    sell_index = df[df['close'] < df['最近N2个交易日的最低点'].shift(1)].index
    df.loc[sell_index, 'TTA_sign'] = 0

    return df


