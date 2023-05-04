--
-- PostgreSQL database dump
--

-- Dumped from database version 13.2
-- Dumped by pg_dump version 13.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: admin; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA admin;


ALTER SCHEMA admin OWNER TO postgres;

--
-- Name: app; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA app;


ALTER SCHEMA app OWNER TO postgres;

--
-- Name: footgun(text, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.footgun(_schema text, _parttionbase text) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    row     record;
BEGIN
    FOR row IN 
        SELECT
            table_schema,
            table_name
        FROM
            information_schema.tables
        WHERE
            table_type = 'BASE TABLE'
        AND
            table_schema = _schema
        AND
            table_name ILIKE (_parttionbase || '%')
    LOOP
        EXECUTE 'DROP TABLE ' || quote_ident(row.table_schema) || '.' || quote_ident(row.table_name) || ' CASCADE ';
        RAISE INFO 'Dropped table: %', quote_ident(row.table_schema) || '.' || quote_ident(row.table_name);
    END LOOP;
END;
$$;


ALTER FUNCTION public.footgun(_schema text, _parttionbase text) OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: admin_menu; Type: TABLE; Schema: admin; Owner: postgres
--

CREATE TABLE admin.admin_menu (
    uuid integer NOT NULL,
    title character varying,
    icon character varying,
    url character varying,
    parent bigint NOT NULL,
    description character varying,
    sorts smallint,
    status smallint,
    create_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    update_time timestamp with time zone,
    delete_time timestamp with time zone
);


ALTER TABLE admin.admin_menu OWNER TO postgres;

--
-- Name: admin_menu_power; Type: TABLE; Schema: admin; Owner: postgres
--

CREATE TABLE admin.admin_menu_power (
    uuid integer NOT NULL,
    menu_id bigint NOT NULL,
    title character varying,
    code character varying,
    description character varying,
    sorts smallint,
    status smallint,
    create_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    update_time timestamp with time zone
);


ALTER TABLE admin.admin_menu_power OWNER TO postgres;

--
-- Name: admin_menu_power_uuid_seq; Type: SEQUENCE; Schema: admin; Owner: postgres
--

CREATE SEQUENCE admin.admin_menu_power_uuid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE admin.admin_menu_power_uuid_seq OWNER TO postgres;

--
-- Name: admin_menu_power_uuid_seq; Type: SEQUENCE OWNED BY; Schema: admin; Owner: postgres
--

ALTER SEQUENCE admin.admin_menu_power_uuid_seq OWNED BY admin.admin_menu_power.uuid;


--
-- Name: admin_menu_uuid_seq; Type: SEQUENCE; Schema: admin; Owner: postgres
--

CREATE SEQUENCE admin.admin_menu_uuid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE admin.admin_menu_uuid_seq OWNER TO postgres;

--
-- Name: admin_menu_uuid_seq; Type: SEQUENCE OWNED BY; Schema: admin; Owner: postgres
--

ALTER SEQUENCE admin.admin_menu_uuid_seq OWNED BY admin.admin_menu.uuid;


--
-- Name: admin_role; Type: TABLE; Schema: admin; Owner: postgres
--

CREATE TABLE admin.admin_role (
    uuid integer NOT NULL,
    title character varying,
    description character varying,
    sorts smallint,
    status smallint,
    create_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    update_time timestamp with time zone,
    delete_time timestamp with time zone
);


ALTER TABLE admin.admin_role OWNER TO postgres;

--
-- Name: admin_role_menu_power; Type: TABLE; Schema: admin; Owner: postgres
--

CREATE TABLE admin.admin_role_menu_power (
    uuid integer NOT NULL,
    role_id integer NOT NULL,
    menu_id integer NOT NULL,
    power_id integer NOT NULL,
    create_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE admin.admin_role_menu_power OWNER TO postgres;

--
-- Name: admin_role_menu_power_uuid_seq; Type: SEQUENCE; Schema: admin; Owner: postgres
--

CREATE SEQUENCE admin.admin_role_menu_power_uuid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE admin.admin_role_menu_power_uuid_seq OWNER TO postgres;

--
-- Name: admin_role_menu_power_uuid_seq; Type: SEQUENCE OWNED BY; Schema: admin; Owner: postgres
--

ALTER SEQUENCE admin.admin_role_menu_power_uuid_seq OWNED BY admin.admin_role_menu_power.uuid;


--
-- Name: admin_role_uuid_seq; Type: SEQUENCE; Schema: admin; Owner: postgres
--

CREATE SEQUENCE admin.admin_role_uuid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE admin.admin_role_uuid_seq OWNER TO postgres;

--
-- Name: admin_role_uuid_seq; Type: SEQUENCE OWNED BY; Schema: admin; Owner: postgres
--

ALTER SEQUENCE admin.admin_role_uuid_seq OWNED BY admin.admin_role.uuid;


--
-- Name: admin_user; Type: TABLE; Schema: admin; Owner: postgres
--

CREATE TABLE admin.admin_user (
    uuid integer NOT NULL,
    username character varying NOT NULL,
    password character varying NOT NULL,
    salt character varying NOT NULL,
    phone character varying NOT NULL,
    email character varying NOT NULL,
    description character varying NOT NULL,
    status smallint,
    create_time timestamp with time zone DEFAULT now(),
    update_time timestamp with time zone,
    delete_time timestamp with time zone
);


ALTER TABLE admin.admin_user OWNER TO postgres;

--
-- Name: admin_user_role; Type: TABLE; Schema: admin; Owner: postgres
--

CREATE TABLE admin.admin_user_role (
    uuid integer NOT NULL,
    role_id bigint NOT NULL,
    admin_user_id bigint NOT NULL,
    create_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE admin.admin_user_role OWNER TO postgres;

--
-- Name: admin_user_role_uuid_seq; Type: SEQUENCE; Schema: admin; Owner: postgres
--

CREATE SEQUENCE admin.admin_user_role_uuid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE admin.admin_user_role_uuid_seq OWNER TO postgres;

--
-- Name: admin_user_role_uuid_seq; Type: SEQUENCE OWNED BY; Schema: admin; Owner: postgres
--

ALTER SEQUENCE admin.admin_user_role_uuid_seq OWNED BY admin.admin_user_role.uuid;


--
-- Name: admin_user_uuid_seq1; Type: SEQUENCE; Schema: admin; Owner: postgres
--

CREATE SEQUENCE admin.admin_user_uuid_seq1
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE admin.admin_user_uuid_seq1 OWNER TO postgres;

--
-- Name: admin_user_uuid_seq1; Type: SEQUENCE OWNED BY; Schema: admin; Owner: postgres
--

ALTER SEQUENCE admin.admin_user_uuid_seq1 OWNED BY admin.admin_user.uuid;


--
-- Name: app_feedback_uuid_seq; Type: SEQUENCE; Schema: app; Owner: postgres
--

CREATE SEQUENCE app.app_feedback_uuid_seq
    START WITH 13
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE app.app_feedback_uuid_seq OWNER TO postgres;

--
-- Name: app_feedback; Type: TABLE; Schema: app; Owner: postgres
--

CREATE TABLE app.app_feedback (
    uuid bigint DEFAULT nextval('app.app_feedback_uuid_seq'::regclass) NOT NULL,
    content character varying NOT NULL,
    contact character varying,
    type smallint NOT NULL,
    create_time time with time zone,
    imgs character varying,
    user_id bigint NOT NULL
);


ALTER TABLE app.app_feedback OWNER TO postgres;

--
-- Name: app_imgs_uuid_seq; Type: SEQUENCE; Schema: app; Owner: postgres
--

CREATE SEQUENCE app.app_imgs_uuid_seq
    START WITH 13
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE app.app_imgs_uuid_seq OWNER TO postgres;

--
-- Name: app_imgs; Type: TABLE; Schema: app; Owner: postgres
--

CREATE TABLE app.app_imgs (
    uuid bigint DEFAULT nextval('app.app_imgs_uuid_seq'::regclass) NOT NULL,
    tags character varying,
    url character varying,
    create_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    update_time time with time zone,
    type smallint,
    base_dir character varying
);


ALTER TABLE app.app_imgs OWNER TO postgres;

--
-- Name: TABLE app_imgs; Type: COMMENT; Schema: app; Owner: postgres
--

COMMENT ON TABLE app.app_imgs IS '图片';


--
-- Name: app_scheduled_tasks; Type: TABLE; Schema: app; Owner: postgres
--

CREATE TABLE app.app_scheduled_tasks (
    uuid bigint NOT NULL,
    type smallint,
    name character varying,
    content character varying,
    create_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    update_time time with time zone,
    status smallint DEFAULT 1 NOT NULL
);


ALTER TABLE app.app_scheduled_tasks OWNER TO postgres;

--
-- Name: app_user; Type: TABLE; Schema: app; Owner: postgres
--

CREATE TABLE app.app_user (
    create_time time with time zone,
    email character varying,
    phone character varying,
    status smallint,
    update_time time with time zone,
    username character varying,
    uuid bigint NOT NULL,
    delete_time time with time zone,
    description character varying,
    type smallint,
    openid character varying
);


ALTER TABLE app.app_user OWNER TO postgres;

--
-- Name: app_user_uuid_seq; Type: SEQUENCE; Schema: app; Owner: postgres
--

CREATE SEQUENCE app.app_user_uuid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE app.app_user_uuid_seq OWNER TO postgres;

--
-- Name: app_user_uuid_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: postgres
--

ALTER SEQUENCE app.app_user_uuid_seq OWNED BY app.app_user.uuid;


--
-- Name: day_trading_; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.day_trading_ (
    uuid integer NOT NULL,
    stock_code character varying(255) NOT NULL,
    trading_date timestamp without time zone NOT NULL,
    close_price numeric NOT NULL,
    high_price numeric NOT NULL,
    low_price numeric NOT NULL,
    open_price numeric NOT NULL,
    volume numeric NOT NULL,
    outstanding_share numeric NOT NULL,
    turnover numeric NOT NULL
);


ALTER TABLE public.day_trading_ OWNER TO postgres;

--
-- Name: COLUMN day_trading_.stock_code; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.day_trading_.stock_code IS '股票代码';


--
-- Name: COLUMN day_trading_.trading_date; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.day_trading_.trading_date IS '日交易日期';


--
-- Name: COLUMN day_trading_.close_price; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.day_trading_.close_price IS '收盘价';


--
-- Name: COLUMN day_trading_.high_price; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.day_trading_.high_price IS '最高价';


--
-- Name: COLUMN day_trading_.low_price; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.day_trading_.low_price IS '最低价';


--
-- Name: COLUMN day_trading_.open_price; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.day_trading_.open_price IS '开盘价';


--
-- Name: COLUMN day_trading_.volume; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.day_trading_.volume IS '成交量(股)';


--
-- Name: COLUMN day_trading_.outstanding_share; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.day_trading_.outstanding_share IS '流动股本(股)';


--
-- Name: COLUMN day_trading_.turnover; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.day_trading_.turnover IS '换手率=成交量(股)/流动股本(股)';


--
-- Name: day_trading__uuid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.day_trading__uuid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.day_trading__uuid_seq OWNER TO postgres;

--
-- Name: day_trading__uuid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.day_trading__uuid_seq OWNED BY public.day_trading_.uuid;


--
-- Name: admin_menu uuid; Type: DEFAULT; Schema: admin; Owner: postgres
--

ALTER TABLE ONLY admin.admin_menu ALTER COLUMN uuid SET DEFAULT nextval('admin.admin_menu_uuid_seq'::regclass);


--
-- Name: admin_menu_power uuid; Type: DEFAULT; Schema: admin; Owner: postgres
--

ALTER TABLE ONLY admin.admin_menu_power ALTER COLUMN uuid SET DEFAULT nextval('admin.admin_menu_power_uuid_seq'::regclass);


--
-- Name: admin_role uuid; Type: DEFAULT; Schema: admin; Owner: postgres
--

ALTER TABLE ONLY admin.admin_role ALTER COLUMN uuid SET DEFAULT nextval('admin.admin_role_uuid_seq'::regclass);


--
-- Name: admin_role_menu_power uuid; Type: DEFAULT; Schema: admin; Owner: postgres
--

ALTER TABLE ONLY admin.admin_role_menu_power ALTER COLUMN uuid SET DEFAULT nextval('admin.admin_role_menu_power_uuid_seq'::regclass);


--
-- Name: admin_user uuid; Type: DEFAULT; Schema: admin; Owner: postgres
--

ALTER TABLE ONLY admin.admin_user ALTER COLUMN uuid SET DEFAULT nextval('admin.admin_user_uuid_seq1'::regclass);


--
-- Name: admin_user_role uuid; Type: DEFAULT; Schema: admin; Owner: postgres
--

ALTER TABLE ONLY admin.admin_user_role ALTER COLUMN uuid SET DEFAULT nextval('admin.admin_user_role_uuid_seq'::regclass);


--
-- Name: app_user uuid; Type: DEFAULT; Schema: app; Owner: postgres
--

ALTER TABLE ONLY app.app_user ALTER COLUMN uuid SET DEFAULT nextval('app.app_user_uuid_seq'::regclass);


--
-- Name: day_trading_ uuid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.day_trading_ ALTER COLUMN uuid SET DEFAULT nextval('public.day_trading__uuid_seq'::regclass);


--
-- Name: admin_menu admin_menu_pkey; Type: CONSTRAINT; Schema: admin; Owner: postgres
--

ALTER TABLE ONLY admin.admin_menu
    ADD CONSTRAINT admin_menu_pkey PRIMARY KEY (uuid);


--
-- Name: admin_menu_power admin_menu_power_pkey; Type: CONSTRAINT; Schema: admin; Owner: postgres
--

ALTER TABLE ONLY admin.admin_menu_power
    ADD CONSTRAINT admin_menu_power_pkey PRIMARY KEY (uuid);


--
-- Name: admin_role_menu_power admin_role_menu_power_pkey; Type: CONSTRAINT; Schema: admin; Owner: postgres
--

ALTER TABLE ONLY admin.admin_role_menu_power
    ADD CONSTRAINT admin_role_menu_power_pkey PRIMARY KEY (uuid);


--
-- Name: admin_role admin_role_pkey; Type: CONSTRAINT; Schema: admin; Owner: postgres
--

ALTER TABLE ONLY admin.admin_role
    ADD CONSTRAINT admin_role_pkey PRIMARY KEY (uuid);


--
-- Name: admin_user admin_user_pkey1; Type: CONSTRAINT; Schema: admin; Owner: postgres
--

ALTER TABLE ONLY admin.admin_user
    ADD CONSTRAINT admin_user_pkey1 PRIMARY KEY (uuid);


--
-- Name: admin_user_role admin_user_role_pkey; Type: CONSTRAINT; Schema: admin; Owner: postgres
--

ALTER TABLE ONLY admin.admin_user_role
    ADD CONSTRAINT admin_user_role_pkey PRIMARY KEY (uuid);


--
-- Name: admin_user_role unique_user_role; Type: CONSTRAINT; Schema: admin; Owner: postgres
--

ALTER TABLE ONLY admin.admin_user_role
    ADD CONSTRAINT unique_user_role UNIQUE (admin_user_id, role_id);


--
-- Name: admin_role_menu_power unique_user_role_power; Type: CONSTRAINT; Schema: admin; Owner: postgres
--

ALTER TABLE ONLY admin.admin_role_menu_power
    ADD CONSTRAINT unique_user_role_power UNIQUE (role_id, menu_id, power_id);


--
-- Name: app_feedback app_feedback_pkey; Type: CONSTRAINT; Schema: app; Owner: postgres
--

ALTER TABLE ONLY app.app_feedback
    ADD CONSTRAINT app_feedback_pkey PRIMARY KEY (uuid);


--
-- Name: app_scheduled_tasks app_scheduled_tasks_pkey; Type: CONSTRAINT; Schema: app; Owner: postgres
--

ALTER TABLE ONLY app.app_scheduled_tasks
    ADD CONSTRAINT app_scheduled_tasks_pkey PRIMARY KEY (uuid);


--
-- Name: app_user app_user_pkey; Type: CONSTRAINT; Schema: app; Owner: postgres
--

ALTER TABLE ONLY app.app_user
    ADD CONSTRAINT app_user_pkey PRIMARY KEY (uuid);


--
-- Name: app_imgs imgs_pkey; Type: CONSTRAINT; Schema: app; Owner: postgres
--

ALTER TABLE ONLY app.app_imgs
    ADD CONSTRAINT imgs_pkey PRIMARY KEY (uuid);


--
-- Name: day_trading_ day_trading__pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.day_trading_
    ADD CONSTRAINT day_trading__pkey PRIMARY KEY (uuid);


--
-- Name: day_trading_ day_trading__stock_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.day_trading_
    ADD CONSTRAINT day_trading__stock_code_key UNIQUE (stock_code);


--
-- Name: idx_tags; Type: INDEX; Schema: app; Owner: postgres
--

CREATE INDEX idx_tags ON app.app_imgs USING btree (tags);


--
-- Name: idx_url; Type: INDEX; Schema: app; Owner: postgres
--

CREATE INDEX idx_url ON app.app_imgs USING btree (url);


--
-- PostgreSQL database dump complete
--

