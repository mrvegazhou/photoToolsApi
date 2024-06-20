# coding:utf8
import pandas as pd
import datetime
import json
from py_mini_racer import py_mini_racer
from .stockDataBase import StockDataBase
from ..config.stockDataConst import Constants, SinaConfig


class TradingDate(StockDataBase):

    @property
    def stock_date_api(self) -> str:
        return Constants.SZSE_DATE_URL.value.format(datetime.datetime.now().strftime('%Y-%m'))

    def get_stock_trading_date(self) -> pd.DataFrame:
        '''
        获取当前日期是否为交易日
        '''
        data_json = self._fetch_trading_date_data()
        return self._format_trading_date_response_data(data_json)

    def _fetch_trading_date_data(self):
        req = self._session.get(self.stock_date_api, headers=SinaConfig.header.value)
        return json.loads(req.text)

    def _format_trading_date_response_data(self, json_state):
        lists = []
        now_date = json_state['nowdate']
        for dict_value in json_state['data']:
            if dict_value['jybz'] == "0":  # 非交易日
                lists.append([dict_value['jyrq'], False, now_date == dict_value['jyrq']])
            elif dict_value['jybz'] == "1":  # 交易日
                lists.append([dict_value['jyrq'], True, now_date == dict_value['jyrq']])
        columns = ['date', 'is_trading_day', 'is_now']
        return pd.DataFrame(lists, columns=columns)

    @property
    def stock_date_list_api(self) -> str:
        return Constants.SINA_DATE_LIST_URL.value

    def get_stock_trading_date_list(self) -> pd.DataFrame:
        """
        新浪财经-交易日历-历史数据
        https://finance.sina.com.cn/realstock/company/klc_td_sh.txt
        :return: 交易日历
        :rtype: pandas.DataFrame
        """
        data_json = self._fetch_trading_date_list_data()
        return self._format_trading_date_list_response_data(data_json)

    def _fetch_trading_date_list_data(self):
        r = self._session.get(self.stock_date_list_api)
        js_code = py_mini_racer.MiniRacer()
        js_code.eval(SinaConfig.hk_js_decode.value)
        return js_code.call("d", r.text.split("=")[1].split(";")[0].replace('"', ""))

    def _format_trading_date_list_response_data(self, date_list):
        temp_list = [datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y%m%d')
                           for date_str in date_list]
        temp_list.append('19920504')
        temp_df = pd.DataFrame(date_list)
        temp_df.columns = ["trading_date"]
        temp_df["trading_date"] = pd.to_datetime(temp_df["trading_date"]).dt.date
        temp_list.sort()
        temp_df = temp_df.dropna()
        return temp_df
