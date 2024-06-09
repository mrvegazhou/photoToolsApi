# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
import talib
import pandas as pd
import numpy as np


# PDI--上升方向线 MDI--下降方向线 ADX--趋向线
def get_DMI(df, n=14):

    # 计算HD和LD值
    df['hd'] = df['high'] - df['high'].shift(1)
    df['ld'] = df['low'].shift(1) - df['low']

    # 计算TR值
    # 计算True Range (真实波幅） TR =∣最高价-最低价∣，∣最高价-昨收∣，∣昨收-最低价∣ 三者之中的最高值
    df['t1'] = df['high'] - df['low']
    df['t2'] = abs(df['high'] - df['close'].shift(1))
    df['t3'] = abs(df['close'].shift(1) - df['low'])

    df.loc[df['t1'] >= df['t2'], 'temp'] = df['t1']
    df.loc[df['t1'] < df['t2'], 'temp'] = df['t2']
    df.loc[df['temp'] < df['t3'], 'temp'] = df['t3']
    df = df.drop(['t1', 't2', 't3'], axis=1)

    # df['temp2'] = df['low'] - df['close'].shift(1)
    #
    # df.loc[df['temp1'] >= df['temp2'], 'temp'] = df['temp1']
    # df.loc[df['temp1'] < df['temp2'], 'temp'] = df['temp2']

    # df.fillna(0, inplace=True)

    df['tr'] = df['temp'].rolling(n).sum()
    df = df.drop(['temp'], axis=1)

    df.loc[(df['hd'] > 0) & (df['hd'] > df['ld']), 'hd1'] = df['hd']
    df['hd1'].fillna(0, inplace=True)

    df.loc[(df['ld'] > 0) & (df['ld'] > df['hd']), 'ld1'] = df['ld']
    df['ld1'].fillna(0, inplace=True)

    df['pdi'] = df['hd1'].rolling(n).sum() / df['tr'] * 100
    df['mdi'] = df['ld1'].rolling(n).sum() / df['tr'] * 100
    df = df.drop(['hd1', 'ld1', 'hd', 'tr', 'ld'], axis=1)

    if len(df['pdi']) > 10 or len(df['mdi']) > 10:
        # ADXR=（当日的ADX+前n日的ADX）÷ 2
        dx = abs((df['pdi'] - df['mdi'])) / (df['pdi'] + df['mdi']) * 100
        dx.fillna(0, inplace=True)
        df['adx'] = talib.SMA(dx, 10)
    else:
        df['adx'] = np.nan

    df["MDI_buy"] = 0
    # 当+DI上穿-DI，买入，信号为1
    df.loc[df['pdi'] > df['mdi'], 'MDI_buy'] = 1
    # 当+DI下穿-DI，卖空，信号为-1
    df.loc[df['pdi'] < df['mdi'], 'MDI_buy'] = -1

    print(df)
    return df


if __name__ == "__main__":
    pass