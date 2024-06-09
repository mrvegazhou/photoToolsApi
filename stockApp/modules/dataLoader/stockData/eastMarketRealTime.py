# coding:utf8
import pandas as pd
from ...common.hepler import contains_chinese
from ..config.stockDataConst import Constants, EastConfig
from stockApp.config.mainConst import StockDict
from .stockDataBase import StockDataBase


class EastMarketRealTime(StockDataBase):
    """
    各组合行情获取
    Parameters
    ----------
    fs : Union[str, List[str]], optional
        行情名称或者多个行情名列表 可选值及示例如下

        - ``None``  沪深京A股市场行情
        - ``'沪深A股'`` 沪深A股市场行情
        - ``'沪A'`` 沪市A股市场行情
        - ``'深A'`` 深市A股市场行情
        - ``北A``   北证A股市场行情
        - ``'可转债'``  沪深可转债市场行情
        - ``'期货'``    期货市场行情
        - ``'创业板'``  创业板市场行情
        - ``'美股'``    美股市场行情
        - ``'港股'``    港股市场行情
        - ``'中概股'``  中国概念股市场行情
        - ``'新股'``    沪深新股市场行情
        - ``'科创板'``  科创板市场行情
        - ``'沪股通'``  沪股通市场行情
        - ``'深股通'``  深股通市场行情
        - ``'行业板块'``    行业板块市场行情
        - ``'概念板块'``    概念板块市场行情
        - ``'沪深系列指数'``    沪深系列指数市场行情
        - ``'上证系列指数'``    上证系列指数市场行情
        - ``'深证系列指数'``    深证系列指数市场行情
        - ``'ETF'`` ETF 基金市场行情
        - ``'LOF'`` LOF 基金市场行情
    """

    def __init__(self):
        super().__init__()

    @property
    def stock_api(self) -> str:
        return Constants.MARKET_REAL_TIME_URL.value

    def get_market_real_time(self, code, **kwargs):
        res = self._fetch_stock_data(code)
        # """获取并格式化股票信息"""
        return self._format_response_data(res, **kwargs)

    def _fetch_stock_data(self, code):
        main_market_dict = StockDict.market_dict.value
        flipped_market_dict = {v: k for k, v in main_market_dict.items()}
        if code not in flipped_market_dict and code not in main_market_dict:
            return []
        if contains_chinese(code):
            market_key = flipped_market_dict[code]
        else:
            market_key = code

        east_market_dict = EastConfig.market_dict.value
        trade_detail_dict = EastConfig.stock_real_time_dict.value

        fs = east_market_dict[market_key]
        fields = ",".join(trade_detail_dict.values())
        params = (
            ('pn', '1'),
            ('pz', '1000000'),
            ('po', '1'),
            ('np', '1'),
            ('fltt', '2'),
            ('invt', '2'),
            ('fid', 'f3'),
            ('fs', fs),
            ('fields', fields)
        )
        json_response = self._session.get(self.stock_api, headers=EastConfig.request_header.value, params=params).json()
        return json_response['data']['diff']

    def _format_response_data(self, rep_data, **kwargs):
        const_trade_detail_dict = EastConfig.stock_real_time_dict.value
        if rep_data:
            flipped_trade_detail_dict = {v: k for k, v in const_trade_detail_dict.items()}
            df = pd.DataFrame(rep_data)
            df = df.rename(columns=flipped_trade_detail_dict)
            date = pd.to_datetime(df['date'], unit='s', errors='coerce')
            if df['date'].isna().any():
                df['time'] = pd.NA
                df['date'] = pd.NA
            else:
                df['date'] = date.dt.strftime('%Y-%m-%d')
                df['time'] = date.dt.strftime('%H:%M:%S')
            # df.index.name = 'code'
            df.set_index('code', inplace=True, drop=False)
        else:
            df = pd.DataFrame(columns=const_trade_detail_dict.keys())
            df.set_index('code', inplace=True, drop=False)
        return df