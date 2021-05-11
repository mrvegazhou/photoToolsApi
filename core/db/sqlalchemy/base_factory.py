# -*- coding: utf-8 -*-
from .sqlalchemy_factory import SqlalchemyFactory
from core.config.sys_config import config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer
import uuid
from core.utils.common import md5

Base = declarative_base()

class BaseFactory(SqlalchemyFactory):
    _instance = None
    env = config['env']
    config[env].DB_URI
    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(BaseFactory, cls).__new__(cls)
        return cls._instance

    def __init__(self, uri=config[env].DB_URI, echo=False, encoding="utf8"):
        super(BaseFactory, self).__init__(uri, echo, encoding, Base.metadata)

    def __init_db__(self):
        Base.metadata.create_all(self._engine)

class BaseModelMixin(Base):
    __abstract__ = True
    uuid = Column(Integer, primary_key=True, default=uuid.uuid4().hex)

    @staticmethod
    def get_hash_table_id(code, max_num):
        hash_str = md5(code)
        num = int(hash_str[:2] + hash_str[-2:], 16)  # 16进制 --> 10进制
        hash_id = num % max_num
        return hash_id