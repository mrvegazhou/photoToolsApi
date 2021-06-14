# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
from stock_app.__init__ import db, utils
import json


class DayTrading:

    _mapper = {}

    @staticmethod
    def get_hash_table_id(code, max_num):
        hash_str = utils['common'].md5(code)
        num = int(hash_str[:2] + hash_str[-2:], 16)  # 16进制 --> 10进制
        hash_id = num % max_num
        return hash_id

    @staticmethod
    def model(stock_code):
        table_index = DayTrading.get_hash_table_id(stock_code, 10)
        table_name = 'day_trading_%d' % table_index
        class_name = 'DayTrading_%d' % table_index
        ModelClass = DayTrading._mapper.get(class_name, None)
        if ModelClass is None:
            ModelClass = type(table_name, (db.Model,), {
                '__module__': __name__,
                '__name__': class_name,
                '__tablename__': table_name,
                '__table_args__': {'extend_existing': True, 'schema': 'stock'},

                '__repr__': DayTrading.__repr__,

                'uuid': db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True),  # id 整型，主键，自增，唯一
                'stock_code': db.Column(db.String(255), unique=True, nullable=False, comment="股票代码"),
                'trading_date': db.Column(db.String(50), nullable=False, comment="日交易日期"),
                'close_price': db.Column(db.Numeric, nullable=False, comment="收盘价"),
                'high_price': db.Column(db.Numeric, nullable=False, comment="最高价"),
                'low_price': db.Column(db.Numeric, nullable=False, comment="最低价"),
                'open_price': db.Column(db.Numeric, nullable=False, comment="开盘价"),
                'volume':  db.Column(db.Numeric, nullable=False, comment="成交量(股)"),
                'outstanding_share': db.Column(db.Numeric, nullable=False, comment="流动股本(股)"),
                'turnover': db.Column(db.Numeric, nullable=False, comment="换手率=成交量(股)/流动股本(股)"),
                'chg_pct': db.Column(db.Numeric, nullable=False, comment="涨跌幅=(现价-上一个交易日收盘价)/上一个交易日收盘价*100%")
            })
            DayTrading._mapper[class_name] = ModelClass

        return ModelClass()

    def __repr__(self):
        obj = {
            "uuid": self.uuid,
            "stock_code": self.stock_code,
            "trading_date": self.trading_date,
            "close_price": self.close_price,
            "high_price": self.high_price,
            "low_price": self.low_price,
            "open_price": self.open_price,
            "volume": self.volume,
            "outstanding_share": self.outstanding_share,
            "turnover": self.turnover,
            "chg_pct": self.chg_pct
        }
        return json.dumps(obj, cls=utils["common"].ComplexEncoder)

    # 获取时间段内的股票日交易信息
    @staticmethod
    def get_stock_day_trading_info(code, start_date, end_date):
        obj = DayTrading.model(code)
        query = obj.query.filter(db.and_(
            db.column('stock_code') == code,
            db.column('trading_date') >= start_date,
            db.column('trading_date') <= end_date
        )).order_by(db.text("trading_date desc"))
        return query.all()

    @staticmethod
    def get_stock_trading_list_by_SQL(code, start_date, end_date, cols=None):
        obj = DayTrading.model(code)
        name = obj.__tablename__
        schema = obj.__table_args__
        schema = schema['schema']
        tbl_name = '{schema}.{table}'.format(schema=schema, table=name)
        if cols:
            cols = ['{}.{}'.format(tbl_name, col) for col in cols]
            cols = ','.join(cols)
        else:
            cols = '*'

        result = db.session.connection().execute(db.text(
            'select {cols} from {tbl_name} where stock_code = :code and  trading_date>=:start_date and trading_date<=:end_date order by trading_date desc'.format(cols=cols, tbl_name=tbl_name)),
                                                 {'code': code, 'start_date': start_date, 'end_date': end_date})
        return result.fetchall()


    @staticmethod
    def get_stock_trading_info_by_SQL(code, date, cols=None):
        obj = DayTrading.model(code)
        name = obj.__tablename__
        schema = obj.__table_args__
        schema = schema['schema']
        tbl_name = '{schema}.{table}'.format(schema=schema, table=name)
        if cols:
            cols = ['{}.{}'.format(tbl_name, col) for col in cols]
            cols = ','.join(cols)
        else:
            cols = '*'
        result = db.session.connection().execute(db.text(
            'select {cols} from {tbl_name} where stock_code = :code and  trading_date =: trading_date order by trading_date desc'.format(
                cols=cols, tbl_name=tbl_name)),
            {'code': code, 'trading_date': date})
        return result.fetchone()


    @staticmethod
    def get_stock_trading_info_by_SQL(code, start_date, end_date, cols=None):
        obj = DayTrading.model(code)
        name = obj.__tablename__
        schema = obj.__table_args__
        schema = schema['schema']
        tbl_name = '{schema}.{table}'.format(schema=schema, table=name)
        if cols:
            cols = ['{}.{}'.format(tbl_name, col) for col in cols]
            cols = ','.join(cols)
        else:
            cols = '*'

        result = db.session.connection().execute(db.text(
            'select {cols} from {tbl_name} where stock_code = :code and  trading_date>=:start_date and trading_date<=:end_date order by trading_date desc'.format(
                cols=cols, tbl_name=tbl_name)),
            {'code': code, 'start_date': start_date, 'end_date': end_date})
        return result.fetchall()


    @staticmethod
    def get_stock_day_trading_by_date(code, date):
        obj = DayTrading.model(code)
        return obj.query.filter(db.and_(obj.stock_code == code, obj.trading_date == date)).first()

    @staticmethod
    def get_stock_all_day_trading(code):
        obj = DayTrading.model(code)
        return obj.query.filter_by(stock_code = code).order_by(db.desc('trading_date')).all()

    @staticmethod
    def create_tables():
        for i in range(10):
            sql = '''
                CREATE TABLE if not exists "stock"."day_trading_{}"
                (
                  uuid SERIAL NOT NULL PRIMARY KEY,
                  stock_code character varying NOT NULL,
                  trading_date timestamp without time zone,
                  close_price numeric,
                  high_price numeric,
                  low_price numeric,
                  open_price numeric,
                  volume numeric,
                  outstanding_share numeric,
                  turnover numeric,
                  chg_pct numeric,
                  
                  DIFF numeric,
                  DEA numeric,
                  MACD numeric,
                  MACD_buy numeric,
                  KDJ_K numeric,
                  KDJ_D numeric,
                  KDJ_J numeric,
                  KDJ_buy numeric,
                  MA5 numeric,
                  MA10 numeric,
                  MA20 numeric,
                  MA43 numeric,
                  MA60 numeric,
                  M5_cross_M10 numeric,
                  
                  PE numeric,
                  PE_TTM numeric,
                  PB numeric,
                  PS numeric,
                  PS_TTM numeric,
                  DV_ratio numeric,
                  DV_TTM numeric,
                  total_mv numeric,
                  
                ) with (oids = false);
                COMMENT on table "stock"."day_trading_{}" is '股票日交易行情';
                COMMENT ON COLUMN stock.day_trading_{}.volume IS '成交量(股)';
                COMMENT ON COLUMN stock.day_trading_{}.outstanding_share IS '流动股本(股)';
                COMMENT ON COLUMN stock.day_trading_{}.turnover IS '换手率=成交量(股)/流动股本(股)';
                COMMENT ON COLUMN stock.day_trading_{}.chg_pct IS '涨跌幅=(现价-上一个交易日收盘价)/上一个交易日收盘价*100%';
                COMMENT ON COLUMN stock.day_trading_{}.PE IS '市盈率';
                COMMENT ON COLUMN stock.day_trading_{}.PE_TTM IS '市盈率TTM';
                COMMENT ON COLUMN stock.day_trading_{}.PB IS '市净率';
                COMMENT ON COLUMN stock.day_trading_{}.PS IS '市销率';
                COMMENT ON COLUMN stock.day_trading_{}.PS_TTM IS '市销率TTM';
                COMMENT ON COLUMN stock.day_trading_{}.DV_ratio IS '股息率';
                COMMENT ON COLUMN stock.day_trading_{}.DV_TTM IS '股息率TTM';
                COMMENT ON COLUMN stock.day_trading_{}.total_mv IS '总市值';
            '''.format(i, i, i, i, i, i)
            db.session.execute(sql)
            db.session.commit()

    @staticmethod
    def drop_tables():
        for i in range(10):
            sql = '''
                DROP TABLE IF EXISTS "stock"."day_trading_{}";
            '''.format(i)
            db.session.execute(sql)
            db.session.commit()

    def get_table(self, code):
        return self.get_hash_table_id(code, 10)

    @staticmethod
    def clear_tables():
        for i in range(10):
            sql = '''
                TRUNCATE TABLE "stock"."day_trading_{}";
            '''.format(i)
            db.session.execute(sql)
            db.session.commit()

    @staticmethod
    def add_trading_info(code, **kwargs):
        obj = DayTrading.model(code)
        for key, value in kwargs.items():
            if hasattr(obj, key) and key != 'uuid':
                setattr(obj, key, value)
        db.session.add(obj)
        uuid = obj.uuid
        db.session.commit()
        return uuid


if __name__ == "__main__":
    obj = DayTrading.model('0000')
    print(hasattr(obj, "stock_code"))


