# -*- coding: utf-8 -*-
import math
import pandas as pd
from .stockDataBase import StockDataBase
from ..config.stockDataConst import Constants, SinaConfig


class SinaNewlyIssuedData(StockDataBase):
    @property
    def stock_api(self) -> str:
        return f"{Constants.NEWLY_ISSUED_URL.value}getHQNodeStockCount"

    def get_newly_issued_data(self) -> pd.DataFrame:
        data_json = self._fetch_stock_data()
        return self._format_response_data(data_json)

    def _fetch_stock_data(self):
        params = {"node": "new_stock"}
        r = self._session.get(self.stock_api, params=params)
        total_page = math.ceil(int(r.json()) / 80)
        url = f"{Constants.NEWLY_ISSUED_URL.value}getHQNodeData"
        big_df = pd.DataFrame()
        for page in range(1, total_page + 1):
            params = {
                "page": str(page),
                "num": "80",
                "sort": "symbol",
                "asc": "1",
                "node": "new_stock",
                "symbol": "",
                "_s_r_a": "page",
            }
            r = self._session.get(url, params=params)
            r.encoding = "gb2312"
            data_json = r.json()
            temp_df = pd.DataFrame(data_json)
            big_df = pd.concat([big_df, temp_df], ignore_index=True)

        return big_df

    def _format_response_data(self, big_df) -> pd.DataFrame:
        list_column = SinaConfig.new_stock_info_dict.value
        flipped_const_new_stock_info_dict = {value: key for key, value in list_column.items()}
        big_df = big_df[
            list_column.values()
        ]
        big_df = big_df.rename(columns=flipped_const_new_stock_info_dict)
        big_df['open'] = pd.to_numeric(big_df['open'])
        big_df['high_price'] = pd.to_numeric(big_df['high_price'])
        big_df['low_price'] = pd.to_numeric(big_df['low_price'])
        big_df.set_index('code', inplace=True, drop=False)
        return big_df