# coding:utf8
import requests
import re
import pandas as pd
from modules.datas.config.fundDataConst import Constants, EastConfig


"""基金持仓信息获取"""
class EastFundInvestPosition(object):

    def __init__(self):
        self._session = requests.session()

    def fund_invest_pos_api(self) -> str:
        """
        基金列表 api 地址
        """
        return Constants.FUNDS_CODES_URL.value

    def get_fund_invest_position(self, fund_code):
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