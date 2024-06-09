# coding:utf8
import pandas as pd
from jsonpath import jsonpath
from tqdm.auto import tqdm
from modules.dataLoader.config.stockDataConst import Constants, EastConfig
from modules.common.hepler import trans_num
from modules.common import session


class EastFinancialReport(object):
    '''flag:报表类型,默认输出业绩报表，注意flag或date输出也默认输出业绩报表
    '业绩报表'或'yjbb'：返回年报季报财务指标
    '业绩快报'或'yjkb'：返回市场最新业绩快报
    '业绩预告'或'yjyg'：返回市场最新业绩预告
    '资产负债表'或'zcfz'：返回最新资产负债指标
    '利润表'或'lrb'：返回最新利润表指标
    '现金流量表'或'xjll'：返回最新现金流量表指标
    date:报表日期，如‘20220630’，‘20220331’，默认当前最新季报（或半年报或年报）
    '''

    def __init__(self):
        self._session = session
        self._headers = EastConfig.request_header.value

    def get_financial_report_data(self, type, date=None):
        date = self.trans_date(date)
        if not date:
            return None
        if type in ['业绩快报', 'yjkb']:
            return self.get_stock_earnings_release(date=date)
        elif type in ['业绩预告', 'yjyg']:
            return self.get_stock_earnings_forcast(date=date)
        elif type in ['资产负债表','资产负债','zcfz','zcfzb']:
            return self.get_stock_balance_sheet(date=date)
        elif type in ['利润表', '利润', 'lr', 'lrb']:
            return self.get_stock_income_statement(date)
        elif type in ['现金流量表', '现金流量', 'xjll', 'xjllb']:
            return self.get_stock_cash_flow_statement(date)
        else:
            return self.get_stock_q_a_report(date)

    def get_stock_earnings_release(self, date=None):
        """
        获取东方财富年报季报-业绩快报
        http://data.eastmoney.com/bbsj/202003/yjkb.html
        date: 如"20220331", "20220630"
        """
        # date = self.trans_date(date)
        params = {
            "st": "UPDATE_DATE,SECURITY_CODE",
            "sr": "-1,-1",
            "ps": "5000",
            "p": "1",
            "type": "RPT_FCI_PERFORMANCEE",
            "sty": "ALL",
            "token": "894050c76af8597a853f5b408b759f5d",
            "filter": f"(REPORT_DATE='{'-'.join([date[:4], date[4:6], date[6:]])}')",
        }
        url = Constants.EARNINGS_RELEASE_URL.value
        res = self._session.get(url, params=params)
        data_json = res.json()
        page_num = data_json["result"]["pages"]
        old_cols = EastConfig.earnings_release_dict.value
        new_cols = [x for x in old_cols if x != '_']
        if page_num > 1:
            df = pd.DataFrame()
            for page in tqdm(range(1, page_num + 1), leave=True):
                params = {
                    "st": "UPDATE_DATE,SECURITY_CODE",
                    "sr": "-1,-1",
                    "ps": "5000",
                    "p": page,
                    "type": "RPT_FCI_PERFORMANCEE",
                    "sty": "ALL",
                    "token": "894050c76af8597a853f5b408b759f5d",
                    "filter": f"(REPORT_DATE='{'-'.join([date[:4], date[4:6], date[6:]])}')",
                }
                r = self._session.get(url, params=params)
                data_json = r.json()
                temp_df = pd.DataFrame(data_json["result"]["data"])
                temp_df.reset_index(inplace=True)
                temp_df["index"] = range(1, len(temp_df) + 1)
                df = pd.concat([df, temp_df], ignore_index=True)

            df.columns = old_cols
            df = df[new_cols]
            return df
        df2 = pd.DataFrame(data_json["result"]["data"])
        df2.reset_index(inplace=True)
        df2["index"] = range(1, len(df2) + 1)
        df2.columns = old_cols
        df2 = df2[new_cols]
        return df2

    def get_stock_earnings_forcast(self, date=None):
        url = Constants.EARNINGS_FORECAST_URL.value
        params = {
            "sortColumns": "NOTICE_DATE,SECURITY_CODE",
            "sortTypes": "-1,-1",
            "pageSize": "50",
            "pageNumber": "1",
            "reportName": "RPT_PUBLIC_OP_NEWPREDICT",
            "columns": "ALL",
            "token": "894050c76af8597a853f5b408b759f5d",
            "filter": f" (REPORT_DATE='{'-'.join([date[:4], date[4:6], date[6:]])}')",
        }
        res = self._session.get(url, params=params)
        data_json = res.json()
        df = pd.DataFrame()
        total_page = data_json["result"]["pages"]
        for page in tqdm(range(1, total_page + 1), leave=False):
            params = {
                "sortColumns": "NOTICE_DATE,SECURITY_CODE",
                "sortTypes": "-1,-1",
                "pageSize": "50",
                "pageNumber": page,
                "reportName": "RPT_PUBLIC_OP_NEWPREDICT",
                "columns": "ALL",
                "token": "894050c76af8597a853f5b408b759f5d",
                "filter": f" (REPORT_DATE='{'-'.join([date[:4], date[4:6], date[6:]])}')",
            }
            r = self._session.get(url, params=params)
            data_json = r.json()
            temp_df = pd.DataFrame(data_json["result"]["data"])
            df = pd.concat([df, temp_df], ignore_index=True)

        df.reset_index(inplace=True)
        df["index"] = range(1, len(df) + 1)

        earning_forcast_dict = EastConfig.earning_forcast_dict.value
        old_cols = earning_forcast_dict.values()
        new_cols = earning_forcast_dict.keys()

        df = df.rename(columns=dict(zip(old_cols, new_cols)))[new_cols]
        return df

    def get_stock_balance_sheet(self, date=None):
        """
        东方财富年报季报资产负债表
        http://data.eastmoney.com/bbsj/202003/zcfz.html
        date:如"20220331", "20220630",
        """
        url = Constants.BALANCE_SHEET_URL.value
        params = {
            "sortColumns": "NOTICE_DATE,SECURITY_CODE",
            "sortTypes": "-1,-1",
            "pageSize": "500",
            "pageNumber": "1",
            "reportName": "RPT_DMSK_FN_BALANCE",
            "columns": "ALL",
            "filter": f"""(SECURITY_TYPE_CODE in ("058001001","058001008"))(TRADE_MARKET_CODE!="069001017")(REPORT_DATE='{'-'.join([date[:4], date[4:6], date[6:]])}')""",
        }
        res = self._session.get(url, params=params)
        data_json = res.json()
        page_num = data_json["result"]["pages"]
        df = pd.DataFrame()
        for page in tqdm(range(1, page_num + 1), leave=False):
            params.update(
                {
                    "pageNumber": page,
                }
            )
            r = self._session.get(url, params=params)
            data_json = r.json()
            temp_df = pd.DataFrame(data_json["result"]["data"])
            df = pd.concat([df, temp_df], ignore_index=True)

        df.reset_index(inplace=True)
        df["index"] = df.index + 1
        df.columns = ["序号", "_", "代码", "_", "_", "简称", "_", "_", "_", "_", "_", "_",
                      "_", "公告日", "_", "总资产", "_", "货币资金", "_", "应收账款", "_", "存货", "_",
                      "总负债", "应付账款", "_", "预收账款", "_", "股东权益", "_", "总资产同比", "总负债同比",
                      "_", "资产负债率", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_",
                      "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", ]
        df = df[["代码", "简称", "货币资金", "应收账款", "存货", "总资产", "总资产同比",
                 "应付账款", "预收账款", "总负债", "总负债同比", "资产负债率", "股东权益", "公告日", ]]
        df["公告日"] = pd.to_datetime(df["公告日"]).dt.date
        cols = ['代码', '简称', '公告日', ]
        df = trans_num(df, cols).round(2)
        return df

    def get_stock_income_statement(self, date=None):
        """
           获取东方财富年报季报-利润表
           http://data.eastmoney.com/bbsj/202003/lrb.html
           date: 如"20220331", "20220630"
           """
        url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
        params = {
            "sortColumns": "NOTICE_DATE,SECURITY_CODE",
            "sortTypes": "-1,-1",
            "pageSize": "500",
            "pageNumber": "1",
            "reportName": "RPT_DMSK_FN_INCOME",
            "columns": "ALL",
            "filter": f"""(SECURITY_TYPE_CODE in ("058001001","058001008"))(TRADE_MARKET_CODE!="069001017")(REPORT_DATE='{'-'.join([date[:4], date[4:6], date[6:]])}')""",
        }
        res = self._session.get(url, params=params)
        data_json = res.json()
        page_num = data_json["result"]["pages"]
        df = pd.DataFrame()
        for page in tqdm(range(1, page_num + 1), leave=False):
            params.update(
                {
                    "pageNumber": page,
                }
            )
            r = self._session.get(url, params=params)
            data_json = r.json()
            temp_df = pd.DataFrame(data_json["result"]["data"])
            df = pd.concat([df, temp_df], ignore_index=True)

        df.reset_index(inplace=True)
        df["index"] = df.index + 1
        df.columns = ["序号", "_", "代码", "_", "_", "简称", "_", "_", "_", "_", "_", "_",
                      "_", "公告日", "_", "净利润", "营业总收入", "营业总支出", "_", "营业支出",
                      "_", "_", "销售费用", "管理费用", "财务费用", "营业利润", "利润总额",
                      "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_",
                      "营业总收入同比", "_", "净利润同比", "_", "_", ]

        df = df[["代码", "简称", "净利润", "净利润同比", "营业总收入", "营业总收入同比",
                 "营业支出", "销售费用", "管理费用", "财务费用", "营业总支出",
                 "营业利润", "利润总额", "公告日", ]]

        df["公告日"] = pd.to_datetime(df["公告日"]).dt.date
        cols = ['代码', '简称', '公告日', ]
        df = trans_num(df, cols).round(2)
        return df

    def get_stock_cash_flow_statement(self, date=None):
        """
            获取东方财富年报季报现金流量表
            http://data.eastmoney.com/bbsj/202003/xjll.html
            date: 如"20220331", "20220630"
            """
        url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
        params = {
            "sortColumns": "NOTICE_DATE,SECURITY_CODE",
            "sortTypes": "-1,-1",
            "pageSize": "500",
            "pageNumber": "1",
            "reportName": "RPT_DMSK_FN_CASHFLOW",
            "columns": "ALL",
            "filter": f"""(SECURITY_TYPE_CODE in ("058001001","058001008"))(TRADE_MARKET_CODE!="069001017")(REPORT_DATE='{'-'.join([date[:4], date[4:6], date[6:]])}')""",
        }
        res = self._session.get(url, params=params)
        data_json = res.json()
        page_num = data_json["result"]["pages"]
        df = pd.DataFrame()
        for page in tqdm(range(1, page_num + 1), leave=False):
            params.update(
                {
                    "pageNumber": page,
                }
            )
            r = self._session.get(url, params=params)
            data_json = r.json()
            temp_df = pd.DataFrame(data_json["result"]["data"])
            df = pd.concat([df, temp_df], ignore_index=True)

        df.reset_index(inplace=True)
        df["index"] = df.index + 1
        df.columns = ["序号", "_", "代码", "_", "_", "简称", "_", "_", "_", "_", "_", "_", "_",
                      "公告日", "_", "经营性现金流量净额", "经营性净现金流占比", "_", "_", "_", "_",
                      "投资性现金流量净额", "投资性净现金流占比", "_", "_", "_", "_",
                      "融资性现金流量净额", "融资性净现金流占比", "净现金流",
                      "净现金流同比增长", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_",
                      "_", "_", "_", "_", "_", "_", ]

        df = df[["代码", "简称", "净现金流", "净现金流同比增长", "经营性现金流量净额",
                 "经营性净现金流占比", "投资性现金流量净额", "投资性净现金流占比",
                 "融资性现金流量净额", "融资性净现金流占比", "公告日", ]]

        df["公告日"] = pd.to_datetime(df["公告日"]).dt.date
        cols = ['代码', '简称', '公告日', ]
        df = trans_num(df, cols).round(2)
        return df

    def get_stock_q_a_report(self, date=None):
        """
            东方财富年报季报业绩报表
            http://data.eastmoney.com/bbsj/202003/yjbb.html
            date: 如"20220331", "20220630"
            """
        url = "http://datacenter.eastmoney.com/api/data/get"
        params = {
            "st": "UPDATE_DATE,SECURITY_CODE",
            "sr": "-1,-1",
            "ps": "5000",
            "p": "1",
            "type": "RPT_LICO_FN_CPD",
            "sty": "ALL",
            "token": "894050c76af8597a853f5b408b759f5d",
            "filter": f"(REPORTDATE='{'-'.join([date[:4], date[4:6], date[6:]])}')",
        }
        res = self._session.get(url, params=params)
        data_json = res.json()
        page_num = data_json["result"]["pages"]
        df = pd.DataFrame()
        for page in tqdm(range(1, page_num + 1), leave=False):
            params = {
                "st": "UPDATE_DATE,SECURITY_CODE",
                "sr": "-1,-1",
                "ps": "500",
                "p": page,
                "type": "RPT_LICO_FN_CPD",
                "sty": "ALL",
                "token": "894050c76af8597a853f5b408b759f5d",
                "filter": f"(REPORTDATE='{'-'.join([date[:4], date[4:6], date[6:]])}')",
            }
            r = self._session.get(url, params=params)
            data_json2 = r.json()
            temp_df = pd.DataFrame(data_json2["result"]["data"])
            for col in temp_df.columns:
                if temp_df[col].isnull().all():
                    temp_df[col] = temp_df[col].fillna('')
            df = pd.concat([df, temp_df], ignore_index=True)

        df.reset_index(inplace=True)
        df["index"] = range(1, len(df) + 1)
        df.columns = ["序号", "代码", "简称", "_", "_", "_", "_", "最新公告日", "_", "每股收益",
                      "_", "营业收入", "净利润", "净资产收益率", "营业收入同比", "净利润同比", "每股净资产",
                      "每股经营现金流量", "销售毛利率", "营业收入季度环比", "净利润季度环比",
                      "_", "_", "行业", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", ]

        df = df[["代码", "简称", "每股收益", "营业收入", "营业收入同比", "营业收入季度环比",
                 "净利润", "净利润同比", "净利润季度环比", "每股净资产", "净资产收益率",
                 "每股经营现金流量", "销售毛利率", "行业", "最新公告日", ]]
        return df


    def trans_date(self, date=None):
        '''将日期格式'2022-09-30'转为'20220930'
        '''
        if date is None:
            date = self.latest_report_date()
        date = ''.join(date.split('-'))
        return date

    def latest_report_date(self):
        df = self.report_date()
        return df['报告日期'].iloc[0]

    # 获取沪深市场全部股票报告期信息
    def report_date(self):
        """
        获取沪深市场的全部股票报告期信息
        """
        fields = {
            'REPORT_DATE': '报告日期',
            'DATATYPE': '季报名称'
        }
        params = (
            ('type', 'RPT_LICO_FN_CPD_BBBQ'),
            ('sty', ','.join(fields.keys())),
            ('p', '1'),
            ('ps', '2000'),
        )
        url = Constants.ALL_STOCK_REPORT_URL.value
        response = self._session.get(
            url,
            headers=self._headers,
            params=params)
        try:
            items = jsonpath(response.json(), '$..data[:]')
            if not items:
                pd.DataFrame(columns=fields.values())
            df = pd.DataFrame(items)
            df = df.rename(columns=fields)
            df['报告日期'] = df['报告日期'].apply(lambda x: x.split()[0])
            return df
        except Exception as e:
            pd.DataFrame(columns=fields.values())