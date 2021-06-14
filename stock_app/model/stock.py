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
    is_st = db.Column(db.CHAR, unique=True, nullable=False, server_default="", comment="是否ST 1是，0否")
    trade_status = db.Column(db.CHAR, unique=True, nullable=False, server_default="", comment="是否停牌 1：正常交易 0：停牌")
    a_capital_total = db.Column(db.Integer, unique=True, nullable=False, server_default="", comment="流通A股(亿股)")

    def __repr__(self):
        obj = {
            "uuid": self.uuid,
            "name": self.name,
            "code": self.code,
            "is_st": self.is_st,
            "trade_status": self.trade_status,
            "a_capital_total": self.a_capital_total
        }
        return json.dumps(obj, cls=utils["common"].ComplexEncoder)

    def get_stock_info(self, code):
        return self.query.filter(Stock.code == code).first()

    @staticmethod
    def get_stock_info_by_sql(code, cols=None):
        name = Stock.__tablename__
        schema = Stock.__table_args__
        schema = schema['schema']
        tbl_name = '{schema}.{table}'.format(schema=schema, table=name)
        if cols:
            cols = ['{}.{}'.format(tbl_name, col) for col in cols]
            cols = ','.join(cols)
        else:
            cols = '*'
        result = db.session.connection().execute(db.text(
            'select {cols} from {tbl_name} where code = :code'.format(
                cols=cols, tbl_name=tbl_name)),
            {'code': code})
        return result.fetchone()

    def get_all_stock_codes(self):
        return self.query.all()

    @staticmethod
    def add_new_stock(name, code, a_capital_total=0, is_st=False, trade_status=True):
        tmp = Stock()
        tmp.name = name
        tmp.code = code
        tmp.is_st = is_st
        tmp.trade_status = trade_status
        tmp.a_capital_total = a_capital_total
        db.session.add(tmp)
        db.session.flush()
        uuid = tmp.uuid
        db.session.commit()
        return uuid

    @staticmethod
    def update_stock_st_status(code, a_capital_total, is_st, trade_status):
        num_rows_updated = Stock.query.filter_by(code=code).update(dict(is_st=is_st, trade_status=trade_status, a_capital_total=a_capital_total))
        db.session.commit()
        return num_rows_updated

    @staticmethod
    def get_total(*args):
        if args:
            return db.session.query(db.func.count(Stock.uuid)).filter(*args).scalar()
        return db.session.query(db.func.count(Stock.uuid)).scalar()

    def del_stock(self, code):
        return self.query.filter(Stock.code == code).delete()

    @staticmethod
    def get_stock_list_by_codes(codes):
        return Stock.query.filter(Stock.code.in_(codes)).order_by(Stock.id.desc()).all()




if __name__ == "__main__":
    stock = Stock()
    count = stock.get_total()
    print(count)