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

CREATE TABLE if not exists "stock"."stock_finance"
(
  uuid SERIAL NOT NULL PRIMARY KEY,
  stock_code character varying NOT NULL,
  date timestamp without time zone,
  assets numeric
)with (oids = false);
-- 注释
comment on table "stock"."stock_finance" is '股票财务信息';
COMMENT ON COLUMN stock.stock_finance.assets IS '股东权益不含少数股东权益';
-- 加索引
CREATE INDEX idx_code_date ON "stock"."stock_finance" (stock_code, date);


CREATE TABLE if not exists "stock"."sz50_stock_trading"
(
  uuid SERIAL NOT NULL PRIMARY KEY,
  trading_date timestamp without time zone,
  open_price numeric,
  close_price numeric,
  high_price numeric,
  low_price numeric,
  change_amount numeric,
  chg_pct numeric,
  volume numeric,
  turnover numeric
)with (oids = false);
-- 注释
comment on table "stock"."sz50_stock_trading" is '上证50 历史交易数据';
COMMENT ON COLUMN stock.sz50_stock_trading.change_amount IS '涨跌额';
COMMENT ON COLUMN stock.sz50_stock_trading.chg_pct IS '涨跌幅(%)';
COMMENT ON COLUMN stock.sz50_stock_trading.volume IS '成交量(股)';
COMMENT ON COLUMN stock.sz50_stock_trading.turnover IS '成交金额(元)';
-- 加索引
CREATE INDEX idx_trading_date ON "stock"."sz50_stock_trading" (trading_date);

--- 后台管理表
-- 管理员信息表
CREATE TABLE if not exists "stock"."admin_user"
(
  uuid SERIAL NOT NULL PRIMARY KEY,
  username character varying NOT NULL,
  password character varying NOT NULL,
  salt character varying NOT NULL,
  phone character varying NOT NULL,
  email character varying NOT NULL,
  description character varying NOT NULL,
  status smallint,
  create_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time TIMESTAMPTZ,
  delete_time TIMESTAMPTZ
)with (oids = false);

ALTER TABLE stock.admin_user ALTER COLUMN create_time SET DEFAULT CURRENT_TIMESTAMP;
alter table stock.admin_user alter create_time drop not null;
SELECT SETVAL((SELECT pg_get_serial_sequence('stock.admin_user', 'uuid')), 10, false);


-- 管理员和角色关系表
CREATE TABLE if not exists "stock"."admin_user_role"
(
  uuid SERIAL NOT NULL PRIMARY KEY,
  role_id bigint NOT NULL,
  admin_user_id bigint NOT NULL,
  create_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
)with (oids = false);
alter table stock.admin_user_role add constraint unique_user_role unique(admin_user_id, role_id);

-- 管理后台角色
CREATE TABLE if not exists "stock"."admin_role"
(
  uuid SERIAL NOT NULL PRIMARY KEY,
  title character varying,
  description character varying,
  sorts smallint,
  status smallint,
  create_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  update_time TIMESTAMPTZ,
  delete_time TIMESTAMPTZ
)with (oids = false);

-- 后台管理角色和菜单的权限关系
CREATE TABLE if not exists "stock"."admin_role_menu_power"
(
  uuid SERIAL NOT NULL PRIMARY KEY,
  role_id bigint NOT NULL,
  menu_id bigint NOT NULL,
  power_id bigint NOT NULL,
  create_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
)with (oids = false);
alter table stock.admin_role_menu_power add constraint unique_user_role_power unique(role_id, menu_id, power_id);

-- 菜单的操作项
CREATE TABLE if not exists "stock"."admin_menu_power"
(
  uuid SERIAL NOT NULL PRIMARY KEY,
  menu_id bigint NOT NULL,
  title character varying,
  code character varying,
  description character varying,
  sorts smallint,
  status smallint,
  create_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
)with (oids = false);

--菜单
CREATE TABLE if not exists "stock"."admin_menu"
(
  uuid SERIAL NOT NULL PRIMARY KEY,
  title character varying,
  icon character varying,
  url character varying,
  parent bigint NOT NULL,
  description character varying,
  sorts smallint,
  status smallint,
  create_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time TIMESTAMPTZ,
  delete_time TIMESTAMPTZ
)with (oids = false);


DO $$
DECLARE
    i INT := 0;
BEGIN
    WHILE i < 10 LOOP
--         EXECUTE format('ALTER TABLE stock.day_trading_%s ADD COLUMN code2 char(6);', i);
-- 				EXECUTE format('UPDATE stock.day_trading_%s SET code2 = LPAD(code::text, 6, ''0'');', i);
-- 				EXECUTE format('ALTER TABLE stock.day_trading_%s DROP COLUMN code;', i);
				EXECUTE format('ALTER TABLE stock.day_trading_%s RENAME COLUMN code2 TO code;', i);
        i := i + 1;
    END LOOP;
END $$;
