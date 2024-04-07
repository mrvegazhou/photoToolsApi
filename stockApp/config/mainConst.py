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
    market_dict = {
        'all_stocks': '所有股票',
        'sh_sz_A': '沪深A',
        'sh_A': '上证A',
        'sz_A': '深证A',
        'bj_A': '北证A',
        'chi_next_A': '创业板',
        'star_A': '科创板',
        'sh_sz_bj_A': '沪深京A',
        'sh_north_bound_A': '沪股通',
        'sz_north_bound_A': '深股通',
        'risk_warning_board': '风险警示板',
        'delisting': '两网及退市',
        'new_stocks': '新股',
        'american_stocks': '美股',
        'hk_stocks': '港股',
        'china_concept_stocks': '中概股',
        'regional_sector': '地域板块',
        'industry_sector': '行业板块',
        'conceptual_sector': '概念板块',
        'sh_index': '上证指数',
        'sz_index': '深证指数',
        'sh_sz_index': '沪深指数',
        'bond': '可转债',
        'future': '期货',
        'ETF': 'ETF',
        'LOF': 'LOF',
    }

    stock_dict = {
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
        'floating_market_value': '流通市值',
        'total_market_value': '总市值',
        'p_e_ratio': '市盈率',

        'limit_up_price': '涨停价',
        'limit_down_price': '跌停价',

        'out_trade': '外盘',
        'in_trade': '内盘',

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