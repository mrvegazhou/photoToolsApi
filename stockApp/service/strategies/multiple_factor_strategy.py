# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
import pandas as pd
from stock_app.api.request_api import api_all_fundamental_datas, api_stock_financial_analysis_indicator
from stock_app.service.base_strategy import BaseStratege
import numpy as np


class MultipleFactorStratege(BaseStratege):

    '''
    盈利因子：
        销售净利率 = 净利润 / 主营业务收入
        毛利率 = 毛利润 / 主营业务收入
        ROE = 归属母公司股东净利润／期末归属母公司股东的权益
        ROA = 利润总额 / (期初资产总额+期末资产总额)/2
    '''
    @staticmethod
    def get_gain_factor(df):
        new_df = pd.DataFrame()
        new_df["np_margin"] = df['npMargin']
        new_df['gp_margin'] = df['gpMargin']
        # 净资产收益率
        new_df['ROE'] = df['dupontROE']
        # 总资产周转率
        new_df['ROA'] = df['AssetTurnRatio']
        return new_df


    '''
    成长因子:
        股东权益增长率 = (本期股东权益-上年同期股东权益)/(上年同期股东权益)
        总资产增长率 = (本期总资产-上年同期总资产)/(上年同期总资产)
        净利润增长率 = (本期净利润-上年同期净利润)/(上年同期净利润)
        每股净资产增长率 = (本期股东权益/本期总股本-上年同期股东权益/上年同期总股本)/(上年同期股东权益/上年同期总股本)
        EPS 增长率 = (本期净利润/本期总股本-上年同期净利润/上年同期总股本)/(上年同期净利润/上年同期总股本)
        ROE 增长率 = (本期净利润/本期股东权益-上年同期净利润/上年同期股东权益)/(上年同期净利润/上年同期股东权益)
    '''
    @staticmethod
    def get_growth_factor(df):
        new_df = pd.DataFrame()
        # 基本每股收益同比增长率
        new_df["EPS_rate"] = df['YOYEPSBasic']
        new_df["growth_rate_of_total_assets"] = df['总资产增长率(%)']
        new_df["growth_rate_of_net_profit"] = df['净利润增长率(%)']
        new_df["ROE_rate"] = df['roeAvg']
        return new_df


    '''
    杠杆因子：
        资产负债率 = 负债总额/资产总额
        长期负债比率 = 长期负债/总资产
        每股负债比 = 负债总额/总股本
        流动负债率 = 流动负债/总负债
    '''
    @staticmethod
    def get_leverage_factor(df):
        new_df = pd.DataFrame()
        # 资产负债率
        new_df["liability_to_asset"] = df['liabilityToAsset']
        # 长期负债比率
        new_df["long_term_debt_ratio"] = df['长期负债比率(%)']
        return new_df


    '''
    流动因子:
        1个月成交金额( 换成 一个季度的成交金额均值 )
        近3个月平均成交量
        换手率
    '''
    @staticmethod
    def get_flow_factor(code, year, quarter=1):
        volume_avg, amount_avg, turn_avg = MultipleFactorStratege.get_vol_handoff_quarter_avg(code, year, quarter=quarter)
        new_df = pd.DataFrame()
        # 3个月成交金额
        new_df['amount_quarter_avg'] = pd.Series(amount_avg)
        # 近3个月平均成交量
        new_df['volume_quarter_avg'] = pd.Series(volume_avg)
        # 换手率
        new_df['turn_quarter_avg'] = pd.Series(turn_avg)
        return new_df



    # 合并所有基本面信息
    @staticmethod
    def get_all_financial_report_datas(code, year, quarter):
        one_df = api_stock_financial_analysis_indicator(code[2:len(code)], year=year, quarter=quarter)
        one_df = one_df.reset_index()
        str_code = list(code)
        str_code.insert(2, '.')
        code = "".join(str_code)
        other_df = api_all_fundamental_datas(code, year, quarter)
        all_df = pd.concat([one_df, other_df], axis=1)

        gain_factor_df = MultipleFactorStratege.get_gain_factor(all_df)
        growth_factor_df = MultipleFactorStratege.get_growth_factor(all_df)
        leverage_factor_df = MultipleFactorStratege.get_leverage_factor(all_df)
        flow_factor_df = MultipleFactorStratege.get_flow_factor(code, year, quarter=quarter)

        data_curr_quarter = pd.concat([gain_factor_df, growth_factor_df, leverage_factor_df, flow_factor_df], axis=1)



if __name__ == "__main__":
    # https://github.com/Brian378935268/multi-factors-model/blob/master/main.py
    from sklearn.model_selection import train_test_split
    from sklearn import linear_model
    from sklearn import metrics

    code = "sh600004"
    # ret = get_all_financial_report(code)
    # ret = api_stock_financial_abstract(code)
    # for item in ret.columns.values:
    #     print(item)

    # one = api_stock_financial_analysis_indicator(code, year=2020, quarter=2)
    # one = one.reset_index()
    #
    # ret = api_all_fundamental_datas('sh.600000', 2020, 2)

    # get_all_financial_report_datas('sh600004', 2020, 1)

    class Para():
        month_in_sample = range(1, 10)  # 样本内数据
        month_test = range(142, 243 + 1)  # 样本外数据
        percent_select = [0.2, 0.2]  # 正例和反例数据的比例
        percent_cv = 0.1  # 试题比例
        seed = 45  # 随机数种子点
        logi_C = 0.0005  # 置信度
        n_stock = 3625  # 现今股票数
        n_stock_select = 10  # 选出股票数
        parameters = ('A', 'B', 'C', 'return')
    para = Para()
    dates = pd.date_range('20130101', periods=10)

    for i_month in para.month_in_sample:
        data_curr_month = pd.DataFrame(np.random.rand(10, 4).reshape((10, 4)), index=dates, columns=['A', 'B', 'C', 'return'])
        data_curr_month['return_bin'] = np.nan  # 加入判定列，默认设为空
        data_curr_month = data_curr_month.sort_values(by='return', ascending=False)  # 按return列排序，降序

        n_stock = data_curr_month.shape[0]  # 样本内股票数
        n_stock_select = np.multiply(n_stock, para.percent_select)  # 取样本前后比例的“显著”样本参与训练
        n_stock_select = np.around(n_stock_select)  # 取整
        n_stock_select = n_stock_select.astype(int)  # 转化为int

        data_curr_month.iloc[:n_stock_select[0], -1] = 1  # 打标签
        data_curr_month.iloc[-n_stock_select[0]:, -1] = 0  # 打标签
        data_curr_month = data_curr_month.dropna()  # 去除中间部分表现平平的股票

        if i_month == para.month_in_sample[0]:
            data_in_sample = data_curr_month
        else:
            data_in_sample = data_in_sample.append(data_curr_month)

    print(data_in_sample)
    '''将样本内数据集拆分：训练集+验证集，进行训练'''
    x_in_sample = data_in_sample.loc[:, para.parameters]
    # 拆分所需的特征因子（列数据），定义为x
    y_in_sample = data_in_sample.loc[:, 'return_bin']

    x_train, x_cv, y_train, y_cv = train_test_split(x_in_sample, y_in_sample, test_size=para.percent_cv, random_state=para.seed)
    model = linear_model.LogisticRegression(C=para.logi_C)
    # 设置模型：线性回归 后面可以尝试SVM模型、SGD模型
    model.fit(x_train, y_train)

    '''训练结果检验'''
    y_pred_train = model.predict(x_train)  # 训练集拟合结果
    accuracy_score_train = metrics.accuracy_score(y_train, y_pred_train)  # 训练集拟合正确率
    y_pred_cv = model.predict(x_cv)  # 验证集拟合结果
    accuracy_score_cv = metrics.accuracy_score(y_cv, y_pred_cv)  # 验证集拟合准确率



