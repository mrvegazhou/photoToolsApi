# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
import pandas as pd
from stock_app.__init__ import utils
from stock_app.model.sz50_stock_trading import SZ50StockTrading
from stock_app.api.request_api import api_sz50_stock_by_year_season


# 同步上证50的交易数据
def sync_sz50_day_trading_list():
    now = utils["date"].get_now()
    first_quarter_date = utils["date"].get_last_day_of_the_quarter(now)
    first_quarter_date = str(first_quarter_date).split()[0]
    now_format = utils["date"].get_now_date()
    if now_format == first_quarter_date:
        year = now.year
        season = utils["date"].get_quarter(now)
        df = api_sz50_stock_by_year_season(year, season)
        for index, row in df.iterrows():
            kwargs = {
                'trading_date': "{}-{}-{}".format(index[0:4], index[4:6], index[6:8]),
                'close_price': row['收盘价'],
                'high_price': row['最高价'],
                'low_price': row['最低价'],
                'open_price': row['开盘价'],
                'volume': row['成交量(手)'],
                'change_amount': row['涨跌额'],
                'chg_pct': row['涨跌幅(%)'],
                'turnover': row['成交金额(万元)']
            }
            SZ50StockTrading.add_new_sz50_stock(**kwargs)




if __name__ == "__main__":
    now = utils["date"].get_now()
    # first_quarter_date = utils["date"].get_last_day_of_the_quarter(now)
    # now_format = utils["date"].get_now_date()
    # print(now_format)
    # first_quarter_date = utils["date"].get_last_day_of_the_quarter(now)
    # print(str(first_quarter_date).split()[0])

    import datetime, time

    sync_sz50_day_trading_list()
    # print(datetime.datetime.strptime('2012-09-20', '%Y-%m-%d'))