# coding:utf8
import re
import time
import pandas as pd
from .stockRealTimeBase import StockRealTimeBase
from modules.datas.config.stockDataConst import Constants, SinaConfig
from ..common.hepler import get_stock_type


"""新浪免费行情获取"""
class SinaStockRealTime(StockRealTimeBase):

    @property
    def stock_api(self) -> str:
        return f"{Constants.REAL_TIME_SINA_URL.value.format(int(time.time() * 1000))}"

    def get_stock_code_list(self, stock_codes):
        return [get_stock_type(item)+item for item in stock_codes if get_stock_type(item)]

    """获取股票信息"""
    def fetch_stock_data(self, stock_list, full):
        headers = {
            "Accept-Encoding": "gzip, deflate, sdch",
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/54.0.2840.100 "
                "Safari/537.36"
            ),
            'referer': 'https://finance.sina.com.cn'
        }
        r = self._session.get(self.stock_api + ",".join(stock_list), headers=headers)
        return r.text

    """
        格式化数据
        原始格式：
            var hq_str_sz002603="以岭药业,20.220,20.220,20.270,20.390,20.130,20.270,20.280,6881263,139427619.390,74291,20.270,31509,20.260,30700,20.250,38600,20.240,10300,20.230,97356,20.280,13800,20.290,16900,20.300,17400,20.310,23900,20.320,2024-04-03,15:00:00,00"
    """
    def format_response_data(self, rep_data, **kwargs):
        const_stock_real_time = SinaConfig.stock_real_time_dict.value
        datas = rep_data.split(';')
        pattern = r'(\d+)="([^"]*)"'
        stock_dict = dict()
        for item in datas:
            match = re.search(pattern, item)
            if match:
                stock_code = match.group(1)
                content_inside_quotes = match.group(2)
                content_inside_quotes = content_inside_quotes.strip(',')
                data_arr = content_inside_quotes.split(',')
                tmp_dict = {}
                for key in const_stock_real_time:
                    idx = const_stock_real_time[key]
                    tmp_dict[key] = data_arr[idx]
                stock_dict[stock_code] = tmp_dict
        if stock_dict:
            df = pd.DataFrame.from_dict(stock_dict, orient='index')
        else:
            df = pd.DataFrame(columns=const_stock_real_time.keys(), orient='index')
        df.index.name = 'code'
        return df

