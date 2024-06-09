# coding:utf8
from typing import List
from modules.dataLoader.config.fundDataConst import Constants, EastConfig
from modules.common import session


def get_public_dates(fund_code: str) -> List[str]:
    """
        获取历史上更新持仓情况的日期列表

        Parameters
        ----------
        fund_code : str
            6 位基金代码

        Returns
        -------
        List[str]
            指定基金公开持仓的日期列表
    """
    params = (
        ('FCODE', fund_code),
        ('appVersion', '6.3.8'),
        ('deviceid', '3EA024C2-7F22-408B-95E4-383D38160FB3'),
        ('plat', 'Iphone'),
        ('product', 'EFund'),
        ('serverVersion', '6.3.6'),
        ('version', '6.3.8'),
    )
    url = Constants.FUND_PUBLIC_DATES_URL.value
    headers = EastConfig.fund_headers.value
    json_response = session.get(
        url, headers=headers, params=params
    ).json()
    if json_response['Datas'] is None:
        return []
    return json_response['Datas']