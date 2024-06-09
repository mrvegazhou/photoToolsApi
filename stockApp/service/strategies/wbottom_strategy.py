# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
from stock_app.service.base_strategy import BaseStrategy
from stock_app.service.MACD_strategy import MACDStragety
import operator
import datetime


class WBottomStragete(BaseStrategy):
    min_interval = 0
    max_interval = min_interval
    neck = 10
    start_date = None
    end_date = None

    @classmethod
    def init(cls, min_interval, start_date, end_date):
        # 将大区间分为N个小区间
        cls.min_interval = min_interval
        # 大区间
        cls.max_interval = 2 * min_interval
        cls.neck = 10
        cls.start_date = start_date
        cls.end_date = end_date

    @staticmethod
    def get_w_bottom(df, code):
        if df.empty:
            return

        # 交易日期
        trade_day = df['date']

        # 收盘价 最高价 最低价 成交额
        low_price = df['low']
        high_price = df['high']
        close_price = df['close']
        amount = df['volume']

        # macd指标
        MACDStragety.set_MACD(df)
        macd = df['MACD']

        cur_close = close_price.iloc[-1]
        cur_low = low_price.iloc[-1]
        cur_trade_day = trade_day.iloc[-1]

        # 每个小区间内的最低价
        len_low = len(low_price)

        # 左底最低价格
        bottom1 = 0
        # 左底在原始数据中的位置
        bottom1_idx = 0

        # 右底最低价格
        bottom2 = 0
        # 右底在原始数据中的位置
        bottom2_idx = 0

        if len_low < WBottomStragete.max_interval:
            return None

        # 取最近一段固定时间作为小区间，找双底；
        # 算法描述：
        # 1. 找左区域的极小值
        # 2. 找右区域的极小值
        # 3. 找左底与右底之间区域的极大值
        # 4. 比较左底与右底的涨幅，是否相差<3%
        # 5. 比较左底与右底的macd值，是否形成底背离
        # 6. 终点日期收盘价，是否突破颈线位; 并且最低点在颈线位下方
        # 6.1 右区间的极大值，必须小于当日的收盘价
        # 实践出真理
        # 突破颈线位时，连续三天温和放量，回踩重要支撑位：ma5，ma10，颈线位等，缩量
        # 以下条件可选
        # 7. 比较左底与右底的成交额，是否左底成交额>右底成交额
        # 8. 比较左底与极大值之间涨跌幅，是否>N%(判断颈线位幅度)
        # 9. 比较左底与右底之间，是否出现过涨停(判断股性活跃程度)
        # 10. 其他
        # 当前计算区间范围，左索引，右索引
        '''
        |---------------------------------|
        |             大区间              |
        |----------------|----------------|
        |     小区间1     |     小区间2     |
        |----------------|----------------|
        左索引        右索引
        '''
        for i in range(len_low - WBottomStragete.max_interval, len_low, WBottomStragete.min_interval):
            idx_left = i
            idx_right = i + WBottomStragete.min_interval
            interval_arrary = low_price[idx_left:idx_right]
            # 获取大区间数组中的极小值，以及对应的索引号
            min_index, min_number = min(enumerate(interval_arrary), key=operator.itemgetter(1))
            # 小区间索引，映射到原始数据的索引号
            index = min_index + idx_left

            # 小区间1的极小值，成为底1
            if bottom1 == 0:
                bottom1 = min_number
                bottom1_idx = index
            else:
                # 小区间2的极小值，成为底2
                bottom2 = min_number
                bottom2_idx = index

            # 底1和底2都找到
            if bottom1 != 0 and bottom2 != 0:
                # 计算两个底之间的百分比差值
                per = BaseStrategy.percentage(bottom2 - bottom1, bottom2)
                # 保留2位小数点
                per = round(per, 2)
                # 差距小于3个点，认为是双底
                if abs(per) < 3:
                    # 条件1 W底MACD值
                    bottom1_macd = macd[bottom1_idx]
                    bottom1_amount = amount[bottom1_idx]

                    bottom2_macd = macd[bottom2_idx]
                    bottom2_amount = amount[bottom2_idx]

                    # 条件2 macd底背离
                    b_macd_depart = False
                    if bottom1_macd is None or bottom2_macd is None:
                        continue

                    if bottom1_macd < bottom2_macd:
                        b_macd_depart = True
                    else:
                        continue

                    # 条件3 底2缩量
                    b_bottom2_lessamount = False
                    if bottom1_amount > bottom2_amount:
                        b_bottom2_lessamount = True
                    else:
                        continue

                    # 条件4 极大值与极小值之间，颈线位涨幅达到N%
                    b_neck = False
                    # 双底之间的区间极大值
                    w_interval = high_price[bottom1_idx:bottom2_idx]
                    max_index, max_number = max(enumerate(w_interval), key=operator.itemgetter(1))
                    # W底小区间索引映射成原始数据的索引
                    highest_idx = bottom1_idx + max_index
                    per_gain = BaseStrategy.percentage(max_number - bottom1, bottom1)
                    per_gain = round(per_gain, 2)

                    # 涨幅达到N%
                    if per_gain > WBottomStragete.neck:
                        b_neck = True
                    else:
                        continue

                    # 条件6.1，今天收盘价，大于右区间的极大值
                    # 右区间，底2到昨日
                    right_interval = high_price[bottom2_idx:-2]
                    if len(right_interval) == 0:
                        return

                    r_max_index, r_max_number = max(enumerate(right_interval), key=operator.itemgetter(1))
                    b_right_highest = False
                    if cur_close > r_max_number:
                        b_right_highest = True

                    # 条件6 今天收盘价突破颈线位
                    b_standup_neck = False
                    if cur_close > max_number and cur_low < max_number:
                        b_standup_neck = True

                    if b_macd_depart and b_bottom2_lessamount and b_neck and b_standup_neck and b_right_highest:
                        print('******** ', code, ' *********')
                        print('小间距：', WBottomStragete.min_interval,
                              '起始时间:', trade_day[len_low - WBottomStragete.max_interval], '~', trade_day[len_low - 1])
                        print('价格间距 = ', per, '%')
                        print('底1：index=', bottom1_idx, '  price=', bottom1, ' trade day=', trade_day[bottom1_idx])
                        print('底2：index=', bottom2_idx, '  price=', bottom2, ' trade day=', trade_day[bottom2_idx])


    @staticmethod
    def process():
        try:
            if WBottomStragete.start_date is None or WBottomStragete.end_date is None:
                raise ValueError("日期为空")
            starttime = datetime.datetime.now()
            stocks = BaseStrategy.get_all_stocks_df()
            for index, stock in stocks.iterrows():
                print(stock.code)
                # 加载日交易记录
                all_stock_kdata = BaseStrategy.get_stock_special_indicators(stock.code, WBottomStragete.start_date, WBottomStragete.end_date)
                # 交易日小于60日，不处理
                if all_stock_kdata is None or len(all_stock_kdata) < 60:
                    print(stock['code'], 'is empty! --- wbottom.py Process')
                    continue
                all_stock_kdata = all_stock_kdata.reset_index()
                WBottomStragete.get_w_bottom(all_stock_kdata, stock.code)

            endtime = datetime.datetime.now()
            times = (endtime - starttime).seconds
            print('wbottom Process for code 用时(秒)：', times)
        except ValueError as e:
            print("引发异常：", repr(e)+" | code:"+stock.code)


if __name__ == "__main__":
    WBottomStragete.init(10, '20200110', '20200510')
    WBottomStragete.process()