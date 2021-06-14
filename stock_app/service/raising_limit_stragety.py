# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
from stock_app.service.base_strategy import BaseStratege


# 涨停筛选
class RaisingLimitStragete(BaseStratege):

    start_date = None
    end_date = None

    @classmethod
    def init(cls, start_date, end_date):
        cls.start_date = start_date
        cls.end_date = end_date

    @staticmethod
    def get_raising_limit(df, code):
        if df.empty:
            return
        df['pre_close'] = df['close'].shift(1)
        ret = list()
        limit = 9.5  # 界限值
        for idx in range(0, len(df)):
            # 昨日收盘价
            pre_close = df['pre_close'][idx]
            close_price = df['close'][idx]
            low = df['low'][idx]
            gain = BaseStratege.calc_gain(float(close_price), float(pre_close))  # 计算涨幅
            low_gain = BaseStratege.calc_gain(float(close_price), float(low))  # 计算涨幅
            aaa = abs(low_gain / gain)
            if abs(low_gain / gain) > 3:
                ret.append(code)
        return ret
