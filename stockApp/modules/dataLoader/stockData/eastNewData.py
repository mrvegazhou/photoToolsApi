# -*- coding: utf-8 -*-
import pandas as pd
from .stockDataBase import StockDataBase
from ..config.stockDataConst import Constants, EastConfig

class EastNewData(StockDataBase):

    @property
    def stock_api(self) -> str:
        return Constants.NEW_OR_ST_STOCKS_URL.value

    def get_new_data(self) -> pd.DataFrame:
        data_json = self.fetch_stock_data()
        return self.format_response_data(data_json)

    def fetch_stock_data(self):
        params = {
            'pn': '1',
            'pz': '2000',
            'po': '1',
            'np': '1',
            'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
            'fltt': '2',
            'invt': '2',
            'fid': 'f26',
            'fs': 'm:0 f:8,m:1 f:8',
            'fields': 'f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152',
            '_': '1631107510188',
        }
        r = self._session.get(EastNewData.stock_api, params=params)
        data_json = r.json()
        return data_json['data']['diff']

    def format_response_data(self, data_json) -> pd.DataFrame:
        temp_df = pd.DataFrame(data_json)
        temp_df.reset_index(inplace=True)
        temp_df['index'] = range(1, len(temp_df) + 1)
        temp_df.columns = [
            'index',
            'close',
            'percent',
            'price_change',
            'volume',
            'turnover',
            'amplitude',
            'turnover_rate',
            'forward_pe',
            'volume_ratio',
            '_',
            'code',
            '_',
            'name',
            'high_price',
            'low_price',
            'open',
            'yesterday_close',
            '_',
            '_',
            '_',
            'pb_ratio',
            '_',
            '_',
            '_',
            '_',
            '_',
            '_',
            '_',
            '_',
            '_',
        ]
        list_column = EastConfig.new_st_stock_info_dict.value.keys()
        temp_df = temp_df[list_column]
        temp_df['close'] = pd.to_numeric(temp_df['close'], errors="coerce")
        temp_df['percent'] = pd.to_numeric(temp_df['percent'], errors="coerce")
        temp_df['price_change'] = pd.to_numeric(temp_df['price_change'], errors="coerce")
        temp_df['volume'] = pd.to_numeric(temp_df['volume'], errors="coerce")
        temp_df['turnover'] = pd.to_numeric(temp_df['turnover'], errors="coerce")
        temp_df['amplitude'] = pd.to_numeric(temp_df['amplitude'], errors="coerce")
        temp_df['high_price'] = pd.to_numeric(temp_df['high_price'], errors="coerce")
        temp_df['low_price'] = pd.to_numeric(temp_df['low_price'], errors="coerce")
        temp_df['open'] = pd.to_numeric(temp_df['open'], errors="coerce")
        temp_df['volume_ratio'] = pd.to_numeric(temp_df['volume_ratio'], errors="coerce")
        temp_df['turnover_rate'] = pd.to_numeric(temp_df['turnover_rate'], errors="coerce")
        return temp_df