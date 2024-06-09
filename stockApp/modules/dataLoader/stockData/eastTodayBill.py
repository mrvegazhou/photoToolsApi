# coding:utf8
import pandas as pd
from typing import List
from jsonpath import jsonpath
from modules.dataLoader.config.stockDataConst import Constants, EastConfig
from .stockDataBase import StockDataBase
from modules.common import session


class EastTodayBill(StockDataBase):
    '''
    股票最新一个交易日单子流入数据(分钟级)
    '''
    def __init__(self):
        super().__init__()
        self._stock_today_bill_dict = EastConfig.today_bill_dict.value
        columns = list(self._stock_today_bill_dict.keys())
        self.columns = columns.copy()
        columns.insert(0, 'code')
        columns.insert(0, 'name')
        self._none_df = pd.DataFrame(columns=columns)

    @property
    def today_bill_api(self) -> str:
        return Constants.TODAY_BILL_URL.value

    def get_today_bill(self, code):
        if not code:
            return self._none_df
        res = self._fetch_today_bill_data(code)
        return self._format_today_bill_data(code, res)

    def _fetch_today_bill_data(self, code):
        quote_id = self.get_code_id(code)
        params = (
            ('lmt', '0'),
            ('klt', '1'),
            ('secid', quote_id),
            ('fields1', 'f1,f2,f3,f7'),
            ('fields2', 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63'),
        )
        json_response = session.get(
            self.today_bill_api, headers=self._headers, params=params
        ).json()
        return json_response

    def _format_today_bill_data(self, code, res):
        name = jsonpath(res, '$..name')[0]
        klines: List[str] = jsonpath(res, '$..klines[:]')
        if not klines:
            return self._none_df
        rows = [kline.split(',') for kline in klines]
        df = pd.DataFrame(rows, columns=self.columns)
        df.insert(0, 'code', code)
        df.insert(0, 'name', name)
        return df