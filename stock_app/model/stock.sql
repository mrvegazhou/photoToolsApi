-- create schema stock;
CREATE TABLE if not exists "stock"."stock_info"
(
    uuid SERIAL NOT NULL PRIMARY KEY,
    name character varying NOT NULL UNIQUE,
    code character varying NOT NULL UNIQUE
)with (oids = false);
-- 注释
comment on table "stock"."stock_info" is '股票基本信息表';
COMMENT ON COLUMN stock.stock_info.name IS '股票名称';
COMMENT ON COLUMN stock.stock_info.code IS '股票代码';

CREATE TABLE if not exists "stock"."day_trading"
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
  chg_pct numeric
)with (oids = false);
-- 注释
comment on table "stock"."day_trading" is '股票日交易行情';
COMMENT ON COLUMN stock.day_trading.volume IS '成交量(股)';
COMMENT ON COLUMN stock.day_trading.outstanding_share IS '流动股本(股)';
COMMENT ON COLUMN stock.day_trading.turnover IS '换手率=成交量(股)/流动股本(股)';
COMMENT ON COLUMN stock.day_trading.chg_pct IS '涨跌幅=(现价-上一个交易日收盘价)/上一个交易日收盘价*100%';