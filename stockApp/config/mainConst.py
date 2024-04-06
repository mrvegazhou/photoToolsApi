# _*_ coding: utf-8 _*_
import os
from enum import Enum, unique

@unique
class Constant(Enum):
    PAGE_SIZE = 20


@unique
class ErrConstant(Enum):
    STOCK_CODE_ERR = "输入代码有误"


@unique
class StockDict(Enum):
    stock_real_time_dict = {
        'name': '名称',
        'code': '代码',

        'yesterday_close': '昨日收盘价',
        'now_price': '当前价格',
        'open': '开盘价',
        'volume': '成交量',
        'low_price': '最低价',
        'high_price': '最高价',
        'turnover': '成交额',
        'percent': '涨跌幅',
        'updown': '涨跌金额',

        'turnover_rate': '换手率',
        'amplitude': '振幅(%)',

        'bid_vol_5': '买5数量',
        'bid_vol_4': '买4数量',
        'bid_vol_3': '买3数量',
        'bid_vol_2': '买2数量',
        'bid_vol_1': '买1数量',
        'bid_price_5': '买5价格',
        'bid_price_4': '买4价格',
        'bid_price_3': '买3价格',
        'bid_price_2': '买2价格',
        'bid_price_1': '买1价格',

        'ask_vol_5': '卖5数量',
        'ask_vol_4': '卖4数量',
        'ask_vol_3': '卖3数量',
        'ask_vol_2': '卖2数量',
        'ask_vol_1': '卖1数量',
        'ask_price_5': '卖5价格',
        'ask_price_4': '卖4价格',
        'ask_price_3': '卖3价格',
        'ask_price_2': '卖2价格',
        'ask_price_1': '卖1价格',
    }