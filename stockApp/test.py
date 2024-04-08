# -*- coding: utf-8 -*-
from plugin.easyquotation.sina import Sina
from modules.datas.stockRealTimeData.eastStockRealTime import EastStockRealTime
from modules.datas.stockRealTimeData.sinaStockRealTime import SinaStockRealTime
from modules.datas.stockRealTimeData.netEaseStockRealTime import NetEaseStockRealTime
from modules.datas.stockRealTimeData.tencentStockRealTime import TencentStockRealTime
from modules.datas.marketRealTimeData.eastMarketRealTime import EastMarketRealTime
import requests
import datetime
from modules.datas.fundsData.eastFundsCodes import EastFundsCodes

if __name__ == "__main__":
#     # sina = Sina()
#     # print(sina.real(['002004'， ‘002603’]))
#     east = EastStockRealTime()
#     df = east.get_stock_real_time(['300059'], full=False)
#     print(df)
#     print('\n')
#     sina = SinaStockRealTime()
#     df = sina.get_stock_real_time(['300059'])
#     print(df.transpose())

    # net = NetEaseStockRealTime()
    # net.get_stock_real_time(['300059'])
    # tencent =TencentStockRealTime()
    # tencent.get_stock_real_time(['300059', '002603'])
    # east = EastMarketRealTime()
    # east.get_market_real_time('沪深xxxA')

    east = EastFundsCodes()
    east.get_funds_codes_list('etf')



