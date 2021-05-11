# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
from stock_app.__init__ import utils, current_app
from stock_app.model.day_trading import DayTrading
from stock_app.model.stock import Stock
import akshare as ak
import matplotlib.pyplot as plt



if __name__ == "__main__":
    df = ak.stock_zh_a_daily(symbol='sz002241', start_date="20100101", end_date="20210509", adjust="qfq")
    # 昨日收盘价
    df['pre_close'] = df['close'].shift(1)
    # 明日收盘价
    df['post_close'] = df['close'].shift(-5)
    # 对于开盘价涨跌百分比
    df['close-open'] = (df['close'] - df['open']) / df['open']
    print(df)
