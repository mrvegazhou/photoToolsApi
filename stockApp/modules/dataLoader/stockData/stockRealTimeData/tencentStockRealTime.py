# coding:utf8
import pandas as pd
from datetime import datetime
from .stockRealTimeBase import StockRealTimeBase
from modules.dataLoader.config.stockDataConst import Constants, TencentConfig
from modules.common.hepler import get_stock_type


"""新浪免费行情获取"""
class TencentStockRealTime(StockRealTimeBase):
    @property
    def stock_api(self) -> str:
        return Constants.REAL_TIME_NET_TENCENT_URL.value

    def get_stock_code_list(self, stock_codes):
        stock_with_exchange_list = []
        for code in stock_codes:
            prefix = get_stock_type(code)
            if prefix == "sz":
                stock_with_exchange_list.append('sz' + code)
            elif prefix == "sh":
                stock_with_exchange_list.append('sh' + code)
            else:
                stock_with_exchange_list.append('bj' + code)
        return stock_with_exchange_list

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
        if response.text.strip() == 'v_pv_none_match="1";':
            return []
        return response.text

    def format_response_data(self, rep_data, **kwargs):
        const_stock_real_time = TencentConfig.stock_real_time_dict.value
        rep_data = str(rep_data).strip()
        if rep_data:
            stock_dict = dict()
            stock_info_list = rep_data.split(';')
            for item in stock_info_list:
                if item:
                    datas = item.split('~')
                    tmp_dict = {}
                    dt = datetime.strptime(datas[30], "%Y%m%d%H%M%S")
                    date = dt.strftime("%Y-%m-%d")
                    time = dt.strftime("%H:%M:%S")
                    for const_key in const_stock_real_time:
                        data_key = const_stock_real_time[const_key]
                        tmp_dict[const_key] = datas[data_key]
                        if const_key == 'time':
                            tmp_dict[const_key] = time
                        elif const_key == 'date':
                            tmp_dict[const_key] = date
                    stock_dict[datas[2]] = tmp_dict
            df = pd.DataFrame.from_dict(stock_dict, orient='index')
        else:
            df = pd.DataFrame(columns=const_stock_real_time.keys(), orient='index')
        return df
