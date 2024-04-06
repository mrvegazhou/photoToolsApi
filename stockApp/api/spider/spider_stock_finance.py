# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import pandas as pd


#功能：获取指定股票日期的每日收盘价
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.1708.400 QQBrowser/9.5.9635.400'
}

#爬取财务数据 流通A股(亿股)
def spider_stock_capital(stock_code):

    url = 'http://quotes.money.163.com/f10/gdfx_'+stock_code+'.html#01d01'

    data = requests.get(url, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    table = soup.findAll('table', {'class': 'table_bg001 border_box'})[0]
    rows = table.findAll('tr')

    #rowsData = rowsData[rows[0:1],rows[9:10],rows[17:18]]
    #print(rows[0:1])
    #print(rowsData)#净利润和净资产
    #返回某股票的财务报表
    for row in rows[1:2]:
        csv_row = []
        for cell in row.findAll('td'):
            csv_row.append(cell.get_text().replace(',', ''))
    df = pd.DataFrame([csv_row[1]], columns=[csv_row[0]])
    return df, csv_row[0]



def spider_stock_data(stock_code, year, season):
    #字符化处理
    stockCodeStr = str(stock_code)
    yearStr = str(year)
    seasonStr = str(season)
    url = 'http://quotes.money.163.com/trade/lsjysj_' + stockCodeStr + '.html?year=' + yearStr + '&season=' + seasonStr

    data = requests.get(url, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    table = soup.findAll('table', {'class': 'table_bg001'})[0]
    rows = table.findAll('tr')
    #返回一个季度的交易数据
    ret = []
    dates = []
    for row in rows[:0:-1]:
        csv_row = []
        for cell in row.findAll('td'):
            csv_row.append(cell.get_text().replace(',', ''))

        dates.append(csv_row[0])
        ret.append(csv_row[1:])

    df = pd.DataFrame(ret, index = dates, columns = ['开盘价','最高价','最低价','收盘价','涨跌额','涨跌幅(%)','成交量(手)','成交金额(万元)','振幅(%)','换手率(%)'])
    return df

# 股东权益不含少数股东权益(万元)
def spider_stock_finance(stock_code):
    url = 'http://quotes.money.163.com/f10/zycwzb_' + stock_code + '.html#01c02'

    data = requests.get(url, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    table = soup.findAll('table', {'class': 'table_bg001 border_box limit_sale scr_table'})[0]
    rows = table.findAll('tr')

    # 返回某股票的财务报表
    csv_row1 = []
    for row in rows[0:1]:
        for cell in row.findAll('th'):
            csv_row1.append(cell.get_text().replace(',', ''))

    csv_row2 = []
    for row in rows[18:19]:
        for cell in row.findAll('td'):
            csv_row2.append(cell.get_text().replace(',', ''))

    df = pd.DataFrame(csv_row2, index = csv_row1, columns = ['assets'])
    return df


def spider_sz50(year, season):
    #字符化处理
    yearStr = str(year)
    seasonStr = str(season)
    url = 'http://quotes.money.163.com/trade/lsjysj_zhishu_000016.html?year=' + yearStr + '&season=' + seasonStr

    data = requests.get(url, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    table = soup.findAll('table', {'class': 'table_bg001 border_box limit_sale'})[0]
    rows = table.findAll('tr')
    #返回一个季度的交易数据
    ret = []
    dates = []
    for row in rows[:0:-1]:
        csv_row = []
        for cell in row.findAll('td'):
            csv_row.append(cell.get_text().replace(',', ''))
        dates.append(csv_row[0])
        ret.append(csv_row[1:])

    df = pd.DataFrame(ret, index=dates, columns=['开盘价', '最高价', '最低价', '收盘价', '涨跌额', '涨跌幅(%)', '成交量(手)', '成交金额(万元)'])
    return df



if __name__ == "__main__":
    # print(spider_stock_data('000550', 2010, 1))
    print(spider_sz50('2021', 1))
    # pass
