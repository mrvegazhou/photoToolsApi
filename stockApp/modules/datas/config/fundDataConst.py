# _*_ coding: utf-8 _*_
from enum import Enum, unique

@unique
class Constants(Enum):
    # 基金排名
    FUNDS_CODES_URL = 'http://fund.eastmoney.com/data/rankhandler.aspx'
    # 基金历史数据
    FUND_HISTORY_URL = 'https://fundmobapi.eastmoney.com/FundMNewApi/FundMNHisNetList'

@unique
class EastConfig(Enum):
    fund_headers = {
        'User-Agent': 'EMProjJijin/6.2.8 (iPhone; iOS 13.6; Scale/2.00)',
        'GTOKEN': '98B423068C1F4DEF9842F82ADF08C5db',
        'clientInfo': 'ttjj-iPhone10,1-iOS-iOS13.6',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'fundmobapi.eastmoney.com',
        'Referer': 'https://mpservice.com/516939c37bdb4ba2b1138c50cf69a2e1/release/pages/FundHistoryNetWorth',
    }

    funds_type_dict = {
        'zq': '债券类型基金',
        'gp': '股票类型基金',
        'etf': 'ETF基金',
        'hh': '混合型基金',
        'zs': '指数型基金',
        'fof': 'FOF基金',
        'qdii': 'QDII型基金',
        'all': '全部'
    }

    funds_codes_dict = {
        'code': 0,
        'short_name': 1,
    }

    fund_history_dict = {
        'date': '日期',
        'NAV_per_unit': '单位净值',
        'cumulative_NAV': '累计净值',
        'percent': '涨跌幅'
    }