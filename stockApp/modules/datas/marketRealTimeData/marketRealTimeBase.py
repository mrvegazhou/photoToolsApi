# coding:utf8
import abc
import requests


"""板块行情获取"""
class MarketRealTimeBase(metaclass=abc.ABCMeta):

    def __init__(self):
        self._session = requests.session()

    @property
    @abc.abstractmethod
    def stock_api(self) -> str:
        """
        行情 api 地址
        """
        pass

    def get_market_real_time(self, code, **kwargs):
        res = self.fetch_stock_data(code)
        # """获取并格式化股票信息"""
        return self.format_response_data(res, **kwargs)

    def format_response_data(self, rep_data, **kwargs):
        return rep_data

    @abc.abstractmethod
    def fetch_stock_data(self, stock_list):
        pass