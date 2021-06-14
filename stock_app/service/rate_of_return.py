# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
import pandas as pd
import numpy as np

"""
:param date_line: 日期序列
:param capital_line: 账户价值序列
:return: 输出最大回撤及开始日期和结束日期
"""
# 计算最大回撤函数
def max_drawdown(date_line, capital_line):
    # 将数据序列合并为一个dataframe并按日期排序
    df = pd.DataFrame({'date': date_line, 'capital': capital_line})
    # 计算当日之前的账户最大价值
    df['max2here'] = pd.expanding_max(df['capital'])
    df['dd2here'] = df['capital'] / df['max2here'] - 1  # 计算当日的回撤
    # 计算最大回撤和结束时间
    temp = df.sort_values(by='dd2here').iloc[0][['date', 'dd2here']]
    max_dd = temp['dd2here']
    end_date = temp['date'].strftime('%Y-%m-%d')
    # 计算开始时间
    df = df[df['date'] <= end_date]
    start_date = df.sort_values(by='capital', ascending=False).iloc[0]['date'].strftime('%Y-%m-%d')

    print('最大回撤为：%f, 开始日期：%s, 结束日期：%s' % (max_dd, start_date, end_date))


"""
:param date_line: 日期序列
:param capital_line: 账户价值序列
:return: 输出在回测期间的年化收益率
"""
# 计算年化收益率函数
def annual_return(date_line, capital_line):
    # 将数据序列合并成dataframe并按日期排序
    df = pd.DataFrame({'date': date_line, 'capital': capital_line})
    # 计算年化收益率
    annual = (df['capital'].iloc[-1] / df['capital'].iloc[0]) ** (250 / len(df)) - 1
    print(annual)


"""
:param date_line: 日期序列
:param return_line: 账户日收益率序列
:return: 输出最大连续上涨天数和最大连续下跌天数
"""
# 计算最大连续上涨天数和最大连续下跌天数
def max_successive_up(date_line, return_line):
    df = pd.DataFrame({'date': date_line, 'rtn': return_line})
    # 新建一个全为空值的一列
    df['up'] = [np.nan] * len(df)
    # 当收益率大于0时，up取1，小于0时，up取0，等于0时采用前向差值
    df.loc[df['rtn'] > 0, 'up'] = 1
    df.loc[df['rtn'] < 0, 'up'] = 0
    df['up'].fillna(method='ffill', inplace=True)
    # 根据up这一列计算到某天为止连续上涨下跌的天数
    rtn_list = list(df['up'])
    successive_up_list = []
    num = 1
    for i in range(len(rtn_list)):
        if i == 0:
            successive_up_list.append(num)
        else:
            if (rtn_list[i] == rtn_list[i - 1] == 1) or (rtn_list[i] == rtn_list[i - 1] == 0):
                num += 1
            else:
                num = 1
            successive_up_list.append(num)
    # 将计算结果赋给新的一列'successive_up'
    df['successive_up'] = successive_up_list
    # 分别在上涨和下跌的两个dataframe里按照'successive_up'的值排序并取最大值
    max_successive_up = df[df['up'] == 1].sort_values(by='successive_up', ascending=False)['successive_up'].iloc[0]
    max_successive_down = df[df['up'] == 0].sort_values(by='successive_up', ascending=False)['successive_up'].iloc[0]
    print('最大连续上涨天数为：%d  最大连续下跌天数为：%d' % (max_successive_up, max_successive_down))


# 计算平均涨幅
def average_change(date_line, return_line):
    """
    :param date_line: 日期序列
    :param return_line: 账户日收益率序列
    :return: 输出平均涨幅
    """
    df = pd.DataFrame({'date': date_line, 'rtn': return_line})
    ave = df['rtn'].mean()
    print('平均涨幅为：%f' % ave)


# 计算上涨概率
def prob_up(date_line, return_line):
    """
    :param date_line: 日期序列
    :param return_line: 账户日收益率序列
    :return: 输出上涨概率
    """
    df = pd.DataFrame({'date': date_line, 'rtn': return_line})
    df.ix[df['rtn'] > 0, 'rtn'] = 1  # 收益率大于0的记为1
    df.ix[df['rtn'] <= 0, 'rtn'] = 0  # 收益率小于等于0的记为0
    # 统计1和0各出现的次数
    count = df['rtn'].value_counts()
    p_up = count.loc[1] / len(df.index)
    print('上涨概率为：%f' % p_up)


