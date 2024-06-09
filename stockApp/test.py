# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/stockApi")
from stockApp import app
from core.log.logger import get_module_logger
from stockApp.modules import init
from stockApp.modules.dataHandler.dataset import DatasetH


if __name__ == "__main__":
    # from service.stockGroup.stockGroupService import StockGroupService
    #
    # with app.app_context():
    #     StockGroupService.get_stock_code_date_list('csi100')
    #
    # ddd
    init()

    data_handler_config = {
        "start_time": "2008-01-01",
        "end_time": "2020-08-01",
        "fit_start_time": "2008-01-01",
        "fit_end_time": "2014-12-31",
        "instruments": 'csi300', #["000001"],
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









