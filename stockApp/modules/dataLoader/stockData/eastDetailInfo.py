# -*- coding: utf-8 -*-
import pandas as pd
from .stockDataBase import StockDataBase
from ..config.stockDataConst import Constants, EastConfig


class EastDetailInfo(StockDataBase):

    @property
    def stock_api(self) -> str:
        return Constants.FULL_REAL_TIME_EAST_MONEY_URL.value

    def get_stock_detail_info(self, stock_code, timeout: float = None) -> pd.DataFrame:
        secid = self.get_code_id(stock_code)
        data_json = self._fetch_stock_data(secid, timeout)
        return self._format_response_data(data_json)

    def _fetch_stock_data(self, stock_code, timeout):
        try:
            params = {
                "ut": "fa5fd1943c7b386f172d6893dbfba10b",
                "fltt": "2",
                "invt": "2",
                "fields": "f120,f121,f122,f174,f175,f59,f163,f43,f57,f58,f169,f170,f46,f44,f51,f168,f47,f164,f116,f60,f45,f52,f50,f48,f167,f117,f71,f161,f49,f530,f135,f136,f137,f138,f139,f141,f142,f144,f145,f147,f148,f140,f143,f146,f149,f55,f62,f162,f92,f173,f104,f105,f84,f85,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f107,f111,f86,f177,f78,f110,f262,f263,f264,f267,f268,f255,f256,f257,f258,f127,f199,f128,f198,f259,f260,f261,f171,f277,f278,f279,f288,f152,f250,f251,f252,f253,f254,f269,f270,f271,f272,f273,f274,f275,f276,f265,f266,f289,f290,f286,f285,f292,f293,f294,f295",
                "secid": f"{stock_code}",
                "_": "1640157544804",
            }
            r = self._session.get(self.stock_api, params=params, timeout=timeout)
            return r.json()
        except Exception as e:
            return ""

    def _format_if_date(self, row):
        if row['item'] == 'IPO_date':
            value_str = str(row['value'])
            # 移除 '-' 并尝试转换
            value_str = value_str.replace('-', '')
            if not value_str:
                return "1900-01-01"
            return pd.to_datetime(value_str, format='%Y%m%d').strftime('%Y-%m-%d')
        return row['value']

    def _format_response_data(self, data_json) -> pd.DataFrame:
        if not data_json:
            return pd.DataFrame(columns=['item', 'value'])
        temp_df = pd.DataFrame(data_json)
        temp_df.reset_index(inplace=True)
        del temp_df["rc"]
        del temp_df["rt"]
        del temp_df["svr"]
        del temp_df["lt"]
        del temp_df["full"]
        detail_info_dict = EastConfig.detail_info_dict.value
        flipped_const_detail_info_dict = {value: key for key, value in detail_info_dict.items()}
        temp_df["index"] = temp_df["index"].map(flipped_const_detail_info_dict)
        temp_df = temp_df[pd.notna(temp_df["index"])]
        if "dlmkts" in temp_df.columns:
            del temp_df["dlmkts"]
        temp_df.columns = [
            "item",
            "value",
        ]
        temp_df['value'] = temp_df.apply(self._format_if_date, axis=1)
        temp_df.reset_index(inplace=True, drop=True)
        return temp_df

