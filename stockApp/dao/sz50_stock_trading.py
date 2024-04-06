# -*- coding: utf-8 -*-
import json
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
from stock_app.__init__ import db, utils
from stock_app.model.base import Base

class SZ50StockTrading(Base):
    __tablename__ = 'sz50_stock_trading'
    __table_args__ = {'extend_existing': True, 'schema': 'stock'}

    # 日期	开盘价	最高价	最低价	收盘价	涨跌额	涨跌幅(%)	成交量(股)	成交金额(元)
    uuid = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)  # id 整型，主键，自增，唯一
    trading_date = db.Column(db.String(50), nullable=False, comment="日交易日期")
    open_price = db.Column(db.Numeric, nullable=False, comment="开盘价")
    close_price = db.Column(db.Numeric, nullable=False, comment="收盘价")
    high_price = db.Column(db.Numeric, nullable=False, comment="最高价")
    low_price = db.Column(db.Numeric, nullable=False, comment="最低价")
    change_amount = db.Column(db.Numeric, nullable=False, comment="涨跌额")
    chg_pct = db.Column(db.Numeric, nullable=False, comment="涨跌幅(%)")
    volume = db.Column(db.Numeric, nullable=False, comment="成交量(股)")
    turnover = db.Column(db.Numeric, nullable=False, comment="成交金额(元)")

    def __repr__(self):
        obj = {
            "uuid": self.uuid,
            "trading_date": self.trading_date,
            "open_price": self.open_price,
            "close_price": self.close_price,
            "high_price": self.high_price,
            "low_price": self.low_price,
            "change_amount": self.change_amount,
            "chg_pct": self.chg_pct,
            "volume": self.volume,
            "turnover": self.turnover
        }
        return json.dumps(obj, cls=utils["common"].ComplexEncoder)

    @staticmethod
    def add_new_sz50_stock(**kwargs):
        tmp = SZ50StockTrading()
        for key, value in kwargs.items():
            if hasattr(tmp, key) and key != 'uuid':
                setattr(tmp, key, value)
        db.session.add(tmp)
        db.session.flush()
        uuid = tmp.uuid
        db.session.commit()
        return uuid


    @staticmethod
    def get_sz50_history_trading(start_date, end_date):
        return SZ50StockTrading.query.filter(db.and_(
                db.column('trading_date') >= start_date,
                db.column('trading_date') <= end_date
        )).order_by(db.text("trading_date desc")).all()


