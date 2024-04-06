# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
from stock_app.api.spider.spider_stock_finance import spider_stock_finance
from stock_app.model.stock import Stock
from stock_app.model.stock_finance import StockFinance

def sync_stock_finance():
    stock = Stock()
    all_stocks = stock.get_all_stock_codes()
    for item in all_stocks:
        df = spider_stock_finance(item.code[2:])
        for index, row in df.iterrows():
            if row['assets']=='--':
                row['assets'] = 0
            # 判断是否存在
            ret = StockFinance.get_stock_finance_by_code_date(item.code, index)
            if not ret:
                StockFinance.add_stock_finance(item.code, index, row['assets'])



if __name__ == "__main__":
    sync_stock_finance()

