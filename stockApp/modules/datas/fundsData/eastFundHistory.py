# coding:utf8
import requests
import re
import pandas as pd
from modules.datas.config.fundDataConst import Constants, EastConfig

"""基金历史行情获取"""
class EastFundHistory:

    def __init__(self):
        self._session = requests.session()

    def fund_history_api(self) -> str:
        """
        基金历史数据 api 地址
        """
        return Constants.FUND_HISTORY_URL.value

    def get_fund_history(self, fund_code, **kwargs):
        '''
        获取历史数据调用方法
        '''
        if not fund_code:
            const_fund_history_dict = EastConfig.fund_history_dict.value
            columns = const_fund_history_dict.keys()
            return pd.DataFrame([], columns=columns)

        res = self._fetch_fund_history_data(fund_code, **kwargs)
        return self._format_fund_history_resp_data(res, **kwargs)

    def _fetch_fund_history_data(self, fund_code, **kwargs):
        if 'pz' in kwargs:
            pz = kwargs['pz']
        else:
            pz = 40000

        data = {
            'FCODE': f'{fund_code}',
            'IsShareNet': 'true',
            'MobileKey': '1',
            'appType': 'ttjj',
            'appVersion': '6.2.8',
            'cToken': '1',
            'deviceid': '1',
            'pageIndex': '1',
            'pageSize': f'{pz}',
            'plat': 'Iphone',
            'product': 'EFund',
            'serverVersion': '6.2.8',
            'uToken': '1',
            'userId': '1',
            'version': '6.2.8',
        }
        const_fund_headers = EastConfig.fund_headers.value
        response = self._session.get(self.fund_history_api, headers=const_fund_headers, data=data, verify=False)
        return response.json()

    def _format_fund_history_resp_data(self, json_response):
        const_fund_history_dict = EastConfig.fund_history_dict.value
        columns = const_fund_history_dict.keys()
        rows = []
        if json_response is None:
            return pd.DataFrame(rows, columns=columns)
        datas = json_response['Datas']
        if len(datas) == 0:
            return pd.DataFrame(rows, columns=columns)
        rows = []
        for stock in datas:
            date = stock['FSRQ']
            tmp_dict = {}
            for key in const_fund_history_dict:
                if key == 'date':
                    tmp_dict['date'] = date
                elif key == 'NAV_per_unit':
                    tmp_dict['NAV_per_unit'] = stock['DWJZ']
                elif key == 'cumulative_NAV':
                    tmp_dict['cumulative_NAV'] = stock['LJJZ']
                elif key == 'percent':
                    tmp_dict['percent'] = stock['JZZZL']
                rows.append(tmp_dict)
        df = pd.DataFrame(rows)
        return df