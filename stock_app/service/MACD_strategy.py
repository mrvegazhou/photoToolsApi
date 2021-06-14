# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
import talib
import numpy as np
from stock_app.service.base_strategy import BaseStrategy


class MACDStragety(BaseStrategy):

    '''
    根据 ma_list 计算 ma 数值 # 5, 10, 20, 43, 60
    '''

    @staticmethod
    def calc_ma(df, ma_list):
        try:
            for ma in ma_list:
                df['MA%d' % ma] = talib.SMA(df['close'].values, ma)
        except Exception as e:
            print(e)
        return df


    @staticmethod
    def set_MACD(df):
        # 5日均线，下同
        df['MA5'] = talib.SMA(df['close'], timeperiod=5)
        df['MA10'] = talib.SMA(df['close'], timeperiod=10)
        df['MA20'] = talib.SMA(df['close'], timeperiod=20)
        df = MACDStragety.calc_ma(df, [5, 10, 20, 43, 60])
        # macd = 12 天 EMA - 26 天 EMA
        df['DIFF'], df['DEA'], df['MACD'] = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
        df['MACD'] = df['MACD'] * 2
        return df


    @staticmethod
    def get_MACD(df):

        MACDStragety.set_MACD(df)

        df['MACD_buy'] = 0
        macd_position = df['DIFF'] > df['DEA']
        df.loc[macd_position[(macd_position == True) & (macd_position.shift() == False)].index, 'MACD_buy'] = 1
        df.loc[macd_position[(macd_position == False) & (macd_position.shift() == True)].index, 'MACD_buy'] = -1

        # 5日线上穿10日线：
        df['M5_cross_M10'] = 0
        ma_position = df['MA5'] > df['MA10']
        df.loc[ma_position[(ma_position == True) & (ma_position.shift() == False)].index, 'M5_cross_M10'] = 1
        return df


    # 判断是否为多头排列
    @staticmethod
    def get_MACD_arrangement(df):
        ma_arrangement_position = df['MA5'] > df['MA10'] & df['MA10'] > df['MA20'] & df['MA20'] > df['MA43'] & df['MA43'] > df['MA60']
        df['MACD_arrangement_sign'] = -1
        df.loc[(ma_arrangement_position == True).index, 'MACD_arrangement_sign'] = 1
        return df


    # 暂时用talib公式代替
    @staticmethod
    def get_dif_dea(df):
        data = np.array(df.close)
        ndata = len(data)
        m, n, T = 12, 26, 9
        EMA1 = np.copy(data)
        EMA2 = np.copy(data)
        f1 = (m - 1) / (m + 1)
        f2 = (n - 1) / (n + 1)
        f3 = (T - 1) / (T + 1)
        for i in range(1, ndata):
            EMA1[i] = EMA1[i - 1] * f1 + EMA1[i] * (1 - f1)
            EMA2[i] = EMA2[i - 1] * f2 + EMA2[i] * (1 - f2)
        DIF = EMA1 - EMA2
        df['DIF'] = DIF
        DEA = np.copy(DIF)
        for i in range(1, ndata):
            DEA[i] = DEA[i - 1] * f3 + DEA[i] * (1 - f3)
        df['DEA'] = DEA

