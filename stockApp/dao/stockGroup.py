# -*- coding: utf-8 -*-
import json
from sqlalchemy import BigInteger, String
from datetime import datetime, timezone
from stockApp import db, utils, func
from .base import Base
from core.log.logger import get_module_logger


class StockGroup(Base):

    __tablename__ = 'stock_group'
    __table_args__ = {'extend_existing': True, 'schema': 'stock'}

    uuid = db.Column(BigInteger, primary_key=True, autoincrement=True, unique=True)  # id 整型，主键，自增，唯一
    code = db.Column(String, unique=True, nullable=False, server_default="", comment="股票code")
    group_name = db.Column(String, unique=True, nullable=False, server_default="股票指数名称")
    create_time = db.Column(db.DateTime(timezone=True), comment="创建时间", server_default=func.now(), default=datetime.now)

    def get_keys(self):
        return {
            "uuid": self.uuid,
            "code": self.code,
            "group_name": self.group_name,
            "create_time": self.create_time
        }

    def __repr__(self):
        obj = StockGroup.get_keys(self)
        return json.dumps(obj, cls=utils["common"].ComplexEncoder)

    @staticmethod
    def get_tbl_name():
        name = StockGroup.__tablename__
        schema = StockGroup.__table_args__
        schema = schema['schema']
        tbl_name = '{schema}.{table}'.format(schema=schema, table=name)
        return tbl_name

    @staticmethod
    def get_stock_list_by_sql(group_name, cols=None):
        try:
            tbl_name = StockGroup.get_tbl_name()
            if cols:
                cols = ['{}.{}'.format(tbl_name, col) for col in cols]
                cols = ','.join(cols)
            else:
                cols = '*'
            result = db.session.connection().execute(
                db.text(
                    'select {cols} from {tbl_name} where group_name = :group_name'
                    .format(cols=cols, tbl_name=tbl_name)
                ),
                {'group_name': group_name}
            )
            return result.fetchall()
        except Exception as e:
            get_module_logger("StockGroupDao").warning(f"save stock group list error:{e}")
        finally:
            db.session.close()







