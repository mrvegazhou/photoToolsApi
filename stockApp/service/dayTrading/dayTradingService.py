# -*- coding: utf-8 -*-
import sys, os, inspect
from decimal import Decimal

PACKAGE_PARENT = '../../../'
SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(inspect.getfile(inspect.currentframe())))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from stockApp import app
from stockApp.modules.dataLoader.stockData.eastMarketRealTime import EastMarketRealTime
from stockApp.modules.dataLoader.stockData.eastIntradayData import EastIntradayData
from stockApp.modules.dataLoader.stockData.tradingDate import TradingDate
from stockApp.dao.dayTrading import DayTrading
from stockApp.modules.dataHandler.normalize1d import Normalize1d
from stockApp.service.strategies.baseStrategy import BaseStrategy
from core.log.logger import get_module_logger
from stockApp.__init__ import utils

logger = get_module_logger("DayTradingService")


class DayTradingService(object):

    @staticmethod
    def get_remote_day_trading_data(begin_date: str = '19991110', end_date: str = '19991125'):
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
            intraday_df["adj_factor"] = intraday_df["adj_factor"].fillna(method="ffill")
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
            print(intrady_item_list, "----intrady_item_list----")
            res = DayTrading.add_trading_list(intrady_item_list)
            print(res, "---res---")

    @staticmethod
    def get_recent_trading_date(date=None, shift=None):
        """
        获取交易日期

        Parameters
        ----------
        date: 指定日期
        shift: 比如滑动到前天的日期

        Return
        ------
        """
        td = TradingDate()
        df = td.get_stock_trading_date_list()
        if df.empty:
            return None

        common_util = utils['common']
        if date and not common_util.is_date(date):
            return None

        if not date:
            today = datetime.today()
            now = today.strftime('%Y-%m-%d')
        else:
            last_row = df.iloc[-1]
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
            if last_row.trading_date < date_obj:
                return None
            first_row = df.iloc[0]
            if first_row.trading_date > date_obj:
                return None
            now = date

        df['trading_date'] = pd.to_datetime(df['trading_date'])
        previous_rows = df[df['trading_date'] <= pd.to_datetime(now)]
        idx = previous_rows.index[-1]
        if shift:
            idx = shift + idx
            if idx < df.index[0] or idx > df.index[-1]:
                return None
        return df.iloc[idx]['trading_date'].strftime('%Y-%m-%d')

    @staticmethod
    def get_trading_dates(start_time: str, end_time: str) -> pd.DataFrame:
        td = TradingDate()
        df = td.get_stock_trading_date_list()
        start_date = pd.to_datetime(start_time)
        end_date = pd.to_datetime(end_time)
        return df[(df['trading_date'] >= start_date) & (df['trading_date'] <= end_date)]

    @classmethod
    def get_all_trading_dates(cls) -> pd.DataFrame:
        td = TradingDate()
        df = td.get_stock_trading_date_list()
        df.rename(columns={'trading_date': 'date'}, inplace=True)
        return df

    @classmethod
    def get_feature_datas(cls, code, start_date, end_date) -> pd.DataFrame:
        """
        获取股票的日交易列表 比如存储到hdf5

        Parameters
        ----------

        Return
        ------
        """
        # 获取日期范围内涨跌幅数据
        datas = DayTrading.get_stock_trading_list_by_SQL(code, start_date, end_date)
        column_names = ['code', 'open', 'close', 'high_price', 'low_price', 'volume', 'change', 'adj_factor', 'trading_date']
        if datas:
            df = pd.DataFrame.from_dict(datas, orient='columns')[column_names]
            df.rename(columns={'high_price': 'high', 'low_price': 'low', 'adj_factor': 'factor', 'trading_date': 'date'}, inplace=True)
            # 数据标准化
            df = Normalize1d.manual_adj_data(df)
            for col in df.columns:
                # 检查列的数据类型是否为'object'，因为decimal.Decimal在Pandas中通常被识别为object类型
                if df[col].dtype == 'object':
                    # 尝试将对象转换为Decimal，如果成功，则进一步转换为float
                    if all(isinstance(val, Decimal) for val in df[col] if not pd.isnull(val)):
                        df[col] = df[col].astype(float)
            # 判断是否为单调递增的
            if not df.index.is_monotonic_increasing:
                df.sort_index(inplace=True)
        else:
            df = pd.DataFrame(columns=column_names)

        df['vwap'] = BaseStrategy.vwap(df)
        return df


if __name__ == '__main__':
    with app.app_context():
        # dt = DayTrading()
        # print(dt.get_table('301567'))
    #     DayTrading.create_tables()
        print(DayTradingService.get_recent_trading_date(shift=-2))
    #     df = DayTradingService.get_feature_datas('301231', '2023-01-03', '2024-06-05')
    #     print(df)

