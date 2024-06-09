# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/stock-api")
import akshare as ak
import pandas as pd
import numpy as np


def get_momentum_and_contrariam(stocks, df, start_date, end_date, window=3):
    stock_df = pd.DataFrame([[s.name, s.code] for s in stocks], columns=["name", "code"])
    df.sort_index(inplace=True)
    # 判断每天开盘是否涨停
    df.loc[df['open'] > df['close'].shift(1) * 1.097, 'limit_up'] = 1
    index_data = df[start_date : end_date]
    # 转成月度数据
    by_month = index_data[['close']].resample('M').last()
    by_month.reset_index(inplace=True)
    momentum_portfolio_all = pd.DataFrame()
    contrarian_portfolio_all = pd.DataFrame()

    for i in range(window, len(by_month) - 1):
        # 排名期第一个月
        start_month = by_month['date'].iloc[i - window]
        # 排名期最后一个月
        end_month = by_month['date'].iloc[i]
        # 取出在排名期内的数据
        stock_temp = stock_df[(all_stock['date'] > start_month) & (all_stock['date'] <= end_month)]
