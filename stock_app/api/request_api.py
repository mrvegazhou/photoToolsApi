# -*- coding: utf-8 -*-
import akshare as ak


# 获取股票代码和名称
def api_stock_info():
    return ak.stock_zh_a_spot()


# 获取股票基本指标：市盈率, 市净率, 股息率
def api_stock_base_indicator(code):
    code = code[2:]
    return ak.stock_a_lg_indicator(stock=code)


# 获取股票日交易信息
def api_stock_day_trading_info(code, start_date, end_date):
    return ak.stock_zh_a_daily(symbol=code, start_date=start_date, end_date=end_date, adjust="qfq")