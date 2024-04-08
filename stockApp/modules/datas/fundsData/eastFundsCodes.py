# coding:utf8
import requests
import re
import pandas as pd
from modules.datas.config.fundDataConst import Constants, EastConfig


"""基金行情获取"""
class EastFundsCodes:

    def __init__(self):
        self._session = requests.session()

    def funds_codes_api(self) -> str:
        """
        基金列表 api 地址
        """
        return Constants.FUNDS_CODES_URL.value

    def get_funds_codes_list(self, fund_type='', **kwargs):
        '''
        获取所有基金的列表调用方法
        '''
        const_funds_type_dict = EastConfig.funds_type_dict.value
        if fund_type == '':
            fund_type = 'all'
        elif fund_type != '' and fund_type not in const_funds_type_dict.keys():
            return self._none_df_datas()

        res = self._fetch_funds_codes_data(fund_type)
        return self._format_funds_codes_resp_data(res, **kwargs)

    def _none_df_datas(self):
        const_funds_codes_dict = EastConfig.funds_codes_dict.value
        return pd.DataFrame(columns=const_funds_codes_dict.keys())

    def _fetch_funds_codes_data(self, fund_type):
        '''
        获取基金api
        '''
        headers = {
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75',
            'Accept': '*/*',
            'Referer': 'http://fund.eastmoney.com/data/fundranking.html',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        }
        params = [
            ('op', 'dy'),
            ('dt', 'kf'),
            ('rs', ''),
            ('gs', '0'),
            ('sc', 'qjzf'),
            ('st', 'desc'),
            ('es', '0'),
            ('qdii', ''),
            ('pi', '1'),
            ('pn', '50000'),
            ('dx', '0'),
        ]
        if fund_type is not None:
            params.append(('ft', fund_type))
        res = self._session.get(self.funds_codes_api(), headers=headers, params=params).text
        return res

    def _format_funds_codes_resp_data(self, rep_data, **kwargs):
        '''
        格式化获取的基金列表数据
        '''
        const_funds_codes_dict = EastConfig.funds_codes_dict.value
        columns = const_funds_codes_dict.keys()
        results = re.findall('"(\\d{6}),(.*?),', rep_data)
        print(results)
        df = pd.DataFrame(results, columns=columns)
        return df