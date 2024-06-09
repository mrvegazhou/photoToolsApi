# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
from stock_app.service.base_strategy import BaseStrategy
from stock_app.model.stock_finance import StockFinance
from stock_app.model.day_trading import DayTrading
from stock_app.model.stock import Stock
from stock_app.api.request_api import api_sz50_stock, api_sz50_stock_trading_info
import pandas as pd
import numpy as np
from decimal import Decimal
from sklearn.linear_model import LinearRegression


# 市场资产组合(Rm− Rf)、市值因子(SMB)、账面市值比因子(HML)
class FamaFrench3Strategy(BaseStrategy):

    @staticmethod
    def get_date_list(code="sh600000"):
        cols = ['trading_date', 'close_price', 'high_price', 'low_price', 'open_price', 'volume', 'turnover', 'chg_pct',
                'outstanding_share']
        ret = DayTrading.get_stock_trading_list_by_SQL(code, "2009-01-01", "2020-05-10", cols)
        return pd.DataFrame(ret, columns=cols)

    @staticmethod
    def get_trading(start_date, end_date):
        stock_list = api_sz50_stock()
        stock_finance = StockFinance()
        frames_CL = []
        frames_MC = []
        frames_BM = []
        frames_DR = []
        for _, item in stock_list.iterrows():
            code = item.code
            code = code.replace(".", "")
            a_capital_total = Stock.get_stock_info_by_sql(code, ['a_capital_total'])
            # 时间格式：YYYY-MM-DD
            df = BaseStrategy.get_stock_day_trading(code, start_date, end_date)
            if not df.empty:
                df = df.set_index(['trading_date'])

                a_capital_total = Decimal(a_capital_total[0])
                df['market_cap'] = df['close_price'] * a_capital_total

                new_df = df.copy()
                new_df[code] = new_df['market_cap']
                frames_MC.append(new_df[code])

                new_df = df.copy()
                new_df[code] = new_df['close_price']
                frames_CL.append(new_df[code])

                # 获取 账面市值比bm
                df['bm'] = df.apply(lambda x: FamaFrench3Strategy.fun_apply(stock_finance, code, x), axis=1)
                new_df = df.copy()
                new_df[code] = new_df['bm']
                frames_BM.append(new_df[code])

                # 日收益率
                df['daily_return_rate'] = df['close_price'] / df.shift(1)['close_price'] - 1
                new_df = df.copy()
                new_df = new_df.fillna(0)
                new_df[code] = new_df['daily_return_rate']
                frames_DR.append(new_df[code])


        if frames_CL and frames_MC and frames_DR and frames_BM:
            result_CL = pd.concat(frames_CL, axis=1)
            result_MC = pd.concat(frames_MC, axis=1)
            result_DR = pd.concat(frames_DR, axis=1)
            result_BM = pd.concat(frames_BM, axis=1)
            result_CL.dropna(axis=1, how='any')
            result_MC.dropna(axis=1, how='any')
            result_BM.dropna(axis=1, how='any')
            result_DR.dropna(axis=1, how='any')
            return result_CL, result_MC, result_BM, result_DR
        else:
            none = pd.DataFrame()
            return none, none, none, none


    @staticmethod
    def fun_apply(stock_finance, code, x):
        info = stock_finance.get_stock_finances2(code, str(x.name))
        if info:
            return (info.assets / 10000) / Decimal(x['market_cap'])
        else:
            return 0


    # @staticmethod
    # def get_stock_datas(t, datelist):
    #     x = len(datelist[::t])
    #     dates = map(lambda item: item[0], datelist[::t])
    #     dates = list(dates)
    #     dates.sort()
    #     stock_df_CL_list = []
    #     stock_df_MC_list = []
    #     stock_df_DR_list = []
    #     stock_df_BM_list = []
    #     for i in range(0, x):
    #         if i == (x - 1):
    #             date1 = dates[i]
    #             date2 = pd.to_datetime("2021-05-20").date()
    #         else:
    #             date1 = dates[i]
    #             date2 = dates[i + 1]
    #         start_date = str(date1).split()[0]
    #         end_date = date2 if type(date2) is datetime.date else str(date2).split()[0]
    #         result_CL, result_MC, result_BM, result_DR = FamaFrench3Strategy.get_trading(start_date, end_date)
    #
    #         result_CL.dropna(axis=1, how='any')
    #         result_MC.dropna(axis=1, how='any')
    #         result_BM.dropna(axis=1, how='any')
    #         result_DR.dropna(axis=1, how='any')
    #
    #         stock_df_CL_list.append(result_CL)
    #         stock_df_MC_list.append(result_MC)
    #         stock_df_DR_list.append(result_BM)
    #         stock_df_BM_list.append(result_DR)
    #     return stock_df_CL_list, stock_df_MC_list, stock_df_DR_list, stock_df_BM_list


    # 获取上证50的日收益率
    @staticmethod
    def get_SZ50(start_date, end_date):
        sz50_df = api_sz50_stock_trading_info(start_date, end_date)
        sz50_df.index = pd.DatetimeIndex(sz50_df.index)
        return sz50_df[(sz50_df.index >= start_date) & (sz50_df.index <= end_date)].sort_index(axis=0, ascending=False)



    # 计算SMB HML RM
    @staticmethod
    def get_stock_MC_DR_CL_BM(start_date, end_date):
        result_CL, result_MC, result_BM, result_DR = FamaFrench3Strategy.get_trading('2010-01-10', '2010-05-10')
        if result_CL.empty:
            return None

        # 合并多余index
        result_CL = result_CL.loc[~result_CL.index.duplicated(keep='first')]
        result_MC = result_MC.loc[~result_MC.index.duplicated(keep='first')]
        result_BM = result_BM.loc[~result_BM.index.duplicated(keep='first')]
        result_DR = result_DR.loc[~result_DR.index.duplicated(keep='first')]

        stocks = result_CL.columns.values
        result_MC = result_MC.T
        result_BM = result_BM.T

        # 选取某一列作为基准
        result_MC = result_MC.iloc[:, 0:1]
        result_BM = result_BM.iloc[:, 0:1]

        # 取列名
        sort_name = result_MC.columns
        # 排序
        result_MC = result_MC.sort_values(by=sort_name[0])
        result_BM = result_BM.sort_values(by=sort_name[0])

        # 取当前股票总数
        amount = len(result_MC)

        # 选取大市值股票组合
        B = result_MC[int(amount - amount / 3):].index
        B = B.values

        # 选取小市值股票组合
        S = result_MC[:int(amount / 3)].index
        S = S.values

        # 选取高bm的股票组合
        H = result_BM[int(amount - amount / 3):].index
        H = H.values

        # 选取低bm的股票组合
        L = result_BM[:int(amount / 3)].index
        L = L.values

        # 基准收益率  上证50指数
        sz50_df = FamaFrench3Strategy.get_SZ50(start_date, end_date)

        # index交集
        intersection_index = list(set(result_DR.index.tolist()).intersection(set(sz50_df.index.tolist())))
        sz50_df = sz50_df[sz50_df.index.isin(intersection_index)]
        result_DR = result_DR[result_DR.index.isin(intersection_index)]

        # 求因子的值
        SMB = result_DR[S][1:].sum(axis=1) / len(S) - result_DR[B][1:].sum(axis=1) / len(B)
        HML = result_DR[H][1:].sum(axis=1) / len(H) - result_DR[L][1:].sum(axis=1) / len(L)

        RM = np.diff(np.log(sz50_df['收盘价'].values.astype(float))) - 0.04 / 252

        X = pd.DataFrame({"RM": RM, "SMB": SMB, "HML": HML})

        # 取前g.NoF个因子为策略因子
        factor_flag = ["RM", "SMB", "HML"]
        X = X[factor_flag]

        # 对样本数据进行线性回归并计算ai
        t_scores = [0.0] * amount
        # 循环依次计算股票的分数
        for i in range(0, amount):
            t_stock = stocks[i]
            t_r = FamaFrench3Strategy.linreg(X, result_DR[t_stock][1:].values.astype(float) - 0.04 / 252, len(factor_flag))
            t_scores[i] = t_r[0]

        # 这个scores就是alpha
        scores = pd.DataFrame({'code': stocks, 'score': t_scores})
        # 根据分数进行排序
        scores = scores.sort_values(by='score')
        return scores



    @staticmethod
    def linreg(X, Y, columns=3):
        X = np.array(X)
        Y = np.array(Y)
        if len(Y)>1:
            model = LinearRegression(fit_intercept=True)
            model.fit(X, Y)
            return model.intercept_, model.coef_
        else:
            return [float("nan")] * (columns + 1)



if __name__ == "__main__":
    # t = 63
    # datalist = FamaFrench3Strategy.get_date_list()
    # ret1 = FamaFrench3Strategy.get_SZ50('2010-01-10', '2010-02-10')
    # print(ret1)
    ret = FamaFrench3Strategy.get_stock_MC_DR_CL_BM('2010-01-10', '2010-02-10')

    # a = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    # b = np.array([1.2, 2.4, 3.3, 4.9, 6, 9, 11, 28, 29, 10, 11, 12])




