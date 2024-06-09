# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
import numpy as np
import pandas as pd
from stockApp.service.base_strategy import BaseStrategy
from stockApp.service.MACD_strategy import MACDStragety

# kdj金叉
def get_KDJ(df, approach=False, plus=False):
    if df is None or df.empty:
        return pd.DataFrame()
    low_list = df['low'].rolling(window=9).min()
    low_list.fillna(value=df['low'].expanding().min(), inplace=True)
    high_list = df['high'].rolling(window=9).max()
    high_list.fillna(value=df['high'].expanding().max(), inplace=True)
    rsv = (df['close'] - low_list) / (high_list - low_list) * 100
    df['KDJ_K'] = rsv.ewm(com=2).mean()
    df['KDJ_D'] = df['KDJ_K'].ewm(com=2).mean()
    df['KDJ_J'] = 3 * df['KDJ_K'] - 2 * df['KDJ_D']
    df['KDJ_buy'] = 0
    if approach:
        kdj_position = df['KDJ_K'] > df['KDJ_D']
        kdj_position_plus = (df['KDJ_J'].shift(2) <= 50) & (df['KDJ_J'].shift(1) <= 50)
        # 计算金叉之前的k-d的值
        tmp_df = df.loc[kdj_position[(kdj_position == True) & (kdj_position.shift() == False)].index, :]
        tmp_df['last_KDJ_K'] = tmp_df['KDJ_K'].shift(1)
        tmp_df['last_KDJ_D'] = tmp_df['KDJ_D'].shift(1)
        tmp_df = tmp_df[tmp_df['KDJ_K'] >= tmp_df['KDJ_D']]
        tmp_df['diff_KDJ'] = tmp_df['last_KDJ_K'] - tmp_df['last_KDJ_D']
        tmp_df.drop(tmp_df[np.isnan(tmp_df['diff_KDJ'])].index, inplace=True)
        min = tmp_df['diff_KDJ'].min()
        max = tmp_df['diff_KDJ'].max()
        mean = tmp_df['diff_KDJ'].mean()
        std = tmp_df['diff_KDJ'].std()


        # print(tmp_df[['diff_KDJ']].apply(lambda x: (x - x.min()) / (x.max() - x.min())).head())
        # tmp_df = tmp_df.append([{'diff_KDJ': 2000}], ignore_index=False)
        # diff = tmp_df[['diff_KDJ']].apply(lambda x: abs(x - x.mean()) / x.std()).mean()
        # print(diff[0])
        # kdj_position = df['KDJ_K'] < df['KDJ_D']
        # # df.loc[df[(df['KDJ_D']-df['KDJ_K'])<=diff].index, 'KDJ_buy'] = 1
        # df2 = df[((abs(df['KDJ_D']-df['KDJ_K']) - mean ) / std)<diff[0]]
        # print(((abs(df['KDJ_D']-df['KDJ_K']) - mean ) / std)<diff[0])
        # print(tmp_df[['diff_KDJ']].head())

    else:
        kdj_position = df['KDJ_K'] > df['KDJ_D']
        kdj_position_plus = (df['KDJ_J'].shift(2) <= 50) & (df['KDJ_J'].shift(1) <= 50)
    if plus:
        # day(-2).{KDJ_J}<20 and day(-1).{KDJ_J}<20 and day(0).{KDJ_J}-day(-1).{KDJ_J}>=40 and day(0).{Vol_Change}>=1
        kdj_position_plus = (df['KDJ_J'].shift(2) < 20) & (df['KDJ_J'].shift(1) < 20) & ((df['KDJ_J']-df['KDJ_J'].shift(1)) >= 40)
    df.loc[kdj_position[(kdj_position == True) & (kdj_position_plus == True) & (kdj_position.shift() == False)].index, 'KDJ_buy'] = 1
    df.loc[kdj_position[(kdj_position == False) & (kdj_position.shift() == True)].index, 'KDJ_buy'] = -1
    return df


if __name__ == "__main__":
    # import baostock as bs
    # import pandas as pd
    #
    # login_result = bs.login()
    # print(login_result.error_msg)
    # # 获取股票日K线数据
    # rs = bs.query_history_k_data('sz.002555',
    #                              "date,code,high,close,low,tradeStatus",
    #                              start_date='2021-02-01', end_date='2021-05-22',
    #                              frequency="d", adjustflag="3")
    # result_list = []
    # while (rs.error_code == '0') & rs.next():
    #     # 获取一条记录，将记录合并在一起
    #     result_list.append(rs.get_row_data())
    #
    # df_init = pd.DataFrame(result_list, columns=rs.fields)
    # # 剔除停盘数据
    # df_status = df_init[df_init['tradeStatus'] == '1']
    # low = df_status['low'].astype(float)
    # del df_status['low']
    # df_status.insert(0, 'low', low)
    # high = df_status['high'].astype(float)
    # del df_status['high']
    # df_status.insert(0, 'high', high)
    # close = df_status['close'].astype(float)
    # del df_status['close']
    # df_status.insert(0, 'close', close)

    df_codes = BaseStrategy.get_all_stocks_df()
    new_df = pd.DataFrame()
    for index, code in df_codes.iterrows():
        df = BaseStrategy.get_stock_special_indicators(code['code'], '20210523', '20210527')
        if not df.empty:
            df = MACDStragety.set_MACD(df)
            df_ret = get_KDJ(df, approach=False)
            buy = df_ret[df_ret['KDJ_buy'] == 1]
            if not buy.empty:
                print(code['code'], df_ret[df_ret['KDJ_buy'] == 1])
                new_df.append(df_ret[df_ret['KDJ_buy'] == 1])

    print(new_df)


    # data = np.arange(2, 14).reshape((3, 4))
    # print(data)
    # min_max = np.diff(np.sign(np.diff(data))).nonzero()[0] + 1
    # l_min = (np.diff(np.sign(np.diff(data))) > 0).nonzero()[0] + 1  # local min
    # l_max = (np.diff(np.sign(np.diff(data))) < 0).nonzero()[0] + 1
    # print(l_min)
