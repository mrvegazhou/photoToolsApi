# coding:utf8
import sys, os, inspect
PACKAGE_PARENT = '../../'
SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(inspect.getfile(inspect.currentframe())))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
import pandas as pd
from stockApp.service.stockInfo.stockInfoService import StockInfoService
from stockApp.modules.common.time import get_now_date, get_last_n_date

def sync_stock_info():
    file_name = get_now_date() + ".json"
    # 获取当前交易日

    last_day_file_name = get_last_n_date(1) + ".json"
    file_path = '/crontab/_datas2/stocks/{}'
    if not os.path.exists(file_path):
        all_stocks_df = StockInfoService.get_remote_stocks_codes()
        all_stocks_df.to_json(file_path.format(file_name), orient='records', lines=True)
    else:
        all_stocks_df = pd.read_json(file_path.format(file_name), lines=True)
    if os.path.exists(last_day_file_name):
        os.remove(file_path.format(last_day_file_name))

    StockInfoService.save_remote_stocks_list(all_stocks_df)


if __name__ == '__main__':
    sync_stock_info()