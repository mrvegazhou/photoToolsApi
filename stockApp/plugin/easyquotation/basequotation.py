# coding:utf8
import abc
import re
import multiprocessing.pool
import requests
from .helpers import get_stock_type

"""行情获取基类"""
class BaseQuotation(metaclass=abc.ABCMeta):
    max_num = 800  # 每次请求的最大股票数

    @property
    @abc.abstractmethod
    def stock_api(self) -> str:
        """
        行情 api 地址
        """
        pass

    def __init__(self):
        self._session = requests.session()


    def get_stock_data(self, stock_list, **kwargs):
        """获取并格式化股票信息"""
        res = self._fetch_stock_data(stock_list)
        return self.format_response_data(res, **kwargs)

    def real(self, stock_codes, prefix=False):
        if not isinstance(stock_codes, list):
            stock_codes = [stock_codes]
        stock_list = self.gen_stock_list(stock_codes)
        return self.get_stock_data(stock_list, prefix=prefix)

    def gen_stock_list(self, stock_codes):
        stock_with_exchange_list = self._gen_stock_prefix(stock_codes)

        if self.max_num > len(stock_with_exchange_list):
            request_list = ",".join(stock_with_exchange_list)
            return [request_list]

        stock_list = []
        for i in range(0, len(stock_codes), self.max_num):
            request_list = ",".join(
                stock_with_exchange_list[i: i + self.max_num]
            )
            stock_list.append(request_list)
        return stock_list


    def _gen_stock_prefix(self, stock_codes):
        return [
            get_stock_type(code) + code[-6:] for code in stock_codes
        ]

    def get_stocks_by_range(self, params):
        headers = {
            "Accept-Encoding": "gzip, deflate, sdch",
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/54.0.2840.100 "
                "Safari/537.36"
            ),
            'Referer': 'https://finance.sina.com.cn'
        }

        r = self._session.get(self.stock_api + params, headers=headers)
        return r.text

    def _fetch_stock_data(self, stock_list):
        """获取股票信息"""
        pool = multiprocessing.pool.ThreadPool(len(stock_list))
        try:
            res = pool.map(self.get_stocks_by_range, stock_list)
        finally:
            pool.close()
        return [d for d in res if d is not None]

    def format_response_data(self, rep_data, **kwargs):
        pass

    def get_all_codes(self):
        response = requests.get("http://www.shdjt.com/js/lib/astock.js")
        return re.findall(r"~([a-z0-9]*)`", response.text)