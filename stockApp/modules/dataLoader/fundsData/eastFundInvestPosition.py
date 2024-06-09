# coding:utf8
import requests
from typing import Union, List
from jsonpath import jsonpath
import re
import pandas as pd
from modules.dataLoader.config.fundDataConst import Constants, EastConfig


"""基金持仓信息获取"""
class EastFundInvestPosition(object):

    def __init__(self):
        self._session = requests.session()

    def fund_invest_pos_api(self) -> str:
        """
        基金列表 api 地址
        """
        return Constants.FUNDS_CODES_URL.value

    def get_fund_invest_position(self, fund_code: str, dates: Union[str, List[str]] = None, **kwargs) -> pd.DataFrame:
        '''
        获取基金的持仓调用方法
        Parameters
        ----------
        fund_code : str
            基金代码
        dates : Union[str, List[str]], optional
            日期或者日期构成的列表
            可选示例如下
            - ``None`` : 最新公开日期
            - ``'2020-01-01'`` : 一个公开持仓日期
            - ``['2020-12-31' ,'2019-12-31']`` : 多个公开持仓日期
        '''
        if not isinstance(dates, List):
            dates = [dates]
        if dates is None:
            dates = [None]

        res = self._fetch_funds_codes_data(fund_code, dates)
        return self._format_funds_codes_resp_data(res, **kwargs)

    def _fetch_funds_codes_data(self, fund_code, dates):
        headers = EastConfig.fund_headers.value
        url = Constants.FUND_INVEST_POSITION_URL.value
        data_list = []
        for date in dates:
            params = [
                ('FCODE', fund_code),
                ('appType', 'ttjj'),
                ('deviceid', '3EA024C2-7F22-408B-95E4-383D38160FB3'),
                ('plat', 'Iphone'),
                ('product', 'EFund'),
                ('serverVersion', '6.2.8'),
                ('version', '6.2.8'),
            ]
            if date is not None:
                params.append(('DATE', date))
            json_response = self._session.get(
                url, headers=headers, params=params
            ).json()
            stocks = jsonpath(json_response, '$..fundStocks[:]')
            if not stocks:
                continue
            date = json_response['Expansion']
            data_list = data_list + [{**stock, 'date': date, 'fund_code': fund_code} for stock in stocks]
        return data_list

    def _format_funds_codes_resp_data(self, rep_data, **kwargs):
        const_fund_invest_position = EastConfig.fund_invest_position_dict.value
        flipped_const_fund_invest_position = {value: key for key, value in const_fund_invest_position.items()}
        if not rep_data:
            df = pd.DataFrame(columns=const_fund_invest_position.keys())
        else:
            df = pd.DataFrame(rep_data).rename(columns=flipped_const_fund_invest_position)[const_fund_invest_position.keys()]
        return df