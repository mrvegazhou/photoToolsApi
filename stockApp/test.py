# -*- coding: utf-8 -*-
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Union
import pandas as pd
import numpy as np
from modules.dataHandler.dumpHDF5 import DumpDataBase
from service.dayTrading.dayTradingService import DayTradingService
from service.stockGroup.stockGroupService import StockGroupService

sys.path.append("/Users/vega/workspace/codes/py_space/working/stockApi")

from stockApp import app
from stockApp.modules.init import init
from stockApp.modules.dataHandler.dataset import DatasetH


if __name__ == "__main__":

    provider_uri = "/Users/vega/workspace/codes/py_space/working/stockApi/stockApp/crontab/_datas"


    def calendar_task():
        instance = DumpDataBase(stock_app_dir=provider_uri)
        # 日期df
        with app.app_context():
            calendars_df = DayTradingService.get_all_trading_dates()
            instance.save_calendars(calendars_df)
            return calendars_df


    def instruments_task(name: str, start_time: Union[pd.Timestamp, str], end_time: Union[pd.Timestamp, str]):
        instance = DumpDataBase(stock_app_dir=provider_uri)
        # 股票df
        with app.app_context():
            instrument_list = StockGroupService.get_stock_code_date_list(name, start_time, end_time)
            instrument_df = pd.DataFrame(instrument_list, columns=[instance.symbol_field_name, instance.INSTRUMENTS_START_FIELD, instance.INSTRUMENTS_END_FIELD])
            instance.save_instruments(instrument_df)
            return instrument_df


    def feature_process_task(partition_df, calendars_df):
        instance = DumpDataBase(stock_app_dir=provider_uri)
        with app.app_context():
            # for row in partition_df.itertuples():
            #     code = getattr(row, instance.symbol_field_name)
            #     begin = getattr(row, instance.INSTRUMENTS_START_FIELD)
            #     end = getattr(row, instance.INSTRUMENTS_END_FIELD)
            featrue_df = DayTradingService.get_feature_datas('600083', '2008-01-02', '2020-07-31')
            print(featrue_df)
            instance.save_features('600083', featrue_df, calendars_df)

    def features_task(instruments_df, calendars_df):
        # 要分割的份数
        num_partitions = 5
        partitions = np.array_split(instruments_df, num_partitions)
        executor = ThreadPoolExecutor(max_workers=num_partitions)
        results = [executor.submit(feature_process_task, part, calendars_df) for part in partitions]
        for result in as_completed(results):
            print(result.result())
        executor.shutdown(wait=True)

    # 加载数据
    def execute_dump_task(start_time, end_time):
        # executor = ThreadPoolExecutor(max_workers=2)
        # future_cal = executor.submit(calendar_task)
        # future_ins = executor.submit(instruments_task, '', start_time, end_time)
        # calendars_df = future_cal.result()
        # instruments_df = future_ins.result()
        # executor.shutdown(wait=True)
        # features_task(instruments_df, calendars_df)

        calendars_df = calendar_task()
        instruments_df = instruments_task('', start_time, end_time)
        feature_process_task(instruments_df, calendars_df)


    # with app.app_context():
    #     execute_dump_task('2019-01-01', '2020-01-01')
    # ssss


    init(provider_uri=provider_uri)

    data_handler_config = {
        "start_time": "2008-01-01",
        "end_time": "2020-08-01",
        "fit_start_time": "2008-01-01",
        "fit_end_time": "2014-12-31",
        "instruments": ["600083"],
    }

    kwargs = {
                "handler": {
                    "class": "Alpha158",
                    "module_path": "stockApp.modules.contrib.data.handler",
                    "kwargs": data_handler_config,
                },
                "segments": {
                    "train": ("2013-01-01", "2014-12-31"),
                    "valid": ("2015-01-01", "2016-12-31"),
                    "test": ("2019-01-01", "2020-08-01"),
                },
    }
    with app.app_context():
        datasetH = DatasetH(**kwargs)
    # dataset = init_instance_by_config(task["dataset"])
    # from modules.dataHandler.data import D
    # print(D, "===x=====")









