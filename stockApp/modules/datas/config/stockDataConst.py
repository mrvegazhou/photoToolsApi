# _*_ coding: utf-8 _*_
import os
from enum import Enum, unique

@unique
class Constants(Enum):
    # 股票实时
    REAL_TIME_SINA_URL = "http://hq.sinajs.cn/rn={}&list="
    REAL_TIME_EAST_MONEY_URL = "https://push2.eastmoney.com/api/qt/ulist.np/get"
    FULL_REAL_TIME_EAST_MONEY_URL = 'http://push2.eastmoney.com/api/qt/stock/get'
    REAL_TIME_NET_EASE_URL = 'http://api.money.126.net/data/feed/{},money.api'
    REAL_TIME_NET_TENCENT_URL = 'http://qt.gtimg.cn/q={}'

    # 组合市场行情
    MARKET_REAL_TIME_URL = 'http://push2.eastmoney.com/api/qt/clist/get'

@unique
class EastConfig(Enum):
    # 东方财富网网页请求头
    request_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2'}

    code_id_dict = {
        '上证综指': '1.000001', 'sh': '1.000001', '上证指数': '1.000001', '1.000001': '1.000001',
        '深证综指': '0.399106', 'sz': '0.399106', '深证指数': '0.399106', '深证成指': '0.399106',
        '创业板指': '0.399006', 'cyb': '0.399006', '创业板': '0.399006', '创业板指数': '0.399006',
        '沪深300': '1.000300', 'hs300': '1.000300',
        '上证50': '1.000016', 'sz50': '1.000016',
        '上证180': '1.000010', 'sz180': '1.000010',
        '科创50': '1.000688', 'kc50': '1.000688',
        '中小100': '0.399005', 'zxb': '0.399005', '中小板': '0.399005', '中小板指数': '0.399005', '深圳100': '0.399005',
        '标普500': '100.SPX', 'SPX': '100.SPX', 'spx': '100.SPX', '标普指数': '100.SPX',
        '纳斯达克': '100.NDX', '纳斯达克指数': '100.NDX', 'NSDQ': '100.NDX', 'nsdq': '100.NDX',
        '道琼斯': '100.DJIA', 'DJIA': '100.DJIA', 'dqs': '100.DJIA', '道琼斯指数': '100.DJIA',
        '韩国KOSPI': '100.KS11', '韩国综合': '100.KS11', '韩国综合指数': '100.KS11', '韩国指数': '100.KS11',
        '加拿大S&P/TSX': '100.TSX', '加拿大指数': '100.TSX',
        '巴西BOVESPA': '100.BVSP', '巴西指数': '100.BVSP',
        '墨西哥BOLSA': '100.MXX', '墨西哥指数': '100.MXX',
        '俄罗斯RTS': '100.RTS', '俄罗斯指数': '100.RTS',
    }

    market_dict = {
        'all_stocks': 'm:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23',
        'sh_sz_A': 'm:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23',
        'sh_A': 'm:1 t:2,m:1 t:23',
        'sz_A': 'm:0 t:6,m:0 t:80',
        'bj_A': 'm:0 t:81 s:2048',
        'chi_next_A': 'm:0 t:80',
        'star_A': 'm:1 t:23',
        'sh_sz_bj_A': 'm:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23,m:0 t:81 s:2048',
        'sh_north_bound_A': 'b:BK0707',
        'sz_north_bound_A': 'b:BK0804',
        'risk_warning_board': 'm:0 f:4,m:1 f:4',
        'delisting': 'm:0 s:3',
        'new_stocks': 'm:0 f:8,m:1 f:8',
        'american_stocks': 'm:105,m:106,m:107',
        'hk_stocks': 'm:128 t:3,m:128 t:4,m:128 t:1,m:128 t:2',
        'china_concept_stocks': 'b:MK0201',
        'regional_sector': 'm:90 t:1 f:!50',
        'industry_sector': 'm:90 t:2 f:!50',
        'conceptual_sector': 'm:90 t:3 f:!50',
        'sh_index': 'm:1 s:2',
        'sz_index': 'm:0 t:5',
        'sh_sz_index': 'm:1 s:2,m:0 t:5',
        'bond': 'b:MK0354',
        'future': 'm:113,m:114,m:115,m:8,m:142',
        'ETF': 'b:MK0021,b:MK0022,b:MK0023,b:MK0024',
        'LOF': 'b:MK0404,b:MK0405,b:MK0406,b:MK0407',
    }

    stock_real_time_dict = {
        'code': 'f12',
        'name': 'f14',
        'amplitude': 'f3',
        'now_price': 'f2',
        'high_price': 'f15',
        'low_price': 'f16',
        'open': 'f17',
        'turnover_rate': 'f8',
        'volume_ratio': 'f10',
        'p_e_ratio': 'f9', # 市盈率
        'volume': 'f5',
        'turnover': 'f6',
        'yesterday_close': 'f18',
        'total_market_value': 'f20',  # 总市值
        'floating_market_value': 'f21',  # 流通市值
        'date': 'f124',
    }

    full_stock_real_time_dict = {
        'name': 'f58',
        'code': 'f57',
        'open': 'f46',

        'yesterday_close': 'f60',
        'now_price': 'f43',

        'high_price': 'f44',
        'low_price': 'f45',

        'volume': 'f47', # 今日成交量
        'turnover': 'f48', # 今日成交金额

        'buy_volume': 'f49', # 买入数量
        'percent': 'f50', # 涨跌幅
        # 'updown': 'f4', # 涨跌金额
        'sell_volume': 'f59', # 卖出数量
        'p_e_ratio': 'f52', # 市盈率
        'turnover_rate': 'f55', # 换手率
        'amplitude': 'f62', # "振幅(%)":'f62',
        'volume_ratio': 'f92', # 量比
        'total_market_value': 'f84', # 总市值
        'floating_market_value': 'f85', # 流通市值
        'net_inflow': 'f103', # 净流入
        'inner_disk': 'f104', # 内盘
        'outer_disk': 'f105', # 外盘
        'bid_volume': 'f107', # 委买量
        'ask_volume': 'f108', # 委卖量
        'commitment_ratio': 'f109', # 委比
        'bid_amount': 'f110', # 委买金额
        'ask_amount': 'f111', # 委卖金额
        'commitment_ratio_value': 'f112', # 委比值

        'five_trades': 'f113', # 五档成交
        'five_bid': 'f114', # 五档委买
        'five_ask': 'f115', # 五档委卖
        'capital_inflow': 'f116', # 资金流入
        'capital_outflow': 'f117', # 资金流出

        'bid_vol_1': 'f16',
        'bid_price_1': 'f15',

        'bid_vol_2': 'f20',
        'bid_price_2': 'f19',

        'bid_vol_3': 'f40',
        'bid_price_3': 'f39',

        'bid_vol_4': 'f36',
        'bid_price_4': 'f35',

        'bid_vol_5': 'f32',
        'bid_price_5': 'f31',

        'ask_vol_1': 'f14',
        'ask_price_1': 'f13',

        'ask_vol_2': 'f18',
        'ask_price_2': 'f17',

        'ask_vol_3': 'f36',
        'ask_price_3': 'f35',

        'ask_vol_4': 'f38',
        'ask_price_4': 'f37',

        'ask_vol_5': 'f34',
        'ask_price_5': 'f33',

        'date': 'f86',
        'trading_time_periods': 'f80', #交易时间段
        'time': 'f86',
    }


@unique
class SinaConfig(Enum):
    stock_real_time_dict = {
        'name': 0,
        'open': 1,

        'yesterday_close': 2,
        'now_price': 3,

        'high_price': 4,
        'low_price': 5,

        # '竞买价': 6,
        # '竞卖价': 7,

        'volume': 8,
        'turnover': 9,

        # 'percent': '涨跌幅',
        # 'updown': '涨跌金额',

        'bid_vol_1': 10,
        'bid_price_1': 11,

        'bid_vol_2': 12,
        'bid_price_2': 13,

        'bid_vol_3': 14,
        'bid_price_3': 15,

        'bid_vol_4': 16,
        'bid_price_4': 17,

        'bid_vol_5': 18,
        'bid_price_5': 19,

        'ask_vol_1': 20,
        'ask_price_1': 21,

        'ask_vol_2': 22,
        'ask_price_2': 23,

        'ask_vol_3': 24,
        'ask_price_3': 25,

        'ask_vol_4': 26,
        'ask_price_4': 27,

        'ask_vol_5': 28,
        'ask_price_5': 29,

        'date': 30,
        'time': 31,
    }

@unique
class NetEaseConfig(Enum):
    stock_real_time_dict = {
        'name': 'name',
        'open': 'open',

        'yesterday_close': 'yestclose',
        'now_price': 'price',
        'high_price': 'high',
        'low_price': 'low',
        'volume': 'volume', # 成交量
        'turnover': 'turnover', # 成交额

        'percent': 'percent',
        'updown': 'updown',

        'bid_vol_1': 'bidvol1',
        'bid_price_1': 'bid1',

        'bid_vol_2': 'bidvol2',
        'bid_price_2': 'bid2',

        'bid_vol_3': 'bidvol3',
        'bid_price_3': 'bid3',

        'bid_vol_4': 'bidvol4',
        'bid_price_4': 'bid4',

        'bid_vol_5': 'bidvol5',
        'bid_price_5': 'bid5',

        'ask_vol_1': 'askvol1',
        'ask_price_1': 'ask1',

        'ask_vol_2': 'askvol2',
        'ask_price_2': 'ask2',

        'ask_vol_3': 'askvol3',
        'ask_price_3': 'ask3',

        'ask_vol_4': 'askvol4',
        'ask_price_4': 'ask4',

        'ask_vol_5': 'askvol5',
        'ask_price_5': 'ask5',

        'date': 'time',
        'time': 'time'
    }

@unique
class TencentConfig(Enum):
    stock_real_time_dict = {
        'name': 1,
        'open': 5,
        'yesterday_close': 4,
        'now_price': 3,
        'high_price': 33,
        'low_price': 34,
        'volume': 36,  # 成交量
        'turnover': 37,  # 成交额
        'turnover_rate': 38,
        'percent': 32,
        'updown': 31,
        'out_trade': 7,
        'in_trade': 8,
        'p_e_ratio': 39,
        'limit_up_price': 47,
        'limit_down_price': 48,

        'bid_vol_1': 10,
        'bid_price_1': 9,

        'bid_vol_2': 12,
        'bid_price_2': 11,

        'bid_vol_3': 14,
        'bid_price_3': 13,

        'bid_vol_4': 16,
        'bid_price_4': 15,

        'bid_vol_5': 18,
        'bid_price_5': 17,

        'ask_vol_1': 20,
        'ask_price_1': 19,

        'ask_vol_2': 22,
        'ask_price_2': 21,

        'ask_vol_3': 24,
        'ask_price_3': 23,

        'ask_vol_4': 26,
        'ask_price_4': 25,

        'ask_vol_5': 28,
        'ask_price_5': 27,

        'date': 30
    }