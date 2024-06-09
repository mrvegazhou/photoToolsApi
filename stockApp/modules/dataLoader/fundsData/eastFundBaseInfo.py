# coding:utf8
import requests
import pandas as pd
from multiprocessing.pool import ThreadPool
from modules.dataLoader.config.fundDataConst import Constants, EastConfig

"""基金历史行情获取"""
class EastFundBaseInfo:

    def __init__(self):
        self._session = requests.session()
        const_fund_base_info_dict = EastConfig.fund_base_info_dict.value
        self.columns = const_fund_base_info_dict.keys()

    @property
    def fund_base_info_api(self) -> str:
        """
        基金基本数据 api 地址
        """
        return Constants.FUND_BASE_INFO_URL.value

    def get_fund_base_info(self, fund_code, **kwargs):
        '''
        获取基金基础信息
        '''
        if not fund_code:
            return pd.DataFrame([], columns=self.columns)

        res = self._fetch_fund_base_info_data(fund_code, **kwargs)
        return self._format_fund_base_info_resp_data(res, **kwargs)

    def _fetch_fund_base_info_data(self, fund_code, **kwargs):
        params = (
            ('FCODE', fund_code),
            ('deviceid', '3EA024C2-7F22-408B-95E4-383D38160FB3'),
            ('plat', 'Iphone'),
            ('product', 'EFund'),
            ('version', '6.3.8'),
        )
        const_fund_headers = EastConfig.fund_headers.value
        response = self._session.get(
            self.fund_base_info_api, headers=const_fund_headers, params=params
        ).json()
        return response['Datas']

    def _format_fund_base_info_resp_data(self, datas):
        if not datas:
            return pd.DataFrame([], columns=self.columns)
        const_fund_base_info_dict = EastConfig.fund_base_info_dict.value
        flipped_const_fund_base_info_dict = {value: key for key, value in const_fund_base_info_dict.items()}
        if not isinstance(datas, list):
            datas = [datas]
        df = pd.DataFrame(datas)[list(const_fund_base_info_dict.values())].rename(columns=flipped_const_fund_base_info_dict)
        df.index.name = 'code'
        df.set_index('code', inplace=True)
        return df


    def get_muliti_fund_base_info(self, fund_codes):
        """
            获取多只基金基本信息
            Parameters
            ----------
            fund_codes : List[str]
                6 位基金代码列表

            Returns
            -------
            Series
                多只基金基本信息
        """
        with ThreadPool(processes=len(fund_codes)) as pool:
            res = pool.map(self._fetch_fund_base_info_data, fund_codes)
        if not res or len(res) <= 0:
            return pd.DataFrame([], columns=self.columns)
        else:
            return self._format_fund_base_info_resp_data(res)

