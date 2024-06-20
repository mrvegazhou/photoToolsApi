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
        if name:
            stocks = StockGroupService.get_stock_group_list(name)
        else:
            stocks = StockInfo.get_all_stocks()

        res = []
        if isinstance(start_time, str):
            start_time = pd.to_datetime(start_time)

        for item in stocks:
            st = max(start_time, pd.Timestamp(item.IPO_date))
            if pd.Timestamp(end_time) < st:
                et = st.strftime('%Y-%m-%d')
            else:
                et = pd.Timestamp(end_time).strftime('%Y-%m-%d')
            res.append([item.code, st.strftime('%Y-%m-%d'), str(et)])
        return res



