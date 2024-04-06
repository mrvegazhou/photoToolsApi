# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
import akshare as ak
import baostock as bs
import pandas as pd
import re
import demjson
from stock_app.api.spider.spider_stock_finance import spider_stock_capital, spider_sz50


# 获取股票代码和名称
def api_stock_info():
    try:
        return ak.stock_zh_a_spot()
    except demjson.JSONDecodeError:
        return pd.DataFrame()


# 获取股票基本指标：市盈率, 市净率, 股息率
def api_stock_base_indicator(code):
    code = code[2:]
    return ak.stock_a_lg_indicator(stock=code)


# 获取股票日交易信息
def api_stock_day_trading_info(code, start_date, end_date):
    try:
        return ak.stock_zh_a_daily(symbol=code, start_date=start_date, end_date=end_date, adjust="qfq")
    except demjson.JSONDecodeError:
        return pd.DataFrame()

# 财务报表
def api_stock_financial_report(code):
    return ak.stock_financial_report_sina(stock=code)


# 财务摘要
def api_stock_financial_abstract(code):
    return ak.stock_financial_abstract(stock=code)


# 财务指标
def api_stock_financial_analysis_indicator(code, year=None, quarter=None):
    df = ak.stock_financial_analysis_indicator(code)
    if df.empty:
        return pd.DataFrame()
    if year is None and quarter is None:
        return df
    else:
        df.index = pd.to_datetime(df.index)
        if df[df.index.year==year].empty:
            return pd.DataFrame()
        df = df[df.index.year==year].sort_index().reset_index()
        return df[df.index==(quarter-1)]



# 根据baostock接口，获取所有基本面信息
def api_all_fundamental_datas(code, year, quarter):
    try:
        lg = bs.login()
        # 季频财务数据信息
        rs_profit = api_query_profit_data(code=code, year=year, quarter=quarter)
        # 季频营运能力
        rs_operation = api_query_operation_data(code=code, year=year, quarter=quarter)
        # 季频成长能力
        rs_growth = api_query_growth_data(code=code, year=year, quarter=quarter)
        # 季频偿债能力
        rs_balance = api_query_balance_data(code=code, year=year, quarter=quarter)
        # 季频现金流量
        cash_flow_list = api_query_cash_flow_data(code=code, year=year, quarter=quarter)
        # 季频杜邦指数
        rs_dupont = api_query_dupont_data(code=code, year=year, quarter=quarter)
        # 合并报表
        return pd.concat([rs_profit, rs_operation, rs_growth, rs_balance, cash_flow_list, rs_dupont], axis=1)

    except Exception as e:
        print(e)
        print('login respond error_code:' + lg.error_code)
        print('login respond  error_msg:' + lg.error_msg)
    finally:
        bs.logout()


# baostock 季频财务数据信息
def api_query_profit_data(code="sh.600000", year=2017, quarter=2):
    profit_list = []
    rs_profit = bs.query_profit_data(code=code, year=year, quarter=quarter)
    while (rs_profit.error_code == '0') & rs_profit.next():
        profit_list.append(rs_profit.get_row_data())
    return pd.DataFrame(profit_list, columns=rs_profit.fields)


# baostock 季频营运能力
def api_query_operation_data(code="sh.600000", year=2017, quarter=2):
    # 营运能力
    operation_list = []
    rs_operation = bs.query_operation_data(code=code, year=year, quarter=quarter)
    while (rs_operation.error_code == '0') & rs_operation.next():
        operation_list.append(rs_operation.get_row_data())
    return pd.DataFrame(operation_list, columns=rs_operation.fields)


# baostock 季频成长能力
def api_query_growth_data(code="sh.600000", year=2017, quarter=2):
    # 成长能力
    growth_list = []
    rs_growth = bs.query_growth_data(code=code, year=year, quarter=quarter)
    while (rs_growth.error_code == '0') & rs_growth.next():
        growth_list.append(rs_growth.get_row_data())
    return pd.DataFrame(growth_list, columns=rs_growth.fields)


# baostock 季频偿债能力
def api_query_balance_data(code="sh.600000", year=2017, quarter=2):
    # 偿债能力
    balance_list = []
    rs_balance = bs.query_balance_data(code=code, year=year, quarter=quarter)
    while (rs_balance.error_code == '0') & rs_balance.next():
        balance_list.append(rs_balance.get_row_data())
    return pd.DataFrame(balance_list, columns=rs_balance.fields)


# baostock 季频现金流量
def api_query_cash_flow_data(code="sh.600000", year=2017, quarter=2):
    # 季频现金流量
    cash_flow_list = []
    rs_cash_flow = bs.query_cash_flow_data(code=code, year=year, quarter=quarter)
    while (rs_cash_flow.error_code == '0') & rs_cash_flow.next():
        cash_flow_list.append(rs_cash_flow.get_row_data())
    return pd.DataFrame(cash_flow_list, columns=rs_cash_flow.fields)


# baostock 季频杜邦指数
def api_query_dupont_data(code="sh.600000", year=2017, quarter=2):
    # 查询杜邦指数
    dupont_list = []
    rs_dupont = bs.query_dupont_data(code=code, year=year, quarter=quarter)
    while (rs_dupont.error_code == '0') & rs_dupont.next():
        dupont_list.append(rs_dupont.get_row_data())
    return pd.DataFrame(dupont_list, columns=rs_dupont.fields)


# baostock 查询季频公司报告信息
def api_query_performance_express_report(code, start_date, end_date):
    try:
        lg = bs.login()

        #### 获取公司业绩快报 ####
        rs = bs.query_performance_express_report(code, start_date=start_date, end_date=end_date)
        print('query_performance_express_report respond error_code:' + rs.error_code)
        print('query_performance_express_report respond  error_msg:' + rs.error_msg)

        result_list = []
        while (rs.error_code == '0') & rs.next():
            result_list.append(rs.get_row_data())
            # 获取一条记录，将记录合并在一起
        return pd.DataFrame(result_list, columns=rs.fields)

    except Exception as e:
        print(e)
        print('login respond error_code:' + lg.error_code)
        print('login respond  error_msg:' + lg.error_msg)
    finally:
        bs.logout()


# baostock 季频公司业绩预告
def api_query_forecast_report(code, start_date, end_date):
    try:
        lg = bs.login()

        #### 获取公司业绩预告 ####
        rs_forecast = bs.query_forecast_report(code, start_date=start_date, end_date=end_date)
        print('query_forecast_reprot respond error_code:' + rs_forecast.error_code)
        print('query_forecast_reprot respond  error_msg:' + rs_forecast.error_msg)
        rs_forecast_list = []
        while (rs_forecast.error_code == '0') & rs_forecast.next():
            # 分页查询，将每页信息合并在一起
            rs_forecast_list.append(rs_forecast.get_row_data())
        return pd.DataFrame(rs_forecast_list, columns=rs_forecast.fields)

    except Exception as e:
        print(e)
        print('login respond error_code:' + lg.error_code)
        print('login respond  error_msg:' + lg.error_msg)
    finally:
        bs.logout()



# baostock 按日历史A股K线数据
def api_stock_day_trading_info2(code, type, start_date, end_date):
    try:
        lg = bs.login()

        #### 获取沪深A股历史K线数据 ####
        # 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。“分钟线”不包含指数。
        # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
        # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
        rs = bs.query_history_k_data_plus(code,
                                          "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                          start_date=start_date, end_date=end_date,
                                          frequency=type, adjustflag="3") #复权状态(1：后复权， 2：前复权，3：不复权）
        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())
        return pd.DataFrame(data_list, columns=rs.fields)

    except Exception as e:
        print(e)
        print('login respond error_code:' + lg.error_code)
        print('login respond  error_msg:' + lg.error_msg)
    finally:
        bs.logout()

# baostock 按日历史A股K线数据 批量登录
def api_stock_day_trading_info2_nologin(code, type, start_date, end_date):
    #### 获取沪深A股历史K线数据 ####
    # 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。“分钟线”不包含指数。
    # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
    # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
    rs = bs.query_history_k_data_plus(code,
                                      "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                      start_date=start_date, end_date=end_date,
                                      frequency=type, adjustflag="3")  # 复权状态(1：后复权， 2：前复权，3：不复权）
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    return pd.DataFrame(data_list, columns=rs.fields)


# baostock 上证50股票
def api_sz50_stock():
    try:
        lg = bs.login()
        rs = bs.query_sz50_stocks()
        sz50_stocks = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            sz50_stocks.append(rs.get_row_data())
        result = pd.DataFrame(sz50_stocks, columns=rs.fields)
        return result
    except Exception as e:
        print(e)
        print('login respond error_code:' + lg.error_code)
        print('login respond  error_msg:' + lg.error_msg)
    finally:
        bs.logout()


# spider a股流通A股(亿股)
def api_stock_a_capital_total(code):
    try:
        code = re.findall(r"\d+", code)[0]
        return spider_stock_capital(code)
    except Exception as e:
        return None, None


def api_sz50_stock_by_year_season(year, season=1):
    return spider_sz50(year, season)

# spider sz50交易信息
def api_sz50_stock_trading_info(start_date, end_date):
    try:
        start_date_arr = start_date.split('-')
        start_year = int(start_date_arr[0])

        end_date_arr = end_date.split('-')
        end_year = int(end_date_arr[0])

        diff_year = end_year - start_year + 1
        ret_list = []
        if diff_year==0:
            for season in range(1, 5):
                df = spider_sz50(start_year, season)
                if not df.empty:
                    ret_list.append(df)
        else:
            for i in range(0, diff_year):
                for season in range(1, 5):
                    df = spider_sz50(start_year+i, season)
                    if not df.empty:
                        ret_list.append(df)
        return pd.concat(ret_list, axis=0)
    except Exception as e:
        return None



if __name__ == "__main__":
    capital_df, col = api_stock_a_capital_total("600015")
    print(capital_df.at[0, col])
