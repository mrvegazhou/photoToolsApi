# -*- coding: utf-8 -*-
import datetime
import calendar

# 返回包括此月份的前12个月
def get_one_year_month_list(a):
    year_now = int(a.split("-")[0])
    month_now = int(a.split("-")[1])
    res_list = []
    if month_now == 12:
        for i in range(9):
            res_list.append(str(year_now) + "-" + "0" + str(i + 1))
        for i in range(3):
            res_list.append(str(year_now) + "-" + str(i + 1))
    else:
        month_begin = month_now + 1
        month_before_num = 12 - month_now
        for i in range(month_before_num):
            res_list.append(str(year_now - 1) + "-" + str("%02d" % (month_begin + i)))
        for i in range(12 - month_before_num):
            res_list.append(str(year_now) + "-" + str("%02d" % (i + 1)))
    return res_list


def skip_date(date, days):
    now = datetime.date(*map(int, date.split("-")))
    day_distance = datetime.timedelta(days=days)
    day_distance = str(now - day_distance)
    return datetime.datetime.strftime(datetime.datetime.strptime(day_distance, "%Y-%m-%d"), "%Y-%m-%d")


def data_interval(data1, data2):
    d1 = datetime.datetime.strptime(data1, "%Y-%m-%d")
    d2 = datetime.datetime.strptime(data2, "%Y-%m-%d")
    delta = d1 - d2
    return delta.days

def get_now_date():
    return datetime.datetime.now().strftime('%Y-%m-%d')

# 获取第一天
def get_first_day(year, month):
    # 获取当前月的第一天的星期和当月总天数
    return datetime.date(year, month, day=1)



# 获取最后一天
def get_last_day(year, month):
    weekDay, monthCountDay = calendar.monthrange(year, month)
    return datetime.date(year, month, day=monthCountDay)

# 当前第几季度
def get_quarter(date):
    return (date.month - 1) // 3 + 1

# 当前季度的第一日期
def get_first_day_of_the_quarter(date):
    quarter = get_quarter(date)
    return datetime.datetime(date.year, 3 * quarter - 2, 1)

# 当前季度的最后一日期
def get_last_day_of_the_quarter(date):
    quarter = get_quarter(date)
    month = 3 * quarter
    remaining = month // 12
    return datetime.datetime(date.year + remaining, month % 12 + 1, 1) + datetime.timedelta(days=-1)

def get_now():
    return datetime.datetime.now()