# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
from stock_app.model.stock import Stock
from stock_app.api.request_api import api_stock_info


# 同步股票数据
def sync_stocks():
    stock = Stock()
    all_stocks = stock.get_all_stock_codes()
    all_codes_list = [item.code for item in all_stocks]

    stock_zh_a_spot_df = api_stock_info()

    # 添加新增的股票
    stocks_df = stock_zh_a_spot_df[~stock_zh_a_spot_df['代码'].isin(all_codes_list)]
    for index, row in stocks_df.iterrows():
        code = row['代码']
        name = row['名称']
        Stock.add_new_stock(name, code)

    # 删除退市的股票
    for code in all_codes_list:
        if code not in stock_zh_a_spot_df['代码'].tolist():
            stock.del_stock(code)



if __name__ == "__main__":
    sync_stocks()

