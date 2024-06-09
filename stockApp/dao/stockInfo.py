# -*- coding: utf-8 -*-
import json
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/stockApi")
from sqlalchemy import BigInteger, String, SmallInteger, Numeric, Date
from datetime import datetime, timezone
from stockApp import db, utils, func
from .base import Base
from core.log.logger import get_module_logger


class StockInfo(Base):

    __tablename__ = 'stock_info'
    __table_args__ = {'extend_existing': True, 'schema': 'stock'}

    uuid = db.Column(BigInteger, primary_key=True, autoincrement=True, unique=True)  # id 整型，主键，自增，唯一
    name = db.Column(String, unique=True, nullable=False, server_default="", comment="股票名称")
    code = db.Column(String, unique=True, nullable=False, server_default="", comment="股票代码")
    is_st = db.Column(SmallInteger, nullable=False, default=0, server_default=db.text("0"), comment="是否ST 1是，0否")
    is_suspended = db.Column(SmallInteger, nullable=False, default=1, server_default=db.text("1"), comment="是否停牌 1：正常交易 0：停牌")
    is_newly_issued = db.Column(SmallInteger, nullable=False, default=0, server_default=db.text("0"), comment="是否次新 1：是 0：否")
    total_market_value = db.Column(Numeric, nullable=False, server_default="", comment="总市值")
    floating_market_value = db.Column(Numeric, nullable=False, server_default="", comment="流通市值")
    total_share_capital = db.Column(Numeric, nullable=False, server_default="", comment="总股本")
    floating_shares = db.Column(Numeric, nullable=False, server_default="", comment="流通股")
    IPO_date = db.Column(Date, nullable=False, server_default="", comment="上市时间")
    industry = db.Column(String, nullable=False, server_default="", comment="所属行业")
    create_time = db.Column(db.DateTime(timezone=True), comment="创建时间", server_default=func.now(), default=datetime.now)

    def get_keys(self):
        return {
            "uuid": self.uuid,
            "name": self.name,
            "code": self.code,
            "is_st": self.is_st,
            "is_suspended": self.is_suspended,
            "is_newly_issued": self.is_newly_issued,
            "total_market_value": self.total_market_value,
            "floating_market_value": self.floating_market_value,
            "total_share_capital": self.total_share_capital,
            "floating_shares": self.floating_shares,
            "IPO_date": self.IPO_date,
            "industry": self.industry,
        }

    def __repr__(self):
        obj = StockInfo.get_keys(self)
        return json.dumps(obj, cls=utils["common"].ComplexEncoder)

    def get_stock_info(self, code):
        return self.query.filter(StockInfo.code == code).first()

    @staticmethod
    def get_tbl_name():
        name = StockInfo.__tablename__
        schema = StockInfo.__table_args__
        schema = schema['schema']
        tbl_name = '{schema}.{table}'.format(schema=schema, table=name)
        return tbl_name

    @staticmethod
    def get_stock_info_by_sql(code, cols=None):
        tbl_name = StockInfo.get_tbl_name()
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

    @staticmethod
    def get_stock_by_conds(filters):
        if not filters:
            return None
        return StockInfo.query.filter(*filters).order_by(StockInfo.uuid.asc()).all()

    def get_all_stock_codes(self):
        return self.query.all()

    @staticmethod
    def add_new_stock(obj):
        try:
            db.session.add(obj)
            db.session.commit()
            uuid = obj.uuid
            return uuid
        except Exception as e:
            print(e, obj)
            db.session.rollback()
        finally:
            db.session.close()

    @staticmethod
    def add_new_stock_list(objs):
        try:
            info_to_add = []
            for obj in objs:
                info_to_add.append(obj)
            db.session.add_all(obj)
            db.session.commit()
            uuids = [obj.uuid for obj in info_to_add]
            return uuids
        except Exception as e:
            get_module_logger("StockInfoDao").warning(f"save stock info list error:{e}")
            db.session.rollback()
        finally:
            db.session.close()

    @staticmethod
    def update_stock_info(uuid, **args):
        info = {'create_time': datetime.now(tz=timezone.utc)}
        for key, val in args.items():
            if hasattr(StockInfo, key) and key != 'uuid' and key != 'create_time' and val:
                info[key] = val
        num_rows_updated = StockInfo.query.filter_by(uuid=uuid).update(info)
        db.session.commit()
        return num_rows_updated

    @staticmethod
    def update_stock_st_status(code, a_capital_total, is_st, trade_status):
        num_rows_updated = StockInfo.query.filter_by(code=code).update(dict(is_st=is_st, trade_status=trade_status, a_capital_total=a_capital_total))
        db.session.commit()
        return num_rows_updated

    @staticmethod
    def get_total(*args):
        if args:
            return db.session.query(db.func.count(StockInfo.uuid)).filter(*args).scalar()
        return db.session.query(db.func.count(StockInfo.uuid)).scalar()

    def del_stock(self, code):
        return self.query.filter(StockInfo.code == code).delete()

    @staticmethod
    def clear_stock_list():
        tbl_name = StockInfo.get_tbl_name()
        sql = db.text(f"TRUNCATE TABLE {tbl_name};")
        result = db.session.execute(sql)
        db.session.execute(db.text("ALTER SEQUENCE stock.stock_info_uuid_seq RESTART WITH 1;"))
        db.session.commit()
        db.session.close()
        return result

    @staticmethod
    def get_stock_list_by_codes(codes):
        return StockInfo.query.filter(StockInfo.code.in_(codes)).order_by(StockInfo.id.desc()).all()






if __name__ == "__main__":
    stock = StockInfo()
    count = stock.get_total()
    print(count)