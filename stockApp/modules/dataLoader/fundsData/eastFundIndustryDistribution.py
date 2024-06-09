# coding:utf8
import pandas as pd
from modules.dataLoader.config.fundDataConst import Constants, EastConfig
from modules.common import session


"""基金行业分布信息"""
class EastFundIndustryDistribution(object):

    def __init__(self):
        self._session = session
        const_fund_industry_distribution_dict = EastConfig.fund_industry_distribution_dict.value
        self.columns = const_fund_industry_distribution_dict.keys()

    @property
    def fund_industry_distribution_api(self) -> str:
        """
        基金行业分布信息 api 地址
        """
        return Constants.FUND_INDUSTRY_DISTRIBUTION_URL.value

    def get_fund_industry_distribution(self, fund_code, dates, **kwargs):
        '''
        获取基金行业分布信息
        '''
        if not fund_code:
            return pd.DataFrame([], columns=self.columns)
        res = self._fetch_fund_industry_distribution_data(fund_code, dates, **kwargs)
        return self._format_fund_industry_distribution_data(res, **kwargs)

    def _fetch_fund_industry_distribution_data(self, fund_code, dates, **kwargs):
        if isinstance(dates, str):
            dates = [dates]
        elif dates is None:
            dates = [None]
        headers = EastConfig.fund_headers.value
        datas_list = []
        for date in dates:
            params = [
                ('FCODE', fund_code),
                ('OSVersion', '14.4'),
                ('appVersion', '6.3.8'),
                ('deviceid', '3EA024C2-7F22-408B-95E4-383D38160FB3'),
                ('plat', 'Iphone'),
                ('product', 'EFund'),
                ('serverVersion', '6.3.6'),
                ('version', '6.3.8'),
            ]
            if date is not None:
                params.append(('DATE', date))
            url = self.fund_industry_distribution_api
            response = self._session.get(url, headers=headers, params=params)
            datas = response.json()['Datas']
            # list_of_dicts = [
            #     dict(d, code=fund_code) for d in datas
            # ]
            datas_list = datas_list + datas
        return datas_list

    def _format_fund_industry_distribution_data(self, res, **kwargs):
        if not res or len(res) == 0:
            return pd.DataFrame([], columns=self.columns)
        df = pd.DataFrame(res)
        const_fund_industry_distribution = EastConfig.fund_industry_distribution_dict.value
        flipped_columns = {value: key for key, value in const_fund_industry_distribution.items()}
        df.rename(columns=flipped_columns, inplace=True)
        df = df.drop_duplicates()
        return df