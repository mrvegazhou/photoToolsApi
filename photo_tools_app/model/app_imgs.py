# -*- coding: utf-8 -*-
import json
from datetime import datetime, timezone
from photo_tools_app.model.base import Base
from photo_tools_app.__init__ import db, utils, func
from photo_tools_app.config.constant import Constant
from sqlalchemy import or_


class AppImgs(Base):
    __tablename__ = 'app_imgs'
    __table_args__ = {'extend_existing': True, 'schema': 'app'}

    uuid = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    tags = db.Column(db.String(), nullable=False, server_default="", comment="标签")
    url = db.Column(db.String(), nullable=False, server_default="", comment="地址")
    type = db.Column(db.Integer, nullable=False, server_default="", comment="类型 1.feedback 2.画板 ")
    create_time = db.Column('create_time', db.TIMESTAMP, comment="创建时间", server_default=func.now())
    update_time = db.Column('update_time', db.TIMESTAMP, comment="修改时间")

    def get_keys(self):
        return {
            "uuid": self.uuid,
            "tags": self.tags,
            "url": self.url,
            "type": self.type,
            "create_time": self.create_time,
            "update_time": self.update_time
        }

    @staticmethod
    def get_type(name):
        types = {'feedback':1, '画板':2}
        if name not in types.keys():
            return False
        return types[name]

    def __repr__(self):
        obj = AppImgs.get_keys(self)
        return json.dumps(obj, cls=utils["common"].ComplexEncoder)

    def keys(self):
        return ('uuid', 'tags', 'url', 'type', 'create_time')

    def __getitem__(self, item):
        return getattr(self, item)

    @staticmethod
    def get_app_imgs(page_num=1,
                     page_size=Constant.PAGE_SIZE.value,
                     tags=None,
                     url=None,
                     type=None,
                     load_time=None,
                     begin_date=None,
                     end_date=None):
        exp = AppImgs.query
        if page_num<=0:
            page_num = 1
        start = (page_num - 1) * page_size
        if tags:
            tags_list = tags.split()
            if len(tags_list)==1:
                exp = exp.filter(AppImgs.tags.ilike('%{keyword}%'.format(keyword=tags)))
            else:
                or_ilike_list = []
                for tag in tags_list:
                    or_ilike_list.append(AppImgs.tags.ilike('%{keyword}%'.format(keyword=tag)))
                exp = exp.filter(or_(*or_ilike_list))
        if url:
            exp = exp.filter(AppImgs.url == url)
        if type:
            exp = exp.filter(AppImgs.type == type)
        if load_time:
            exp = exp.filter(AppImgs.create_time <= load_time)
        if begin_date and end_date:
            exp = exp.filter(db.and_(AppImgs.create_time <= begin_date, AppImgs.create_time >= end_date))
        return exp.order_by(AppImgs.uuid.asc()).offset(start).limit(page_size).all()

    @staticmethod
    def save_imgs(obj):
        db.session.add(obj)
        db.session.commit()
        return obj.uuid

    @staticmethod
    def batch_save_imgs(params):
        name = AppImgs.__tablename__
        schema = AppImgs.__table_args__
        schema = schema['schema']
        tbl_name = '{schema}.{table}'.format(schema=schema, table=name)
        sql_insert = []
        sql_insert_dict = {}
        i = 0
        for item in params:
            if not item['url']:
                return
            i = i + 1
            url_key = 'url' + str(i)
            type_key = 'type' + str(i)
            tags_key = 'tags' + str(i)
            sql_insert.append(
                "(:{url}, :{type}, :{tags})".format(url=url_key, type=type_key, tags=tags_key))
            sql_insert_dict[url_key] = item['url']
            sql_insert_dict[type_key] = AppImgs.get_type(item['type']) or 0
            sql_insert_dict[tags_key] = item['tags'] or ''

        result = db.session.connection().execute(db.text(
            'insert into {tbl_name} (url, type, tags) values {sql_str} RETURNING uuid'
                .format(tbl_name=tbl_name, sql_str=','.join(sql_insert))), **sql_insert_dict)
        db.session.commit()
        return result.fetchall()