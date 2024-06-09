# coding:utf8
import pandas as pd
from typing import List, Union
from jsonpath import jsonpath
from functools import partial
from multiprocessing.pool import ThreadPool
from ..config.stockDataConst import Constants, EastConfig
from .stockDataBase import StockDataBase
from ...common import session


class EastIntradayData(StockDataBase):
    """日内K线交易行情获取"""

    def __init__(self):
        super().__init__()
        self.stock_intraday_data_dict = EastConfig.stock_intraday_data_dict.value
        columns = list(self.stock_intraday_data_dict.keys())
        columns.insert(0, 'code')
        columns.insert(0, 'name')
        self._none_df = pd.DataFrame(columns=columns)

    @property
    def intraday_api(self) -> str:
        return Constants.INTRADY_DATA_URL.value

    def get_intraday_data(self, codes: Union[str, List[str]], begin: str = '19000101', end: str = '20500101',
                          interval: str = '101', ex_rights: int = 1):
        '''
        获取股票、ETF、债券的 K 线数据

        Parameters
        ----------
        codes : Union[str,List[str]]
            股票、债券代码 或者 代码构成的列表
        beg : str, optional
            开始日期，默认为 ``'19000101'`` ，表示 1900年1月1日
        end : str, optional
            结束日期，默认为 ``'20500101'`` ，表示 2050年1月1日
        interval : int, optional
            行情之间的时间间隔，默认为 ``101`` ，可选示例如下

            - ``1`` : 分钟
            - ``5`` : 5 分钟
            - ``15`` : 15 分钟
            - ``30`` : 30 分钟
            - ``60`` : 60 分钟
            - ``101`` : 日
            - ``102`` : 周
            - ``103`` : 月

        ex_rights : int, optional
            复权方式，默认为 ``1`` ，可选示例如下

            - ``0`` : 不复权
            - ``1`` : 前复权
            - ``2`` : 后复权
        '''
        if not codes:
            return self._none_df
        klt = '101'
        if interval == '1day':
            klt = '101'
        elif interval == '1week':
            klt = '102'
        elif interval == '1mon':
            klt = '103'
        elif interval == '60min':
            klt = '60'
        elif interval == '30min':
            klt = '30'
        elif interval == '15min':
            klt = '15'
        elif interval == '5min':
            klt = '5'
        elif interval == '1min':
            klt = '1'

        if isinstance(codes, str):
            return self._get_single_intraday_data(codes, begin, end, interval=klt, ex_rights=ex_rights)
        elif hasattr(codes, '__iter__'):
            codes = list(codes)
            return self._get_multi_intraday_data(codes, begin, end, interval=klt, ex_rights=ex_rights)

    def _get_single_intraday_data(self, code, begin, end, interval, ex_rights):
        code = self.get_code_id(code)
        if not code:
            return self._none_df
        fields = list(self.stock_intraday_data_dict.values())
        columns = list(self.stock_intraday_data_dict.keys())
        fields2 = ",".join(fields)
        params = (
            ('fields1', 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13'),
            ('fields2', fields2),
            ('beg', begin),
            ('end', end),
            ('rtntype', '6'),
            ('secid', code),
            ('klt', f'{interval}'),
            ('fqt', f'{ex_rights}'),
        )
        url = self.intraday_api
        json_response = self._session.get(
            url, headers=self._headers, params=params, verify=False
        ).json()
        klines = jsonpath(json_response, '$..klines[:]')
        if not klines:
            return self._none_df
        rows = [kline.split(',') for kline in klines]
        name = json_response['data']['name']
        code = code.split('.')[-1]
        df = pd.DataFrame(rows, columns=columns)
        df.insert(0, 'code', code)
        df.insert(0, 'name', name)
        return df

    def _get_multi_intraday_data(self, codes, begin, end, interval, ex_rights):
        with ThreadPool(processes=len(codes)) as pool:
            partial_func = partial(self._get_single_intraday_data, begin=begin, end=end, interval=interval,
                                   ex_rights=ex_rights)
            res = pool.map(partial_func, codes)
        if not res or len(res) <= 0:
            return pd.DataFrame([], columns=self.columns)
        else:
            return pd.concat(res, axis=0, ignore_index=True)
