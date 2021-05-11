# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
from stock_app.__init__ import send, utils, current_app
from stock_app.model.day_trading import DayTrading
from stock_app.model.stock import Stock
from chinese_calendar import is_workday


def get_next_day(start_date):
    minus_days = 1
    next_day = utils["date"].skip_date(start_date, minus_days)
    while not is_workday(next_day):
        next_day = utils["date"].skip_date(next_day.strftime('%Y-%m-%d'), minus_days)
        minus_days = 1 + minus_days
    return next_day.strftime('%Y-%m-%d')


'''
start_date, end_date为2015-08-15格式
'''
def get_negative_include_positive(date):
    common_util = utils['common']
    if not common_util.is_date(date):
        return send(-1, data="", msg="日期格式错误")

    # 昨天
    start_date = get_next_day(date)

    # 昨天的昨天
    the_day_before_yesterday = get_next_day(start_date)

    result_codes = []

    # 查询出所有股票代码
    stock_obj = Stock()
    all_stock_codes = stock_obj.get_all_stock_codes()

    for stock in all_stock_codes:
        try:
            code = stock.code
            day_trading_list = DayTrading.get_stock_day_trading_info(code, the_day_before_yesterday, date)
            retry_count = 0
            while len(day_trading_list) < 3 and len(day_trading_list) != 0:
                the_day_before_yesterday = get_next_day(the_day_before_yesterday)
                day_trading_list = DayTrading.get_stock_day_trading_info(code, the_day_before_yesterday, date)
                retry_count = retry_count + 1
                if retry_count >= 10:
                    break

            # 只有三个交易才可以计算
            if len(day_trading_list) >= 3:
                # 前天
                close3 = day_trading_list[2].close_price
                # 昨天
                opens2 = day_trading_list[1].open_price
                close2 = day_trading_list[1].close_price
                p_change2 = (close2-close3)/close3 * 100
                # 今天
                opens1 = day_trading_list[0].open_price
                close1 = day_trading_list[0].close_price
                # 涨跌幅=(现价-上一个交易日收盘价)/上一个交易日收盘价*100%
                p_change1 = (close1-close2)/close2 * 100
                if opens2 < close1 and close2 > opens1 and p_change1 > 9.8 and p_change2 < -2:
                    result_codes.append(code)
        except:
            current_app.logger.error("股票异常：%s", code)

    print(result_codes)
    return result_codes

'''
验证阳包阴
'''
def test_negative_include_positive_rate(today_date):
    result_codes = get_negative_include_positive(today_date)
    for code in result_codes:
        obj = DayTrading()
        trading_list = obj.get_stock_all_day_trading(code)
        for i in range(0, len(trading_list)):
            try:
                date_str = trading_list[i].trading_date
                opens2 = float(trading_list[i].open_price)
                opens1 = float(trading_list[i + 1].open_price)
                close2 = float(trading_list[i].close_price)
                close1 = float(trading_list[i + 1].close_price)
                p_change1 = (close1-close2)/close2
                close3 = float(trading_list[i + 2].close_price)
                p_change2 = (close2-close3)/close3
                if opens2 < close1 and close2 > opens1 and p_change1 < -2 and p_change2 > 9.8:
                    if i - 6 > 0:
                        # 收益率
                        wins = (float(trading_list[i - 6][2]) - float(trading_list[i - 1][1])) / float(trading_list[i - 1][1]) * 100
                        print(wins)
                        print('%s的%s之后5天收率为百分之%d' % (code, date_str, wins))
                    else:
                        print('%s在%s之前没有满足条件的行情\n'%(code, date_str))
            except:
                pass




if __name__ == "__main__":
    get_negative_include_positive('2021-04-12')
    # code = 'sh600048'
    # DayTrading.get_stock_day_trading_info(code, '2010-02-01', '2020-03-12')
