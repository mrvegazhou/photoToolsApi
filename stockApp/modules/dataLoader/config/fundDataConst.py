# _*_ coding: utf-8 _*_
from enum import Enum, unique

@unique
class Constants(Enum):
    # 基金排名
    FUNDS_CODES_URL = 'http://fund.eastmoney.com/data/rankhandler.aspx'
    # 基金历史数据
    FUND_HISTORY_URL = 'https://fundmobapi.eastmoney.com/FundMNewApi/FundMNHisNetList'
    # 基金持仓
    FUND_INVEST_POSITION_URL = 'https://fundmobapi.eastmoney.com/FundMNewApi/FundMNInverstPosition'
    # 基金基本信息
    FUND_BASE_INFO_URL = 'https://fundmobapi.eastmoney.com/FundMNewApi/FundMNNBasicInformation'
    # 基金行业分布信息
    FUND_INDUSTRY_DISTRIBUTION_URL = 'https://fundmobapi.eastmoney.com/FundMNewApi/FundMNSectorAllocation'
    # 基金公开日期
    FUND_PUBLIC_DATES_URL = "https://fundmobapi.eastmoney.com/FundMNewApi/FundMNIVInfoMultiple"

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

    # 通过基金类型查询基金列表
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

    # 基金历史数据
    fund_history_dict = {
        'date': '日期',
        'NAV_per_unit': '单位净值',
        'cumulative_NAV': '累计净值',
        'percent': '涨跌幅'
    }

    # 基金持仓
    fund_invest_position_dict = {
        'stock_code': 'GPDM',
        'stock_name': 'GPJC',
        'pos_holding_prop': 'JZBL',
        'code': 'fund_code',
        'date': 'date'
    }

    # 基金基础信息
    fund_base_info_dict = {
        'code': 'FCODE', #基金代码
        'short_name': 'SHORTNAME',  #基金简称
        'fund_inception_date': 'ESTABDATE', #成立日期
        'percent': 'RZDF', #涨跌幅
        'new_NAV': 'DWJZ', #最新净值
        'fund_company': 'JJGS', #基金公司
        'NAV_update_date': 'FSRQ', #净值更新日期
        'func_comment': 'COMMENTS', #简介
    }

    # 基金行业分布
    fund_industry_distribution_dict = {
        'industry_name': 'HYMC',
        'portfolio_weight': 'ZJZBL',
        'announcement_date': 'FSRQ',
        'market_value': 'SZ',
    }