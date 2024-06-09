# _*_ coding: utf-8 _*_
from enum import Enum, unique


@unique
class EastConfig(Enum):

    trader_info = {
        "assets": "https://jywg.18.cn/Com/queryAssetAndPositionV1?validatekey=%s",
        "submit": "https://jywg.18.cn/Trade/SubmitTradeV2?validatekey=%s",
        "revoke": "https://jywg.18.cn/Trade/RevokeOrders?validatekey=%s",
        "get_stock_list": "https://jywg.18.cn/Search/GetStockList?validatekey=%s",
        "get_orders_data": "https://jywg.18.cn/Search/GetOrdersData?validatekey=%s",
        "get_deal_data": "https://jywg.18.cn/Search/GetDealData?validatekey=%s",
        "authentication": "https://jywg.18.cn/Login/Authentication?validatekey=",
        "yzm": "https://jywg.18.cn/Login/YZM?randNum=",
        "prefix": "",
        "authentication_check": "https://jywg.18.cn/Trade/Buy",
        "get_his_deal_data": "https://jywg.18.cn/Search/GetHisDealData?validatekey=%s",
        "get_his_orders_data": "https://jywg.18.cn/Search/GetHisOrdersData?validatekey=%s",
        "get_can_buy_new_stock_list_v3": "https://jywg.18.cn/Trade/GetCanBuyNewStockListV3?validatekey=%s",
        "get_convertible_bond_list_v2": "https://jywg.18.cn/Trade/GetConvertibleBondListV2?validatekey=%s",
        "submit_bat_trade_v2": "https://jywg.18.cn/Trade/SubmitBatTradeV2?validatekey=%s",

        "response_format": {
            "int": [
                "current_amount",
                "enable_amount",
                "entrust_amount",
                "business_amount",
                "成交数量",
                "撤单数量",
                "委托数量",
                "股份可用",
                "买入冻结",
                "卖出冻结",
                "当前持仓",
                "股份余额"
            ],
            "float": [
                "current_balance",
                "enable_balance",
                "fetch_balance",
                "market_value",
                "asset_balance",
                "av_buy_price",
                "cost_price",
                "income_balance",
                "market_value",
                "entrust_price",
                "business_price",
                "business_balance",
                "fare1",
                "occur_balance",
                "farex",
                "fare0",
                "occur_amount",
                "post_balance",
                "fare2",
                "fare3",
                "资金余额",
                "可用资金",
                "参考市值",
                "总资产",
                "股份参考盈亏",
                "委托价格",
                "成交价格",
                "成交金额",
                "参考盈亏",
                "参考成本价",
                "参考市价",
                "参考市值"
            ]
        }
    }

    public_key = '-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDHdsyxT66pDG4p73yope7jxA92\nc0AT4qIJ' \
            '/xtbBcHkFPK77upnsfDTJiVEuQDH+MiMeb+XhCLNKZGp0yaUU6GlxZdp\n+nLW8b7Kmijr3iepaDhcbVTsYBWchaWUXauj9Lrhz58' \
            '/6AE/NF0aMolxIGpsi+ST\n2hSHPu3GSXMdhPCkWQIDAQAB\n-----END PUBLIC KEY----- '

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/536.66",
        "Host": "jywg.18.cn",
        "Pragma": "no-cache",
        "Connection": "keep-alive",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
        "Cache-Control": "no-cache",
        "Referer": "https://jywg.18.cn/Login?el=1&clear=1",
        "X-Requested-With": "XMLHttpRequest",
    }

    password = '561128'
    user = '540830230980'