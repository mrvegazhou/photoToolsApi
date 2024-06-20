# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/stockApi")
from stockApp import db, utils
from sqlalchemy import BigInteger, String, Date, Numeric
import json
from core.log.logger import get_module_logger


class DayTrading:

    _mapper = {}

    @staticmethod
    def get_hash_table_id(code, max_num=10):
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

                'uuid': db.Column(BigInteger, primary_key=True, autoincrement=True, unique=True),  # id 整型，主键，自增，唯一
                'code': db.Column(String, unique=True, nullable=False, comment="股票代码"),
                'trading_date': db.Column(Date, nullable=False, comment="日交易日期"),
                'close': db.Column(Numeric, nullable=False, comment="收盘价"),
                'high_price': db.Column(Numeric, nullable=False, comment="最高价"),
                'low_price': db.Column(Numeric, nullable=False, comment="最低价"),
                'open': db.Column(Numeric, nullable=False, comment="开盘价"),
                'volume':  db.Column(Numeric, nullable=False, comment="成交量(股)"),
                'turnover': db.Column(Numeric, nullable=False, comment="成交额"),
                'turnover_rate': db.Column(Numeric, nullable=False, comment="换手率=成交量(股)/流动股本(股)"),
                'amplitude': db.Column(Numeric, nullable=False, comment="振幅"),
                'change': db.Column(Numeric, nullable=False, comment="涨跌幅=(现价-上一个交易日收盘价)/上一个交易日收盘价*100%"),
                'price_change': db.Column(Numeric, nullable=False, comment="涨跌额"),
                'adj_factor': db.Column(Numeric, nullable=False, comment="复权因子=后复权价格/不复权价格")
            })
            DayTrading._mapper[class_name] = ModelClass

        return ModelClass()

    def __repr__(self):
        obj = {
            "uuid": self.uuid,
            "code": self.code,
            "trading_date": self.trading_date,
            "close": self.close,
            "open": self.open,
            "high_price": self.high_price,
            "low_price": self.low_price,
            "volume": self.volume,
            "turnover": self.turnover,
            "turnover_rate": self.turnover_rate,
            "amplitude": self.amplitude,
            "change": self.change,
            "price_change": self.price_change,
            "adj_factor": self.adj_factor,
        }
        return json.dumps(obj, cls=utils["common"].ComplexEncoder)

    # 获取时间段内的股票日交易信息
    @staticmethod
    def get_stock_day_trading_info(code, start_date, end_date):
        obj = DayTrading.model(code)
        query = obj.query.filter(db.and_(
            db.column('code') == code,
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
            'select {cols} from {tbl_name} where code = :code and trading_date>=:start_date and trading_date<=:end_date order by trading_date desc'.format(cols=cols, tbl_name=tbl_name)),
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
            'select {cols} from {tbl_name} where code = :code and trading_date =: trading_date order by trading_date asc'.format(
                cols=cols, tbl_name=tbl_name)),
            {'code': code, 'trading_date': date})
        print(str(query))
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
            'select {cols} from {tbl_name} where code = :code and trading_date>=:start_date and trading_date<=:end_date order by trading_date desc'.format(
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
                  code character varying NOT NULL,
                  trading_date timestamp without time zone,
                  close numeric(10, 2),
                  high_price numeric(10, 2),
                  low_price numeric(10, 2),
                  open numeric(10, 2),
                  volume numeric,
                  turnover numeric,
                  amplitude numeric,
                  change numeric,
                  price_change numeric,
                  turnover_rate numeric,
                  adj_factor numeric
                ) with (oids = false);
                COMMENT on table "stock"."day_trading_{}" is '股票日交易行情';
                COMMENT ON COLUMN stock.day_trading_{}.volume IS '成交量(股)';
                COMMENT ON COLUMN stock.day_trading_{}.turnover IS '成交额';
                COMMENT ON COLUMN stock.day_trading_{}.amplitude IS '振幅';
                COMMENT ON COLUMN stock.day_trading_{}.change IS '涨跌幅=(现价-上一个交易日收盘价)/上一个交易日收盘价*100%';
                COMMENT ON COLUMN stock.day_trading_{}.price_change IS '涨跌额';
                COMMENT ON COLUMN stock.day_trading_{}.turnover_rate IS '换手率=成交量(股)/流动股本(股)';
                COMMENT ON COLUMN stock.day_trading_{}.adj_factor IS '复权因子=后复权价格/不复权价格';
            '''.format(i, i, i, i, i, i, i, i, i)
            db.session.execute(db.text(sql))
            db.session.commit()

    @staticmethod
    def drop_tables(num=50):
        for i in range(num):
            sql = '''
                DROP TABLE IF EXISTS "stock"."day_trading_{}";
            '''.format(i)
            db.session.execute(db.text(sql))
            db.session.commit()

    def get_table(self, code):
        return self.get_hash_table_id(code, 10)

    @staticmethod
    def clear_tables():
        for i in range(50):
            sql = '''
                TRUNCATE TABLE "stock"."day_trading_{}";
            '''.format(i)
            db.session.execute(db.text(sql))
        db.session.commit()
        db.session.close()

    @staticmethod
    def add_trading_info(code, obj):
        try:
            info_model = DayTrading.model(code)
            for key, value in obj.items():
                if hasattr(info_model, key) and key != 'uuid':
                    setattr(info_model, key, value)
            db.session.add(info_model)
            uuid = info_model.uuid
            db.session.commit()
            return uuid
        except Exception as e:
            get_module_logger("DayTradingDao").warning(f"save day trading info error:{e}")
            db.session.rollback()
        finally:
            db.session.close()

    @staticmethod
    def add_trading_list(objs):
        try:
            day_trading_to_add = []
            for obj in objs:
                info_model = DayTrading.model(obj['code'])
                for key, value in obj.items():
                    if hasattr(info_model, key) and key != 'uuid':
                        setattr(info_model, key, value)
                day_trading_to_add.append(info_model)
            db.session.add_all(day_trading_to_add)
            db.session.commit()
            return [obj.uuid for obj in day_trading_to_add]
        except Exception as e:
            get_module_logger("DayTradingDao").warning(f"save day trading list error:{e}")
            db.session.rollback()
        finally:
            db.session.close()



if __name__ == "__main__":
    # obj = DayTrading.model('0000')
    # print(hasattr(obj, "code"))
    DayTrading.clear_tables()


