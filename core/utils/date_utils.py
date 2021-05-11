# -*- coding: utf-8 -*-
import datetime

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
    return datetime.datetime.strptime(day_distance, "%Y-%m-%d")


def data_interval(data1, data2):
    d1 = datetime.datetime.strptime(data1, "%Y-%m-%d")
    d2 = datetime.datetime.strptime(data2, "%Y-%m-%d")
    delta = d1 - d2
    return delta.days
