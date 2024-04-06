# coding:utf8
import sys
import os
# 获取项目根目录的路径（假设当前脚本在module1文件夹内）
project_root = os.path.abspath(os.path.join(__file__, *(['..'] * 5)))
# 将项目根目录添加到sys.path中
sys.path.append(project_root)
import time
import json
from jsonpath import jsonpath
from datetime import datetime
from .stockRealTimeBase import StockRealTimeBase
import pandas as pd
from modules.datas.config.stockDataConst import Constants, EastConfig
from modules.datas.common.hepler import get_stock_type

"""东财免费行情获取"""
class EastStockRealTime(StockRealTimeBase):

    @property
    def stock_api(self) -> str:
        return Constants.REAL_TIME_EAST_MONEY_URL.value

    def get_stock_code_list(self, stock_codes):
        if isinstance(stock_codes, str):
            stock_codes = [stock_codes]
        secids = [self._get_code_id(code)
                  for code in stock_codes]
        return secids

    def fetch_stock_data(self, stock_list, full):
        if full:
            stock_dict = dict()
            for stock_code in stock_list:
                params = (
                    ('fltt', '2'),
                    ('invt', '2'),
                    ('secid', stock_code),
                    ('_', str(time.time()))
                )
                resp = self._session.get(Constants.FULL_REAL_TIME_EAST_MONEY_URL.value,
                                              headers=EastConfig.request_header.value,
                                              params=params)
                data = json.loads(resp.text)['data']
                if data:
                    code = data['f57']
                    if data['f86']:
                        datetime_object = datetime.fromtimestamp(data['f86'])
                        date_format = "%Y-%m-%d %H:%M:%S"
                        date_arr = datetime_object.strftime(date_format).split()
                        data['f86'] = date_arr[0]
                        data['time'] = date_arr[1]
                    stock_dict[code] = data
            return stock_dict
        else:
            stock_real_time_dict = EastConfig.stock_real_time_dict.value
            fields = ",".join(stock_real_time_dict.values())
            params = (
                ('OSVersion', '14.3'),
                ('appVersion', '6.3.8'),
                ('fields', fields),
                ('fltt', '2'),
                ('plat', 'Iphone'),
                ('product', 'EFund'),
                ('secids', ",".join(stock_list)),
                ('serverVersion', '6.3.6'),
                ('version', '6.3.8'),
            )
            response = self._session.get(self.stock_api,
                              headers=EastConfig.request_header.value,
                              params=params)
            json_response = response.json()
            rows = jsonpath(json_response, '$..diff[:]')
            if rows:
                return rows
            return []

    def format_response_data(self, rep_data, **kwargs):
        if kwargs['full']:
            full_stock_real_time_dict = EastConfig.full_stock_real_time_dict.value
            swapped_const_stock_real_time = {value: key for key, value in full_stock_real_time_dict.items()}
            if not rep_data:
                df = pd.DataFrame(columns=full_stock_real_time_dict.keys())
            else:
                df = pd.DataFrame.from_dict(rep_data, orient='index')
                df.rename(columns=swapped_const_stock_real_time, inplace=True)
            return df
        else:
            stock_real_time_dict = EastConfig.stock_real_time_dict.value
            swapped_const_stock_real_time = {value: key for key, value in stock_real_time_dict.items()}
            if rep_data:
                df = pd.DataFrame(rep_data)[list(stock_real_time_dict.values())].rename(columns=swapped_const_stock_real_time)
                df.index.name = 'code'
                df.set_index('code', inplace=True)
            else:
                df = pd.DataFrame(columns=stock_real_time_dict.keys())
            return df

    """
    生成东方财富股票专用的行情ID
    code:可以是代码或简称或英文
    """
    def _get_code_id(self, code):
        code_id_dict = EastConfig.code_id_dict.value
        if code in code_id_dict.keys():
            return code_id_dict[code]
        prefix = get_stock_type(code)
        if prefix == "sh":
            return '1.' + code
        elif prefix == "sz":
            return '0.' + code
        else:
            return '0.' + code