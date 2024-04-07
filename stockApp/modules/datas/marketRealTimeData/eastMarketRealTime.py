# coding:utf8
import re
import time
import pandas as pd
from .marketRealTimeBase import MarketRealTimeBase
from modules.datas.config.stockDataConst import Constants, EastConfig
from config.mainConst import StockDict

"""各组合行情获取"""
class EastMarketRealTime(MarketRealTimeBase):

    @property
    def stock_api(self) -> str:
        return Constants.MARKET_REAL_TIME_URL.value

    def fetch_stock_data(self, code):
        main_market_dict = StockDict.market_dict.value
        flipped_market_dict = {v: k for k, v in main_market_dict.items()}
        if code not in flipped_market_dict and code not in main_market_dict:
            return []
        market_key = flipped_market_dict[code]

        east_market_dict = EastConfig.market_dict.value
        trade_detail_dict = EastConfig.stock_real_time_dict.value

        fs = east_market_dict[market_key]
        fields = ",".join(trade_detail_dict.values())
        params = (
            ('pn', '1'),
            ('pz', '1000000'),
            ('po', '1'),
            ('np', '1'),
            ('fltt', '2'),
            ('invt', '2'),
            ('fid', 'f3'),
            ('fs', fs),
            ('fields', fields)
        )
        json_response = self._session.get(self.stock_api, headers=EastConfig.request_header.value, params=params).json()
        return json_response['data']['diff']

    def format_response_data(self, rep_data, **kwargs):
        const_trade_detail_dict = EastConfig.stock_real_time_dict.value
        if rep_data:
            flipped_trade_detail_dict = {v: k for k, v in const_trade_detail_dict.items()}
            df = pd.DataFrame(rep_data)
            df = df.rename(columns=flipped_trade_detail_dict)
            date = pd.to_datetime(df['date'], unit='s', errors='coerce')
            if df['date'].isna().any():
                df['time'] = pd.NA
                df['date'] = pd.NA
            else:
                df['date'] = date.dt.strftime('%Y-%m-%d')
                df['time'] = date.dt.strftime('%H:%M:%S')
            df.index.name = 'code'
            df.set_index('code', inplace=True)
        else:
            df = pd.DataFrame(columns=const_trade_detail_dict.keys())
            df.index.name = 'code'
            df.set_index('code', inplace=True)
        return df