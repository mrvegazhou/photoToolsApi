# coding:utf8
import json
import re
import pandas as pd
from .stockRealTimeBase import StockRealTimeBase
from modules.dataLoader.config.stockDataConst import Constants, NetEaseConfig
from modules.common.hepler import get_stock_type


"""新浪免费行情获取"""
class NetEaseStockRealTime(StockRealTimeBase):

    @property
    def stock_api(self) -> str:
        return Constants.REAL_TIME_NET_EASE_URL.value

    def get_stock_code_list(self, stock_codes):
        stock_with_exchange_list = []
        for code in stock_codes:
            prefix = get_stock_type(code)
            if prefix == "sz":
                stock_with_exchange_list.append('1' + code)
            elif prefix == "sh":
                stock_with_exchange_list.append('0' + code)
            else:
                stock_with_exchange_list.append('2' + code)
        return stock_with_exchange_list

    """获取股票信息"""
    def fetch_stock_data(self, stock_list, full):
        headers = {
            "Accept-Encoding": "gzip, deflate, sdch",
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/54.0.2840.100 "
                "Safari/537.36"
            ),
        }
        url = f"{self.stock_api}".format(','.join(stock_list))
        response = self._session.get(url, headers=headers)
        return response.text

    def format_response_data(self, rep_data, **kwargs):
        find = re.findall(r"_ntes_quote_callback\((.*)\);", rep_data)
        const_stock_real_time = NetEaseConfig.stock_real_time_dict.value
        if len(find) >= 1:
            datas = json.loads(find[-1])
            stock_dict = dict()
            for key in datas:
                tmp_dict = {}
                # 格式化时间
                if 'time' in datas[key]:
                    date = datas[key]['time']
                    date_arr = date.split()
                    datas[key]['time'] = date_arr[1]
                    datas[key]['date'] = date_arr[0]
                for const_key in const_stock_real_time:
                    data_key = const_stock_real_time[const_key]
                    tmp_dict[const_key] = datas[key][data_key]
                stock_dict[key] = tmp_dict
            df = pd.DataFrame.from_dict(stock_dict, orient='index')
        else:
            df = pd.DataFrame(columns=const_stock_real_time.keys(), orient='index')

        return df


