# -*- coding: utf-8 -*-
import sys, os, inspect
PACKAGE_PARENT = '../../../'
SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(inspect.getfile(inspect.currentframe())))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
import pandas as pd
from core.log.logger import get_module_logger
from core import app
from stockApp.modules.dataLoader.stockData.eastMarketRealTime import EastMarketRealTime
from stockApp.modules.dataLoader.stockData.eastSTData import EastSTData
from stockApp.modules.dataLoader.stockData.sinaNewlyIssuedData import SinaNewlyIssuedData
from stockApp.modules.dataLoader.stockData.eastSuspendedData import EastSuspendedData
from stockApp.modules.dataLoader.stockData.eastDetailInfo import EastDetailInfo
from stockApp.modules.common.time import get_now_date
from stockApp.dao.stockInfo import StockInfo


class StockInfoService(object):

    @staticmethod
    def get_remote_stocks_codes():
        # 所有股票
        all_stock_data = EastMarketRealTime()
        all_stocks_df = all_stock_data.get_market_real_time('沪深A')
        all_stocks_df.index.name = 'index'

        # st股票
        st_stock_data = EastSTData()
        st_stocks_df = st_stock_data.get_st_data()
        st_stocks_df.index.name = 'index'

        intersection = pd.merge(all_stocks_df, st_stocks_df, on='code', how='inner')
        all_stocks_df['is_st'] = 0
        all_stocks_df.loc[all_stocks_df['code'].isin(intersection['code']), 'is_st'] = 1

        # 次新股
        new_stock_data = SinaNewlyIssuedData()
        new_stock_df = new_stock_data.get_newly_issued_data()
        new_stock_df.index.name = 'index'

        all_stocks_df['is_newly_issued'] = 0
        intersection = pd.merge(all_stocks_df, new_stock_df, on='code', how='inner')
        all_stocks_df.loc[all_stocks_df['code'].isin(intersection['code']), 'is_newly_issued'] = 1

        # 停牌
        suspended_stock_data = EastSuspendedData()
        suspended_stock_df = suspended_stock_data.get_suspended_data(get_now_date())
        suspended_stock_df.index.name = 'index'

        all_stocks_df['is_suspended'] = 0
        intersection = pd.merge(all_stocks_df, suspended_stock_df, on='code', how='inner')
        all_stocks_df.loc[all_stocks_df['code'].isin(intersection['code']), 'is_suspended'] = 1

        return all_stocks_df

    @staticmethod
    def save_remote_stocks_list(all_stocks_df):
        # 清除当前股票数据
        with app.app_context():
            StockInfo.clear_stock_list()

        objs = []
        for idx, row in all_stocks_df.iterrows():
            obj = StockInfo()
            obj.code = row['code']
            obj.name = row['name']
            obj.is_st = row['is_st']
            obj.is_suspended = row['is_suspended']
            obj.is_newly_issued = row['is_newly_issued']

            # 股票详情
            detail_info = EastDetailInfo()
            detail_info_df = detail_info.get_stock_detail_info(row['code'])
            if not detail_info_df.empty:
                total_market_value = detail_info_df.loc[detail_info_df['item'] == 'total_market_value', 'value'].values[0]
                obj.total_market_value = total_market_value if isinstance(total_market_value, (int, float)) else 0

                floating_market_value = detail_info_df.loc[detail_info_df['item'] == 'floating_market_value', 'value'].values[0]
                obj.floating_market_value = floating_market_value if isinstance(floating_market_value, (int, float)) else 0

                total_share_capital = detail_info_df.loc[detail_info_df['item'] == 'total_share_capital', 'value'].values[0]
                obj.total_share_capital = total_share_capital if isinstance(total_share_capital, (int, float)) else 0

                floating_shares = detail_info_df.loc[detail_info_df['item'] == 'floating_shares', 'value'].values[0]
                obj.floating_shares = floating_shares if isinstance(floating_shares, (int, float)) else 0

                obj.IPO_date = detail_info_df.loc[detail_info_df['item'] == 'IPO_date', 'value'].values[0]
                obj.industry = detail_info_df.loc[detail_info_df['item'] == 'industry', 'value'].values[0]

                # objs.append(obj)

            with app.app_context():
                # res = StockInfo.add_new_stock_list(objs)
                res = StockInfo.add_new_stock(obj)
                print(res, "===res===")


    @staticmethod
    def get_local_stocks_codes():
        pass


if __name__ == '__main__':

    import json
    with app.app_context():
        json_string = '{"uuid": null, "name": "\u8054\u5efa\u5149\u7535", "code": "300269", "is_st": 1, "is_suspended": 1,"is_newly_issued": 1, "total_market_value": 12345678901234567890.1234567890, "floating_market_value": 14299999999999994541318.129000000000000000000000009999,"total_share_capital": 14299999999999994541318.129000000000000000000000009999, "floating_shares":14299999999999994541318.129000000000000000000000009999, "IPO_date": "2011-10-12"}'
        data = json.loads(json_string)
        info = StockInfo()
        info.uuid = data['uuid']
        info.name = data['name']
        info.code = data['code']
        info.is_st = data['is_st']
        info.is_suspended = data['is_suspended']
        info.is_newly_issued = data['is_newly_issued']
        info.total_market_value = data['total_market_value']
        info.floating_market_value = data['floating_market_value']
        info.total_share_capital = data['total_share_capital']
        info.floating_shares = data['floating_shares']
        info.IPO_date = data['IPO_date']
        objs = [info]
        res = StockInfo.add_new_stock_list(objs)
        print(res)