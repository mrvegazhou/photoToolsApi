# -*- coding: utf-8 -*-
import pandas as pd
from typing import List, Dict, Union
from datetime import datetime, timedelta
from dao.stockInfo import StockInfo
from stockApp.dao.stockGroup import StockGroup
from stockApp import app


class StockGroupService:

    @staticmethod
    def get_stock_group_list(name: str) -> List[StockInfo]:
        if not name:
            return []
        stock_group_res = StockGroup.get_stock_list_by_sql(name)
        stocks = []
        for item in stock_group_res:
            stocks.append(item.code)
        filters = {
            StockInfo.code.in_(stocks)
        }
        return StockInfo.get_stock_by_conds(filters)

    @staticmethod
    def get_stock_code_date_list(name: str, start_time: Union[pd.Timestamp, str], end_time: Union[pd.Timestamp, str]) -> Dict[str, object]:
        stocks = StockGroupService.get_stock_group_list(name)
        res = {}
        if isinstance(start_time, str):
            start_time = pd.to_datetime(start_time)
        for item in stocks:
            start_time = max(start_time, pd.Timestamp(item.IPO_date))
            res[item.code] = [start_time.strftime('%Y-%m-%d'), str(end_time)]
        return res



