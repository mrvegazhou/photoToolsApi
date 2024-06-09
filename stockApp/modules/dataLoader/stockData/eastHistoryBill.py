# coding:utf8
import pandas as pd
from typing import List
from jsonpath import jsonpath
from modules.dataLoader.config.stockDataConst import Constants, EastConfig
from .stockDataBase import StockDataBase


class EastHistoryBill(StockDataBase):
    '''
    股票最新一个交易日单子流入数据(分钟级)
    '''

    def __init__(self):
        super().__init__()
        self._stock_history_bill_dict = EastConfig.history_bill_dict.value
        columns = list(self._stock_history_bill_dict.keys())
        self.columns = columns.copy()
        columns.insert(0, 'code')
        columns.insert(0, 'name')
        self._none_df = pd.DataFrame(columns=columns)

    @property
    def history_bill_api(self) -> str:
        return Constants.HISTORY_BILL_URL.value

    def get_history_bill(self, code):
        if not code:
            return self._none_df
        res = self._fetch_history_bill_data(code)
        return self._format_history_bill_data(code, res)

    def _fetch_history_bill_data(self, code):
        fields = self._stock_history_bill_dict.values()
        code_id = self.get_code_id(code)
        params = (
            ('lmt', '100000'),
            ('klt', '101'),
            ('secid', code_id),
            ('fields1', 'f1,f2,f3,f7'),
            ('fields2', ",".join(fields)),
        )
        json_response = self._session.get(
            self.history_bill_api, headers=self._headers, params=params
        ).json()
        return json_response

    def _format_history_bill_data(self, code, json_response):
        klines: List[str] = jsonpath(json_response, '$..klines[:]')
        if not klines:
            return self._none_df
        rows = [kline.split(',') for kline in klines]
        name = jsonpath(json_response, '$..name')[0]
        df = pd.DataFrame(rows, columns=self.columns)
        df.insert(0, 'code', code)
        df.insert(0, 'name', name)
        return df