# -*- coding: utf-8 -*-
from sqlalchemy import create_engine, Table
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker, scoped_session

class SqlalchemyFactory(object):
    _instance = None

    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(SqlalchemyFactory, cls).__new__(cls)
        return cls._instance

    def __init__(self, uri, echo, encoding, metadata):
        kwargs = dict(echo=echo, encoding=encoding, convert_unicode=True)
        self._metadata = metadata
        self._engine = create_engine(uri, **kwargs)
        self._session_maker = sessionmaker(
            bind=self._engine,
            autoflush=False,
            autocommit=False
        )

    def session(self):
        # if not self._session:
        session = scoped_session(self._session_maker)
        _session = session()
        _session.text_factory = str
        return _session

    def create_table(self, table_name, *columns):
        table = Table(table_name, self._metadata, *columns, extend_existing=True)
        if not table.exists(bind=self._engine):
            table.create(bind=self._engine, checkfirst=True)
        return table

    def drop_table(self, table_name):
        table = Table(table_name, self._metadata, extend_existing=True)
        if not table.exists(bind=self._engine):
            return
        table.drop(bind=self._engine)
        return table

    def model(self, table_name, class_name, *columns):
        try:
            # tables = Base.metadata.tables
            # if table_name in tables:
            #     return tables[table_name]
            table = self.create_table(table_name, *columns)
            # Base.metadata.reflect(self._engine)
            model = type(class_name, (object,), dict())
            mapper(model, table)
            # Base.metadata.clear()
            return model
        except Exception as e:
            self.drop_table(table_name)
            print('SqlalchemyFactory model error: %s' % e)