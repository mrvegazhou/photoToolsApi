# -*- coding: utf-8 -*-
import json
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
from stock_app.__init__ import db, utils
from stock_app.model.base import Base

class Stock(Base):
    __tablename__ = 'stock_info'
    __table_args__ = {'extend_existing': True, 'schema': 'stock'}

    uuid = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)  # id 整型，主键，自增，唯一
    name = db.Column(db.String(255), unique=True, nullable=False, server_default="", comment="股票名称")
    code = db.Column(db.String(50), unique=True, nullable=False, server_default="", comment="股票代码")

    def __repr__(self):
        obj = {
            "uuid": self.uuid,
            "name": self.name,
            "code": self.code
        }
        return json.dumps(obj, cls=utils["common"].ComplexEncoder)

    def get_stock_info(self, code):
        return self.query.filter(Stock.code == code).first()

    def get_all_stock_codes(self):
        return self.query.all()

    @staticmethod
    def add_new_stock(name, code):
        tmp = Stock()
        tmp.name = name
        tmp.code = code
        db.session.add(tmp)
        db.session.flush()
        uuid = tmp.uuid
        db.session.commit()
        return uuid

    @staticmethod
    def get_total(*args):
        if args:
            return db.session.query(db.func.count(Stock.uuid)).filter(*args).scalar()
        return db.session.query(db.func.count(Stock.uuid)).scalar()

    def del_stock(self, code):
        return self.query.filter(Stock.code == code).delete()

if __name__ == "__main__":
    stock = Stock()
    count = stock.get_total()
    print(count)