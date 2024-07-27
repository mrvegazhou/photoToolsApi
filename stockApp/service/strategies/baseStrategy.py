# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/stockApi")
import pandas as pd
from core.utils.date_utils import get_last_day, get_first_day
#为了实现虚函数
from abc import ABC
from stockApp.modules.dataLoader.stockData.eastIntradayData import EastIntradayData


class BaseStrategy(ABC):

    # 通过股票名称过滤
    @staticmethod
    def name_filter(df, name_list):
        """
        过滤掉符合条件的股票：根据名字过滤，比如ST
        :param data:
        :param name_list:
        :return:
        """
        return df[~df['code'].str.contains("|".join(name_list))]

    # 通过日交易获取4个季度的平均的成交金额，成交量，换手率
    @staticmethod
    def get_vol_handoff_quarter_avg(code, year, quarter=1):
        intraday = EastIntradayData()
        start_date = get_first_day(year, 1).strftime('%Y%m%d')
        end_date = get_last_day(year, 12).strftime('%Y%m%d')
        df = intraday.get_intraday_data(code, begin=start_date, end=end_date)

        df.date = pd.to_datetime(df.date)
        df = df.set_index("date")
        df = df.to_period('Q')
        quarter_str = "{}Q{}".format(str(year), str(quarter))
        df = df[df.index==quarter_str]

        df["volume"] = pd.to_numeric(df["volume"])
        # 成交量（累计 单位：股）
        volume_avg = df['volume'].mean()

        df["turnover"] = pd.to_numeric(df["turnover"])
        # 成交额（单位：人民币元）
        amount_avg = df['turnover'].mean()

        # 换手率
        df["turnover_rate"] = pd.to_numeric(df["turnover_rate"])
        turn_avg = df['turnover_rate'].mean()

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

    # 成交量加权平均价格
    @staticmethod
    def vwap(df):
        v = df['volume'].values
        tp = (df['low'] + df['close'] + df['high']).div(3).values
        return df.assign(vwap=(tp * v).cumsum() / v.cumsum())


if __name__ == "__main__":
    # BaseStrategy.get_vol_handoff_quarter_avg('sz000002', 2021)
    pass
