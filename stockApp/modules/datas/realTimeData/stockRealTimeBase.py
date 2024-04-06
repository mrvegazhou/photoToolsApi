# coding:utf8
import abc
import requests
from multiprocessing.pool import ThreadPool
from functools import partial

class StockRealTimeBase(metaclass=abc.ABCMeta):
    '''
        子类需要做的：
        1 设置stock_api抓取实时股票的api url
        2 get_stock_code_list 获取实时股票数据的参数id 如果不需要获取额外的参数可以不重写
        3 fetch_stock_data 获取数据
        4 format_response_data 格式化数据
    '''

    max_num = 800  # 每次请求的最大股票数

    def __init__(self):
        self._session = requests.session()

    @property
    @abc.abstractmethod
    def stock_api(self) -> str:
        """
        行情 api 地址
        """
        pass

    def get_stock_real_time(self, stock_codes, full=False):
        if not isinstance(stock_codes, list):
            stock_codes = [stock_codes]
        stock_list = self._get_stock_code_list(stock_codes)
        return self.get_stock_data(stock_list, full=full)

    def get_stock_data(self, stock_lists, **kwargs):
        pool_len = len(stock_lists)
        with ThreadPool(processes=pool_len) as pool:
            partial_func = partial(self.fetch_stock_data, full=kwargs['full'] if 'full' in kwargs else False)
            res = pool.map(partial_func, stock_lists)
        # """获取并格式化股票信息"""
        return self.format_response_data(res[0], **kwargs)

    def format_response_data(self, rep_data, **kwargs):
        return rep_data

    @abc.abstractmethod
    def fetch_stock_data(self, stock_list):
        pass

    def get_stock_code_list(self, stock_codes):
        return stock_codes

    def _get_stock_code_list(self, stock_codes):
        stock_with_exchange_list = self.get_stock_code_list(stock_codes)
        if self.max_num > len(stock_with_exchange_list):
            return [stock_with_exchange_list]
        stock_list = []
        for i in range(0, len(stock_codes), self.max_num):
            request_list = stock_with_exchange_list[i: i + self.max_num]
            stock_list.append(request_list)
        return stock_list
