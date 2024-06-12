# -*- coding: utf-8 -*-
import sys, os, inspect
PACKAGE_PARENT = '../../../'
SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(inspect.getfile(inspect.currentframe())))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
import pandas as pd
from datetime import datetime, timedelta
from stockApp import app
from stockApp.modules.dataLoader.stockData.eastMarketRealTime import EastMarketRealTime
from stockApp.modules.dataLoader.stockData.eastIntradayData import EastIntradayData
from stockApp.modules.dataLoader.stockData.tradingDate import TradingDate
from stockApp.dao.dayTrading import DayTrading


class DayTradingService(object):

    @staticmethod
    def get_remote_day_trading_data(begin_date: str = '20230101', end_date: str = '20240605'):
        # 获取股票列表
        all_stock_data = EastMarketRealTime()
        all_stocks_df = all_stock_data.get_market_real_time('沪深A')
        intraday = EastIntradayData()
        for idx, row in all_stocks_df.iterrows():
            code = row['code']
            # 默认后复权
            intraday_df = intraday.get_intraday_data(code, begin_date, end_date, ex_rights=2)
            intraday_df = intraday_df.set_index("date", drop=False).sort_index()
            unadjusted_df = intraday.get_intraday_data(code, begin_date, end_date, ex_rights=0)
            unadjusted_df = unadjusted_df.set_index("date", drop=False).sort_index()
            intraday_df['adj_factor'] = (intraday_df['open'].astype(float) / unadjusted_df['open'].astype(float)).round(2)
            intrady_item_list = []
            for i, intrady_item in intraday_df.iterrows():
                intrady_dict = {
                    'code': code,
                    'trading_date': intrady_item['date'],
                    'close': intrady_item['close'],
                    'open': intrady_item['open'],
                    'high_price': intrady_item['high_price'],
                    'low_price': intrady_item['low_price'],
                    'turnover': intrady_item['turnover'],
                    'turnover_rate': intrady_item['turnover_rate'],
                    'volume': intrady_item['volume'],
                    'amplitude': intrady_item['amplitude'],
                    'change': intrady_item['change'],
                    'price_change': intrady_item['price_change'],
                    'adj_factor': intrady_item['adj_factor']
                }
                intrady_item_list.append(intrady_dict)
            res = DayTrading.add_trading_list(intrady_item_list)

    @staticmethod
    def get_recent_trading_date():
        td = TradingDate()
        df = td.get_stock_trading_date_list()
        today = datetime.today()
        now = today.strftime('%Y%m%d')
        exists = now in df['trade_date'].astype(str).values
        if exists:
            return now

        date_found = False
        while not date_found:
            if now in df['trade_date'].astype(str).values:
                date_found = True
            else:
                # 如果当前日期不在列中，获取上一天的日期
                today -= timedelta(days=1)
                now = today.strftime('%Y%m%d')
        return now

    @staticmethod
    def get_feature_percen_datas(code, start_date, end_date) -> pd.DataFrame:
        # 获取日期范围内涨跌幅数据
        datas = DayTrading.get_stock_trading_list_by_SQL(code, start_date, end_date)
        pd.DataFrame.from_dict(datas, orient='records')['change', 'high_price', 'low_price', 'close', 'open', 'volume']



if __name__ == '__main__':
    with app.app_context():
    #     DayTrading.create_tables()
        DayTradingService.get_remote_day_trading_data()

