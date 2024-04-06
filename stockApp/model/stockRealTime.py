# -*- coding: utf-8 -*-
from stockApp.config.mainConst import StockDict


class Base:
    def add_attribute(self, name, value):
        setattr(self, name, value)


class StockRealTime(Base):
    pass


def set_dynamic_attribute(type_obj='', dict={}):
    if type_obj == "StockRealTime":
        instance = StockRealTime()
    else:
        return None
    attrs = StockDict.stock_real_time_dict.value
    for key in attrs:
        value = dict.get(key)
        if value is not None:
            instance.add_attribute(key, value)
    return instance