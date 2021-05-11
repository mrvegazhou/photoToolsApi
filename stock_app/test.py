# -*- coding: utf-8 -*-
from model import stock, day_trading

from sqlalchemy import Column,String,create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
import datetime,time
import akshare as ak
from chinese_calendar import is_workday, is_holiday

if __name__ == "__main__":
    engine = create_engine('postgresql+psycopg2://postgres:root@127.0.0.1:5432/stock', echo=True)
    DBsession = sessionmaker(bind=engine)
    session = DBsession()
    session.execute("SET search_path TO stock")
    query = session.query(stock.Stock)
    print(session.query(func.count(stock.Stock.uuid)).one()[0])

    stock = stock.Stock()
    codes_list = stock.get_all_stock_codes()
    for code in codes_list:
        tmp = ak.stock_zh_a_daily(code.code, "20100131", "20210506", adjust="hfq")
        for index, row in tmp.iterrows():
            obj = day_trading.DayTrading.model(code.code)
            obj.stock_code = code.code
            obj.trading_date = index
            obj.close_price = row.close
            obj.high_price = row.high
            obj.low_price = row.low
            obj.open_price = row.open
            obj.volume = row.volume
            obj.outstanding_share = row.outstanding_share
            obj.turnover = row.turnover
            session.add(obj)
            session.commit()

    # obj = day_trading.DayTrading
    # code = "sh600000"
    # start_date = "2021-04-01"
    # end_date = "2021-04-02"
    # pagination = obj.query.filter(obj.stock_code == code).filter(obj.trading_date >= start_date, obj.trading_date <= end_date).order_by(obj.trading_date.desc()).all()
    # print(pagination)


