# -*- coding: utf-8 -*-
import json
from datetime import datetime
from sqlalchemy import BigInteger, String, SmallInteger, or_
from photo_tools_app.model.base import Base
from photo_tools_app.__init__ import db, utils, func


class AppSearchLog(Base):
    __tablename__ = 'app_search_log'
    __table_args__ = {'extend_existing': True, 'schema': 'app'}

    uuid = db.Column(BigInteger, primary_key=True, autoincrement=True, unique=True)
    content = db.Column(String, unique=False, nullable=False, server_default="", comment="搜索内容")
    user_id = db.Column(BigInteger, unique=False, nullable=False, server_default="", comment="搜索用户")
    create_time = db.Column(db.DateTime(timezone=True), comment="创建时间", server_default=func.now(), default=datetime.now)

    def get_keys(self):
        return {
            "uuid": self.uuid,
            "content": self.content,
            "user_id": self.user_id,
            "create_time": self.create_time
        }

    def __repr__(self):
        obj = AppSearchLog.get_keys(self)
        return json.dumps(obj, cls=utils["common"].ComplexEncoder)

    def keys(self):
        return ('uuid', 'content', 'user_id', 'create_time')


