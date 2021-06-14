# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
from stock_app.model.stock import Stock
from stock_app.api.request_api import api_stock_info, api_stock_day_trading_info2, api_stock_a_capital_total
from stock_app.__init__ import utils


# 同步股票数据
def sync_stocks():
    stock = Stock()
    all_stocks = stock.get_all_stock_codes()
    all_codes_list = [item.code for item in all_stocks]

    stock_zh_a_spot_df = api_stock_info()
    if stock_zh_a_spot_df.empty:
        return None

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
        else:
            # 查看st和交易状态
            now = utils["date"].get_now_date()
            start_date = utils["date"].skip_date(now, 10)
            end_date = now
            new_code = list(code)
            new_code.insert(2, '.')
            new_code = ''.join(new_code)

            info = api_stock_day_trading_info2(new_code, "d", start_date, end_date)
            is_ST = info.loc[info.index[0], 'isST'] if not info.empty else False
            trade_status = info.loc[info.index[0], 'tradestatus'] if not info.empty else True
            capital_df, col = api_stock_a_capital_total(code)
            capital_total = capital_df.at[0, col] if capital_df is not None else 0

            if not info.empty:
                Stock.update_stock_st_status(code, capital_total, is_ST, trade_status)




if __name__ == "__main__":
    sync_stocks()
    # import akshare as ak
    # print(ak.stock_zh_a_spot())
    # Stock.update_stock_st_status("sh.600000", 1, 1)




