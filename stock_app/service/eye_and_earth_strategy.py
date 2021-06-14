# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
from stock_app.service.base_strategy import BaseStrategy
from stock_app.__init__ import utils
import talib

# 天眼地量筛选策略
class EyeAndEarthStrategy(BaseStrategy):

    '''
    1. 判断五日线是否穿过20日均线
    2. 判断成交量是否最低
    '''
    @staticmethod
    def get_stocks_by_eye_earth(start_date, end_date):
        stock_list = BaseStrategy.get_all_stocks_df()
        ret = []
        for _, item in stock_list.iterrows():
            code = item.code
            tradings = BaseStrategy.get_stock_day_trading(code, start_date, end_date)
            volume_mean = tradings['volume'].mean()
            volume_min = tradings['volume'].min()
            vals = tradings.values[-1].tolist()
            if vals[5]<volume_mean or vals[5]==volume_min:
                tradings['MA5'] = talib.SMA(tradings['close_price'], timeperiod=5)
                tradings['MA20'] = talib.SMA(tradings['close_price'], timeperiod=20)
                tmp = tradings[ (tradings['MA5'].shift(1)<tradings['MA20'].shift(1)) & (tradings['MA5']>tradings['MA20']) & (tradings['trading_date']==end_date) ]
                if not tmp.empty:
                    ret.append(code)
        return ret


