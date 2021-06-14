# -*- coding: utf-8 -*-
from model import stock, day_trading

from sqlalchemy import Column,String,create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
import datetime,time
import akshare as ak
from chinese_calendar import is_workday, is_holiday

if __name__ == "__main__":
    # engine = create_engine('postgresql+psycopg2://postgres:root@127.0.0.1:5432/stock', echo=True)
    # DBsession = sessionmaker(bind=engine)
    # session = DBsession()
    # session.execute("SET search_path TO stock")
    # query = session.query(stock.Stock)
    # print(session.query(func.count(stock.Stock.uuid)).one()[0])
    #
    # stock = stock.Stock()
    # codes_list = stock.get_all_stock_codes()
    # for code in codes_list:
    #     tmp = ak.stock_zh_a_daily(code.code, "20100131", "20210506", adjust="hfq")
    #     for index, row in tmp.iterrows():
    #         obj = day_trading.DayTrading.model(code.code)
    #         obj.stock_code = code.code
    #         obj.trading_date = index
    #         obj.close_price = row.close
    #         obj.high_price = row.high
    #         obj.low_price = row.low
    #         obj.open_price = row.open
    #         obj.volume = row.volume
    #         obj.outstanding_share = row.outstanding_share
    #         obj.turnover = row.turnover
    #         session.add(obj)
    #         session.commit()

    # obj = day_trading.DayTrading
    # code = "sh600000"
    # start_date = "2021-04-01"
    # end_date = "2021-04-02"
    # pagination = obj.query.filter(obj.stock_code == code).filter(obj.trading_date >= start_date, obj.trading_date <= end_date).order_by(obj.trading_date.desc()).all()
    # print(pagination)

    import pandas as pd

    # for pandas_datareader, otherwise it might have issues, sometimes there is some version mismatch
    pd.core.common.is_list_like = pd.api.types.is_list_like
    import pandas_datareader.data as web
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    import datetime
    import time

    import yfinance as yahoo_finance

    ticker = 'NGG'
    start_time = datetime.datetime(2017, 10, 1)
    end_time = datetime.datetime.now().date().isoformat()

    connected = False
    while not connected:
        try:
            ticker_df = web.get_data_yahoo(ticker, start=start_time, end=end_time)
            connected = True
            print('connected to yahoo')
        except Exception as e:
            print("type error: " + str(e))
            time.sleep(5)
            pass

    ticker_df = ticker_df.reset_index()
    x_data = ticker_df.index.tolist()
    y_data = ticker_df['Low']

    x = np.linspace(0, max(ticker_df.index.tolist()), max(ticker_df.index.tolist()) + 1)

    # 用17次多项式拟合，可改变多项式阶数；
    pol = np.polyfit(x_data, y_data, 17)
    # 求对应x的各项拟合函数值
    y_pol = np.polyval(pol, x)

    # plt.figure(figsize=(15, 2), dpi=120, facecolor='w', edgecolor='k')
    # plt.plot(x_data, y_data, 'o', markersize=1.5, color='grey', alpha=0.7)
    # plt.plot(x, y_pol, '-', markersize=1.0, color='black', alpha=0.9)
    # plt.legend(['stock data', 'polynomial fit'])
    # plt.show()

    data = y_pol
    min_max = np.diff(np.sign(np.diff(data))).nonzero()[0] + 1  # local min & max
    l_min = (np.diff(np.sign(np.diff(data))) > 0).nonzero()[0] + 1  # local min
    l_max = (np.diff(np.sign(np.diff(data))) < 0).nonzero()[0] + 1

    print(data)