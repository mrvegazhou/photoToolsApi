# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
from stock_app.service.base_strategy import BaseStrategy
import pandas as pd
from stock_app.model.day_trading import DayTrading


# 计算日涨跌幅
def statistics_all_stock_day_trading(start_date, end_date):
    all_stocks = BaseStrategy.get_all_stocks()
    frames = []
    # count = 1
    for item in all_stocks:
        try:
            df = BaseStrategy.get_stock_special_indicators(item.code, start_date, end_date)
            df['code'] = item.code
            # df = get_KDJ(get_MACD(df), plus=True)
            # today_date = pd.to_datetime(datetime.datetime.strptime("2021-05-11", '%Y-%m-%d').date())
            # new_df = df[(df['MACD_buy']==1) & (df['KDJ_buy']==1) & (df.index == today_date)]
            # if not new_df.empty:
            #     frames.append(new_df)
            # count = count + 1
            for index, row in df.iterrows():
                kwargs = {
                    'trading_date': index,
                    'stock_code': item.code,
                    'close_price': row['close'],
                    'high_price': row['high'],
                    'low_price': row['low'],
                    'open_price': row['open'],
                    'volume': row['volume'],
                    'outstanding_share': row['outstanding_share'],
                    'turnover': row['turnover'],
                    'chg_pct': row['chg_pct']
                }
                DayTrading.add_trading_info(item.code, **kwargs)
        except Exception:
            print("异常:", Exception)
    result = pd.concat(frames)
    print(result)





if __name__ == "__main__":
    # statistics_all_stock_day_trading("20100101", "20210511")

    code = "sh000001"
    # code = "sz300236"
    # code = "sz002555"
    start_date = "2021-01-01"
    end_date = "2021-05-14"
    # 测试指标
    df = BaseStrategy.get_stock_special_indicators(code, start_date, end_date)
    # print(talib.ADX(df['high'], df['low'], df['close'], timeperiod=14))
    # get_DMI(df)
    print(df)
    # all_stocks = get_all_stocks()
    # get_momentum_and_contrariam(all_stocks, df, start_date, end_date)



