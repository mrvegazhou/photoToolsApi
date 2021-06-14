# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
from stock_app.model.stock import Stock
from stock_app.model.day_trading import DayTrading
from stock_app.api.request_api import api_stock_day_trading_info, api_stock_base_indicator, api_stock_day_trading_info2
import pandas as pd
from core.utils.date_utils import get_last_day, get_first_day
#为了实现虚函数
from abc import ABC

class BaseStrategy(ABC):

    # 获取所有股票代码
    @staticmethod
    def get_all_stocks():
        stock = Stock()
        return stock.get_all_stock_codes()


    # 获取所有股票的dataframe格式
    @staticmethod
    def get_all_stocks_df():
        return pd.DataFrame([[s.name, s.code] for s in BaseStrategy.get_all_stocks()], columns=["name", "code"])


    # A股个股指标
    @staticmethod
    def sync_stock_base_indicator(code, date):
        indicator_df = api_stock_base_indicator(code)
        tmp_df = indicator_df[indicator_df['trade_date'] == date]
        return indicator_df



    # 获取股票各种指标
    @staticmethod
    def get_stock_special_indicators(code, start_date, end_date):
        df = api_stock_day_trading_info(code, start_date, end_date)
        if df.empty:
            return pd.DataFrame()
        df['pre_close'] = df['close'].shift(1)
        df['chg_pct'] = round((df['close'] - df['pre_close']) / df['pre_close'] * 100, 6)
        # 震幅
        df['close_open_pct'] = round((df['close'] - df['open']) / df['open'] * 100, 6)
        # 今日涨跌
        df['close_diff'] = df['close'] - df['pre_close']

        df = df.fillna(0)

        # df['RSI6'] = talib.RSI(df['close'], timeperiod=6)
        # df['RSI12'] = talib.RSI(df['close'], timeperiod=12)
        # df['RSI24'] = talib.RSI(df['close'], timeperiod=24)
        #
        # df['EMA12'] = talib.EMA(df['close'], timeperiod=12)
        # df['EMA26'] = talib.EMA(df['close'], timeperiod=26)

        return df


    @staticmethod
    def get_stock_day_trading(code, start_date, end_date):
        cols = ['trading_date', 'close_price', 'high_price', 'low_price', 'open_price', 'volume', 'turnover', 'chg_pct', 'outstanding_share', 'stock_code']
        ret = DayTrading.get_stock_trading_list_by_SQL(code, start_date, end_date, cols)
        return pd.DataFrame(ret, columns=cols)




    # 通过股票名称过滤
    @staticmethod
    def name_filter(df, name_list):
        """
        过滤掉符合条件的股票：根据名字过滤，比如ST
        :param data:
        :param name_list:
        :return:
        """
        return df[ ~ df['code'].str.contains("|".join(name_list))]


    # 通过日交易获取4个季度的平均的成交金额，成交量，换手率
    @staticmethod
    def get_vol_handoff_quarter_avg(code, year, quarter=1):
        start_date = get_first_day(year, 1).strftime('%Y-%m-%d')
        end_date = get_last_day(year, 12).strftime('%Y-%m-%d')
        df = api_stock_day_trading_info2(code, 'd', start_date, end_date)

        df.date = pd.to_datetime(df.date)
        df = df.set_index("date")
        df = df.to_period('Q')
        quarter_str = "{}Q{}".format(str(year), str(quarter))
        df = df[df.index==quarter_str]

        df["volume"] = pd.to_numeric(df["volume"])
        # 成交量（累计 单位：股）
        volume_avg = df['volume'].mean()

        df["amount"] = pd.to_numeric(df["amount"])
        # 成交额（单位：人民币元）
        amount_avg = df['amount'].mean()

        # 换手率
        df["turn"] = pd.to_numeric(df["turn"])
        turn_avg = df['turn'].mean()

        return volume_avg, amount_avg, turn_avg


    # 功能：计算百分比
    # 参数：分子，分母
    @staticmethod
    def percentage(numerator, denominator):
        return numerator / denominator * 100

    # 计算涨幅
    @staticmethod
    def calc_gain(close, open):
        if close == 0 or open == 0:
            return 0
        rang = close - open
        gain = (rang / open) * 100
        gain = '%.2f' % gain
        return gain

    # 计算涨停价格
    @staticmethod
    def calc_limit_price(pre_close):
        if pre_close == 0:
            return 0
        limit = pre_close + pre_close * 0.1
        limit = '%.2f' % limit
        return limit



if __name__ == "__main__":
    print(BaseStrategy.get_stock_day_trading("sh600000", '2010-01-26', '2010-02-26'))
    # BaseStrategy.get_vol_handoff_quarter_avg('sz000002', 2021)