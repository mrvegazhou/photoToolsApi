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
        'date': '日期',
        'time': '时间',
        'floating_shares': '流通股',
        'total_share_capital': '总股本',
        'IPO_date': '上市时间',
        'yesterday_close': '昨日收盘价',
        'now_price': '当前价格',
        'open': '开盘价',
        'close': '收盘价',
        'volume': '成交量',
        'volume_ratio': '量比',
        'low_price': '最低价',
        'high_price': '最高价',
        'turnover': '成交额',
        'percent': '涨跌幅',
        'price_change': '涨跌额',
        'updown': '涨跌金额',

        'turnover_rate': '换手率',
        'amplitude': '振幅(%)',
        'floating_market_value': '流通市值',
        'total_market_value': '总市值',
        'p_e_ratio': '市盈率',
        'forward_pe': '动态市盈率',
        'pb_ratio': '市净率',

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

        'billboard_net_amt': '龙虎榜净买额',
        'billboard_buy_amt': '龙虎榜买入额',
        'billboard_sell_amt': '龙虎榜卖出额',
        'billboard_deal_amt': '龙虎榜成交额',
        'accum_amount': '市场总成交额',
        'deal_net_ratio': '净买额占总成交比',
        'deal_amount_ratio': '成交额占总成交比',
        'free_market_cap': '流通市值',
        'explanation': '上榜原因',
        'explain': '解读',

        'main_force_net_inflow': '主力净流入',
        'small_order_net_inflow': '小单净流入',
        'medium_order_net_inflow': '中单净流入',
        'large_order_net_inflow': '大单净流入',
        'extra_large_order_net_inflow': '超大单净流入',

        'announcement_date': '公告日',  # 公告日
        'EPS': '每股收益',  # earnings_per_share 每股收益
        'operating_revenue': '营业收入',  # 营业收入
        'YoY_operating_revenue': '营业收入去年同期',  # 营业收入去年同期
        'net_profit': '净利润',  # 净利润
        'YoY_net_profit': '净利润去年同期',  # 净利润去年同期
        'BVPS': '每股净资产',  # book_value_per_share 每股净资产
        'ROE': '净资产收益率',  # return_on_equity 净资产收益率
        'revenue_growth_YoY': '营业收入同比',  # 营业收入同比
        'net_profit_growth_YoY': '净利润同比',  # 净利润同比
        'revenue_growth_QoQ': '营业收入季度环比',  # 营业收入季度环比
        'net_profit_growth_QoQ': '净利润季度环比',  # 净利润季度环比
        'industry': '行业',  # 行业

        'forecasting_indicator': '预测指标',
        'earnings_variation': '业绩变动',
        'predictive_value': '预测数值',
        'variation_range': '变动幅度',
        'change_reason_explain': '变动原因',
        'predict_type': '预告类型',
        'YoY': '上年同期',

        'ANAPS': '调整每股净资产',  # adjusted_net_assets_per_share
        'CFPS': '每股现金流',  # cash_flow_per_share
        'APS': '每股公积金',  # accumulated per share
        'UDPS': '每股未分配利润',  # undistributed profit per share
        'TA': '总资产',  # Total Assets
        'NP_after_NDR': '扣非净利润',
        'MBPR': '主营利润率',
        'ROA': '总资产净利率',
        'net_sales_margin': '销售净利率',
        'ROE2': '净资产报酬率',
        'ROA2': '资产报酬率',
        'WAROE': '加权净资产收益率',
        'RPC': '成本费用利润率',
        'MCR': '主营业务成本率',
        'ART': '应收账款周转率',
        'ITR': '存货周转率',
        'FAT': '固定资产周转率',
        'TAT': '总资产周转率',
        'CATO': '流动资产周转率',
        'CR': '流动比率',
        'QR': '速动比率',
        'cash_ratio': '现金比率',
        'ER': '产权比率',
        'DAR': '资产负债率',
        'CFR': '现金流销售比',
        'CNPR': '现金流净利润比',
        'CFLR': '现金流负债比',
        'MRGR': '主营收入增长率',
        'NPGR': '净利润增长率',
        'NAGR': '净资产增长率',
        'TAGR': '总资产增长率',

        'is_st': '是否ST',
        'is_newly_issue': '是否次新',

        'suspended_date': "停牌时间",
        'suspended_deadline': "停牌截止时间",
        'suspended_period': "停牌期限",
        'suspended_reason': "停牌原因",
        'market': "所属市场",
        'suspended_beigin_date': "停牌开始日期",
        'suspended_end_date': "预计复牌时间",

        "is_trading_day": "是否为交易日",
        "is_now": "是否当日"
    }

    fund_dict = {
        'code': '基金代码',
        'short_name': '基金简称',
        'date': '日期',
        'NAV_per_unit': '单位净值',
        'cumulative_NAV': '累计净值',
        'percent': '涨跌幅',
        'stock_code': '股票代码',
        'stock_name': '股票简称',
        'pos_holding_prop': '持仓占比',
        'fund_inception_date': '成立日期',
        'new_NAV': '最新净值',
        'fund_company': '基金公司',
        'NAV_update_date': '净值更新日期',
        'func_comment': '简介',
        'industry_name': '行业名称',
        'portfolio_weight': '持仓比例',
        'announcement_date': '公布日期',
        'market_value': '市值',
    }