# -*- coding: utf-8 -*-
from plugin.easyquotation.sina import Sina
from modules.datas.stockRealTimeData.eastStockRealTime import EastStockRealTime
from modules.datas.stockRealTimeData.sinaStockRealTime import SinaStockRealTime
from modules.datas.stockRealTimeData.netEaseStockRealTime import NetEaseStockRealTime
from modules.datas.stockRealTimeData.tencentStockRealTime import TencentStockRealTime
from modules.datas.marketRealTimeData.eastMarketRealTime import EastMarketRealTime
import requests
import datetime
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
    east = EastMarketRealTime()
    east.get_market_real_time('沪深xxxA')



# market: sh:沪市 sz:深市
# number: 股票代码
# def getData(market, number):
#     url = 'http://hq.sinajs.cn/list=' + market + number
#     respond = requests.get(url)
#     print(respond.text)
#     index = respond.text.find('=') + 2
#     data_arr = respond.text[index:-4].split(',')
#     data = {'股票代码': data_arr[0], '今日开盘价': data_arr[1], '昨日收盘价': data_arr[2], '当前价格': data_arr[3],
#             '今日最高价': data_arr[4],
#             '今日最低价': data_arr[5], '竞买价': data_arr[6], '竞卖价': data_arr[7], '成交的股票数': data_arr[8],
#             '成交金额': data_arr[9],
#             '买一挂单': data_arr[10], '买一报价': data_arr[11], '买二挂单': data_arr[12], '买二报价': data_arr[13],
#             '买三挂单': data_arr[14], '买三报价': data_arr[15], '买四挂单': data_arr[16], '买四报价': data_arr[17],
#             '买五挂单': data_arr[18], '买五报价': data_arr[19], '卖一挂单': data_arr[20], '卖一报价': data_arr[21],
#             '卖二挂单': data_arr[22], '卖二报价': data_arr[23], '卖三挂单': data_arr[24], '卖三报价': data_arr[25],
#             '卖四挂单': data_arr[26], '卖四报价': data_arr[27], '卖五挂单': data_arr[28], '卖五报价': data_arr[29],
#             '日期': data_arr[30], '时间': data_arr[31]}
#
#     return data
#
#
# if __name__ == '__main__':
#     import requests
#
#     gudaima = "bj831087"  # 股票代码
#     headers = {'referer': 'http://finance.sina.com.cn'}
#     resp = requests.get('http://hq.sinajs.cn/list=' + gudaima, headers=headers, timeout=6)
#     data = resp.text
#     print(data)

#
# # -*- coding: utf-8 -*-
#
# import requests
# import time
# import json
#
#
# def gupiaopankou_dfcf(daima):
#     """
#     从东方财富网获取股票盘口实时数据
#     :param daima: 股票代码
#     :return:  盘口数据
#     """
#     # if daima[:2] == "sh":
#     #     lsbl = '1.' + daima[2:]
#     # else:
#     #     lsbl = '0.' + daima[2:]
#     lsbl = '0.000001,0.600519'
#     wangzhi = 'http://push2.eastmoney.com/api/qt/stock/get?&fltt=2&invt=2&fields=f120,f121,f122,f174,f175,f59,f163,f43,f57,' \
#               'f58,f169,f170,f46,f44,f51,f168,f47,f164,f116,f60,f45,f52,f50,f48,f167,f117,f71,f161,f49,f530,f135,f136,f137,' \
#               'f138,f139,f141,f142,f144,f145,f147,f148,f140,f143,f146,f149,f55,f62,f162,f92,f173,f104,f105,f84,f85,f183,' \
#               'f184,f185,f186,f187,f188,f189,f190,f191,f192,f107,f111,f86,f177,f78,f110,f262,f263,f264,f267,f268,f255,f256,' \
#               'f257,f258,f127,f199,f128,f198,f259,f260,f261,f171,f277,f278,f279,f288,f152,f250,f251,f252,f253,f254,f269,' \
#               'f270,f271,f272,f273,f274,f275,f276,f265,f266,f289,f290,f286,f285,f292,f293,f294,f295&secids=' + lsbl + \
#               '&_=' + str(time.time())
#
#     resp = requests.get(wangzhi, timeout=6)
#     # print (resp) #打印请求结果的状态码
#     data = json.loads(resp.text)['data']
#     print(resp.text, data)
#     # pankou = {'代码': data['f57'], '名称': data['f58'], '开盘': data['f46'], '最高': data['f44'], '最低': data['f45'],
#     #           '最新': data['f43'], '金额': data['f48'],
#     #           '卖1价': data['f39'], '卖1量': data['f40'], '卖2价': data['f37'], '卖2量': data['f38'],
#     #           '卖3价': data['f35'], '卖3量': data['f36'], '卖4价': data['f33'], '卖4量': data['f34'],
#     #           '卖5价': data['f31'], '卖5量': data['f32'],
#     #           '买1价': data['f19'], '买1量': data['f20'], '买2价': data['f17'], '买2量': data['f18'],
#     #           '买3价': data['f15'], '买3量': data['f16'], '买4价': data['f13'], '买4量': data['f14'],
#     #           '买5价': data['f11'], '买5量': data['f12']
#     #           }
#     # print(pankou)
#     # return pankou
#
#
#
#
# import re
# import csv
# if __name__ == '__main__':
# #     # while 1:
# #     gupiaopankou_dfcf(['sz000001', 'sh600519'])
# #         # time.sleep(1)
#     url = f'http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft=all&rs=&gs=0&sc=6yzf&st=desc&sd=2020-12-16&ed=2021-12-16&qdii=&tabSubtype=,,,,,&pi=1&pn=50&dx=1'
#     headers = {
#         'Cookie': 'HAList=a-sz-300059-%u4E1C%u65B9%u8D22%u5BCC; em_hq_fls=js; qgqp_b_id=7b7cfe791fce1724e930884be192c85e; _adsame_fullscreen_16928=1; st_si=59966688853664; st_asi=delete; st_pvi=79368259778985; st_sp=2021-12-07%2014%3A33%3A35; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink; st_sn=3; st_psi=20211216201351423-112200312936-0028256540; ASP.NET_SessionId=miyivgzxegpjaya5waosifrb',
#         'Host': 'fund.eastmoney.com',
#         'Referer': 'http://fund.eastmoney.com/data/fundranking.html',
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
#     }
#     response = requests.get(url=url, headers=headers)
#     print(response.text)


