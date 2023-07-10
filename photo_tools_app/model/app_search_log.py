# -*- coding: utf-8 -*-
import json
from datetime import datetime
from sqlalchemy import BigInteger, String, SmallInteger, inspect, select, text
from photo_tools_app.model.base import Base
from photo_tools_app.__init__ import db, utils, func
from photo_tools_app.config.constant import Constant

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

    @staticmethod
    def get_search_log_list_by_page(page_num=1, page_size=Constant.PAGE_SIZE.value, content=None, user_id=None, begin_date=None, end_date=None):
        total = AppSearchLog.get_search_log_list_total(content, user_id, begin_date, end_date)
        start, end, _ = utils['common'].pagination(page_num, page_size, total)
        exp = AppSearchLog.query
        if content:
            exp = exp.filter(AppSearchLog.content.ilike('%{keyword}%'.format(keyword=content)))
        if user_id:
            exp = exp.filter(AppSearchLog.user_id == user_id)
        if begin_date and end_date:
            exp = exp.filter(db.and_(AppSearchLog.create_time <= begin_date, AppSearchLog.create_time >= end_date))
        return exp.order_by(AppSearchLog.uuid.asc()).offset(start).limit(page_size).all(), total

    @staticmethod
    def get_search_log_list_total(content=None, user_id=None, begin_date=None, end_date=None):
        exp = db.session.query(db.func.count(AppSearchLog.uuid))
        if content:
            exp = exp.filter(AppSearchLog.content.ilike('%{keyword}%'.format(keyword=content)))
        if user_id:
            exp = exp.filter(AppSearchLog.user_id == user_id)
        if begin_date and end_date:
            exp = exp.filter(db.and_(AppSearchLog.create_time <= begin_date, AppSearchLog.create_time >= end_date))
        return exp.scalar()

    @staticmethod
    def get_search_log_list_group_by(search_type=None, page_num=1, page_size=Constant.PAGE_SIZE.value, content=None, user_id=None, begin_date=None, end_date=None):
        total = AppSearchLog.get_search_log_list_group_by_total(search_type=search_type, content=content, user_id=user_id, begin_date=begin_date, end_date=end_date)
        start, end, _ = utils['common'].pagination(page_num, page_size, total)

        if search_type=='group_by_content':
            results = select(AppSearchLog.content, func.count('*').label('user_id')).select_from(AppSearchLog)
        else:
            results = select(AppSearchLog.user_id, func.count('*').label('content')).select_from(AppSearchLog)
        if content:
            results = results.filter(AppSearchLog.gender == content)
        if user_id:
            results = results.filter(AppSearchLog.gender == user_id)
        if begin_date and end_date:
            results = results.filter(db.and_(AppSearchLog.create_time <= begin_date, AppSearchLog.create_time >= end_date))
        if search_type == 'group_by_content':
            results = results.group_by(AppSearchLog.content).order_by(func.count('*').label('user_id').desc())
        else:
            results = results.group_by(AppSearchLog.user_id).order_by(func.count('*').label('content').desc())
        return db.session.execute(results.offset(start).limit(page_size)).all(), total

    @staticmethod
    def get_search_log_list_group_by_total(search_type=None, content=None, user_id=None, begin_date=None, end_date=None):
        if search_type == 'group_by_content':
            results = db.session.query(AppSearchLog.content)
        else:
            results = db.session.query(AppSearchLog.user_id)
        if content:
            results = results.filter(AppSearchLog.content == content)
        if user_id:
            results = results.filter(AppSearchLog.user_id == user_id)
        if begin_date and end_date:
            results = results.filter(db.and_(AppSearchLog.create_time <= begin_date, AppSearchLog.create_time >= end_date))
        if search_type == 'group_by_content':
            results = results.group_by(AppSearchLog.content)
        else:
            results = results.group_by(AppSearchLog.user_id)
        return results.count()