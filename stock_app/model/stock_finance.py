# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
import json
from stock_app.__init__ import db, utils
from stock_app.model.base import Base


class StockFinance(Base):

    __tablename__ = 'stock_finance'
    __table_args__ = {'extend_existing': True, 'schema': 'stock'}

    uuid = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)  # id 整型，主键，自增，唯一
    stock_code = db.Column(db.String(50), unique=True, nullable=False, server_default="", comment="股票代码")
    date = db.Column(db.String(50), nullable=False, comment="日交易日期")
    assets = db.Column(db.Numeric, nullable=False, comment="股东权益不含少数股东权益")

    def __repr__(self):
        obj = {
            "uuid": self.uuid,
            "stock_code": self.stock_code,
            "date": self.date,
            "assets": self.assets
        }
        return json.dumps(obj, cls=utils["common"].ComplexEncoder)

    @staticmethod
    def add_stock_finance(stock_code, date, assets):
        tmp = StockFinance()
        tmp.stock_code = stock_code
        tmp.date = date
        tmp.assets = assets
        db.session.add(tmp)
        db.session.flush()
        uuid = tmp.uuid
        db.session.commit()
        return uuid

    @staticmethod
    def get_stock_finance_by_code_date(code, date, cols=None):
        name = StockFinance.__tablename__
        schema = StockFinance.__table_args__
        schema = schema['schema']
        tbl_name = '{schema}.{table}'.format(schema=schema, table=name)
        if cols:
            cols = ['{}.{}'.format(tbl_name, col) for col in cols]
            cols = ','.join(cols)
        else:
            cols = '*'
        result = db.session.connection().execute(db.text(
            'select {cols} from {tbl_name} where stock_code=:code and date=:date order by date desc'.format(
                cols=cols, tbl_name=tbl_name)),
            {'code': code, 'date': date})
        return result.fetchone()


    def get_stock_finance_by_code(self, code):
        return self.query.filter(StockFinance.stock_code == code).all()

    @staticmethod
    def update_stock_finance(code, date, assets):
        num_rows_updated = StockFinance.query.filter_by(stock_code=code).update(
            dict(date=date, assets=assets))
        db.session.commit()
        return num_rows_updated


    def get_stock_finances(self, code, year, season):
        year = str(year)
        if season == 1:
            date = year + '-03-31'
        if season == 2:
            date = year + '-06-30'
        if season == 3:
            date = year + '-09-30'
        if season == 4:
            date = year + '-12-31'
        return self.query.filter(db.and_(StockFinance.stock_code == code, StockFinance.date == date)).first()

    def get_stock_finances2(self, code, date):
        date_arr = date.split('-')
        season = int(date_arr[1])//4 + 1
        year = date_arr[0]
        return self.get_stock_finances(code, year, season)




if __name__ == "__main__":
    pass