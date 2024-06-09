# coding:utf8
import pandas as pd
from typing import List
from jsonpath import jsonpath
from datetime import datetime, timedelta
from tqdm.auto import tqdm
from modules.dataLoader.config.stockDataConst import Constants, EastConfig
from modules.common import session


class EastDailyBillBoard(object):

    def __init__(self):
        self._session = session
        self._headers = EastConfig.request_header.value
        self._stock_daily_bill_board_dict = EastConfig.daily_bill_board_dict.value
        self.columns = self._stock_daily_bill_board_dict.keys()
        self._none_df = pd.DataFrame(columns=self.columns)

    @property
    def daily_bill_board_api(self) -> str:
        return Constants.DAILY_BILL_BOARD_URL.value

    def get_daily_bill_board(self, start_date: str = None, end_date: str = None):
        '''
        获取龙虎榜
        Parameters
        --------------------------
        start_date : str, optional
            开始日期
            部分可选示例如下
            - ``None`` 最新一个榜单公开日(默认值)
            - ``"2021-08-27"`` 2021年8月27日
        end_date : str, optional
            结束日期
            部分可选示例如下
            - ``None`` 最新一个榜单公开日(默认值)
            - ``"2021-08-31"`` 2021年8月31日
        '''
        today = datetime.today().date()
        mode = 'auto'
        if start_date is None:
            start_date = today

        if end_date is None:
            end_date = today

        if isinstance(start_date, str):
            mode = 'user'
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if isinstance(end_date, str):
            mode = 'user'
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        fields = self._stock_daily_bill_board_dict
        flipped_fields = {v: k for k, v in fields.items()}
        bar: tqdm = None

        while 1:
            dfs: List[pd.DataFrame] = []
            page = 1
            while 1:
                params = (
                    ('sortColumns', 'TRADE_DATE,SECURITY_CODE'),
                    ('sortTypes', '-1,1'),
                    ('pageSize', '500'),
                    ('pageNumber', page),
                    ('reportName', 'RPT_DAILYBILLBOARD_DETAILS'),
                    ('columns', 'ALL'),
                    ('source', 'WEB'),
                    ('client', 'WEB'),
                    ('filter', f"(TRADE_DATE<='{end_date}')(TRADE_DATE>='{start_date}')"),
                )

                url = self.daily_bill_board_api

                response = session.get(url, params=params)
                if bar is None:
                    pages = jsonpath(response.json(), '$..pages')

                    if pages and pages[0] != 1:
                        total = pages[0]
                        bar = tqdm(total=int(total))
                if bar is not None:
                    bar.update()

                items = jsonpath(response.json(), '$..data[:]')
                if not items:
                    break
                page += 1
                df = pd.DataFrame(items).rename(columns=flipped_fields)[self.columns]
                dfs.append(df)

            if mode == 'user':
                break
            if len(dfs) == 0:
                start_date = start_date - timedelta(1)
                end_date = end_date - timedelta(1)

            if len(dfs) > 0:
                break

        if len(dfs) == 0:
            df = pd.DataFrame(columns=fields.values())
            return df

        df = pd.concat(dfs, ignore_index=True)
        df['date'] = df['date'].astype('str').apply(lambda x: x.split(' ')[0])
        return df

