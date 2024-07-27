# -*- coding: utf-8 -*-
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Union
import pandas as pd
import numpy as np

from modules.dataHandler.dumpHDF5 import DumpDataBase
from modules.workflow.record_temp import SignalRecord
from service.dayTrading.dayTradingService import DayTradingService
from service.stockGroup.stockGroupService import StockGroupService

sys.path.append("/Users/vega/workspace/codes/py_space/working/stockApi")

from stockApp import app
from stockApp.modules.init import init
from stockApp.modules.dataHandler.dataset import DatasetH
from stockApp.modules.contrib.model.gbdt import LGBModel
from stockApp.modules.contrib.model.pytorch_lstm import LSTM
from stockApp.modules.workflow import R


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
            for row in partition_df.itertuples():
                code = getattr(row, instance.symbol_field_name)
                begin = getattr(row, instance.INSTRUMENTS_START_FIELD)
                end = getattr(row, instance.INSTRUMENTS_END_FIELD)
                featrue_df = DayTradingService.get_feature_datas(code, start_date=begin, end_date=end)
                instance.save_features(code, featrue_df, calendars_df)

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
    #     DayTrading.clear_tables()
    #     execute_dump_task('2019-01-01', '2020-01-01')
    # ssss


    init(provider_uri=provider_uri)

    data_handler_config = {
        "start_time": "2020-01-02",
        "end_time": "2020-07-31",
        "fit_start_time": "2020-01-02",
        "fit_end_time": "2020-07-31",
        "instruments": ["600083"],
        # "infer_processors": [
        #     {"class": "RobustZScoreNorm", "kwargs": {"fields_group": "feature", "clip_outlier": "true"}},
        #     {"class": "Fillna", "kwargs": {"fields_group": "feature"}},
        # ],
        # "learn_processors": [
        #     "DropnaLabel",
        #     {"class": "CSRankNorm", "kwargs": {"fields_group": "label"}},  # CSRankNorm
        # ],
    }

    kwargs = {
                "handler": {
                    "class": "Alpha158",
                    "module_path": "stockApp.modules.contrib.data.handler",
                    "kwargs": data_handler_config,
                },
                "segments": {
                    "train": ("2020-01-02", "2020-07-21"),
                    "valid": ("2020-01-02", "2020-07-21"),
                    "test": ("2020-06-10", "2020-06-17"),
                },
    }

    with app.app_context():
        with R.start(experiment_name="train_model"):
            dataset = DatasetH(**kwargs)
            # kwargs = {
            #     # "loss": "mse",
            #     # "colsample_bytree": 0.8879,
            #     # "learning_rate": 0.0421,
            #     # "subsample": 0.8789,
            #     # "lambda_l1": 205.6999,
            #     # "lambda_l2": 580.9768,
            #     # "max_depth": 8,
            #     # "num_leaves": 210,
            #     # "num_threads": 20,
            #     'boosting_type': 'gbdt',  # 设置提升类型
            #     'objective': 'multiclass',  # 目标函数
            #     'num_class': 3,
            #     # 'metric': 'binary_logloss',  # 评估函数
            #     'num_leaves': 31,  # 叶子节点数
            #     'learning_rate': 0.01,  # 学习速率
            #     'feature_fraction': 0.8,  # 建树的特征选择比例
            #     'bagging_fraction': 0.8,  # 建树的样本采样比例
            #     'bagging_freq': 5,  # k 意味着每 k 次迭代执行bagging
            #     'seed': 100,
            #     'n_jobs': -1,
            #     'verbose': -1,
            #     'lambda_l1': 0.1,
            #     'lambda_l2': 0.2,
            # }
            # model = LGBModel(**kwargs)
            kwargs = {

            }
            model = LSTM(**kwargs)

            model.fit(dataset)
            # print(model.predict(dataset=dataset, segment='test'))

            # R.save_objects(trained_model=model)
            # rid = R.get_recorder().id
            # print(rid, '-----rid-------')
            #
            # # prediction
            # recorder = R.get_recorder()
            # sr = SignalRecord(model, dataset, recorder)
            # sr.generate()


    # from modules.dataHandler.data import D
    # print(D, "===x=====")









