# -*- coding: utf-8 -*-
import json
from datetime import datetime, timezone
from sqlalchemy import BigInteger, String, SmallInteger
from photo_tools_app.model.base import Base
from photo_tools_app.__init__ import db, utils, func
from sqlalchemy.exc import SQLAlchemyError
from photo_tools_app.config.constant import Constant
from sqlalchemy import or_
from photo_tools_app.exception.api_exception import DatabaseError


class AppImgs(Base):
    __tablename__ = 'app_imgs'
    __table_args__ = {'extend_existing': True, 'schema': 'app'}

    uuid = db.Column(BigInteger, primary_key=True, autoincrement=True, unique=True)
    tags = db.Column(String, nullable=False, server_default="", comment="标签")
    url = db.Column(String, nullable=False, server_default="", comment="地址")
    base_dir = db.Column(String, nullable=False, server_default="", comment="存储根目录")
    type = db.Column(SmallInteger, nullable=False, server_default="", comment="类型 1.feedback 2.画板 ")
    create_time = db.Column(db.DateTime(timezone=True), comment="创建时间", server_default=func.now(), default=datetime.now)
    update_time = db.Column('update_time', db.DateTime(timezone=True), comment="修改时间")

    def get_keys(self):
        return {
            "uuid": self.uuid,
            "tags": self.tags,
            "url": self.url,
            "base_dir": self.base_dir,
            "type": self.type,
            "create_time": self.create_time,
            "update_time": self.update_time
        }

    types = {1:'反馈', 2:'画板'}

    @staticmethod
    def get_type(name):
        types = {'反馈':1, '画板':2}
        if name not in types.keys():
            return False
        return types[name]

    @staticmethod
    def get_type_name(num):
        if num in AppImgs.types:
            return AppImgs.types[num]
        else:
            return '未知'

    def __repr__(self):
        obj = AppImgs.get_keys(self)
        return json.dumps(obj, cls=utils["common"].ComplexEncoder)

    def keys(self):
        return ('uuid', 'tags', 'url', 'base_dir', 'type', 'create_time')

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
    def get_app_imgs_by_page(page_num=1,
                             page_size=Constant.PAGE_SIZE.value,
                             tags=None,
                             url=None,
                             type=None,
                             begin_date=None,
                             end_date=None):
        with db.session.no_autoflush:
            total = AppImgs.get_app_imgs_total(tags, url, type, begin_date, end_date)
            start, end, _ = utils['common'].pagination(page_num, page_size, total)
            exp = AppImgs.query
            if tags:
                tags = tags.strip()
                tags_list = tags.split()
                if len(tags_list)==1:
                    exp = exp.filter(AppImgs.tags.ilike('%{keyword}%'.format(keyword=tags)))
                else:
                    or_ilike_list = []
                    for tag in tags_list:
                        or_ilike_list.append(AppImgs.tags.ilike('%{keyword}%'.format(keyword=tag)))
                    exp = exp.filter(or_(*or_ilike_list))
            if url:
                url = url.strip()
                exp = exp.filter(AppImgs.url == url)
            if type:
                exp = exp.filter(AppImgs.type == type)
            if begin_date and end_date:
                exp = exp.filter(db.and_(AppImgs.create_time <= begin_date, AppImgs.create_time >= end_date))
            return exp.order_by(AppImgs.uuid.asc()).offset(start).limit(page_size).all(), total


    @staticmethod
    def get_app_imgs_total(tags=None, url=None, type=None, begin_date=None, end_date=None):
        exp = db.session.query(db.func.count(AppImgs.uuid))
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
        if begin_date and end_date:
            exp = exp.filter(db.and_(AppImgs.create_time <= begin_date, AppImgs.create_time >= end_date))
        return exp.scalar()

    @staticmethod
    def get_app_imgs_by_ids(img_ids):
        if not isinstance(img_ids, list):
            return False
        if not img_ids:
            return False
        return AppImgs.query.filter(AppImgs.uuid.in_(img_ids)).all()

    @staticmethod
    def save_imgs(obj):
        db.session.add(obj)
        db.session.commit()
        uuid = obj.uuid
        db.session.close()
        return uuid

    @staticmethod
    def batch_save_imgs(params):
        try:
            name = AppImgs.__tablename__
            schema = AppImgs.__table_args__
            schema = schema['schema']
            tbl_name = '{schema}.{table}'.format(schema=schema, table=name)
            sql_insert = []
            sql_insert_dict = {}
            sql_insert_list = []
            i = 0
            for item in params:
                if not item['url']:
                    return
                i = i + 1
                url_key = 'url' + str(i)
                type_key = 'type' + str(i)
                tags_key = 'tags' + str(i)
                base_dir_key = 'base_dir' + str(i)
                sql_insert.append(
                    "(:{url}, :{type}, :{tags}, :{base_dir})".format(url=url_key, type=type_key, tags=tags_key, base_dir=base_dir_key))
                sql_insert_dict[url_key] = item['url']
                sql_insert_dict[type_key] = AppImgs.get_type(item['type']) or 0
                sql_insert_dict[tags_key] = item['tags'] or ''
                sql_insert_dict[base_dir_key] = item['base_dir']
                sql_insert_list.append(sql_insert_dict)

            result = db.session.connection().execute(db.text(
                'insert into {tbl_name} (url, type, tags, base_dir) values {sql_str} RETURNING uuid'
                    .format(tbl_name=tbl_name, sql_str=','.join(sql_insert))), sql_insert_list)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
        finally:
            db.session.close()
        return result.fetchall() if result else None

    @staticmethod
    def update_app_img(uuid, **args):
        info = {'update_time': datetime.now(tz=timezone.utc)}
        for key, val in args.items():
            if hasattr(AppImgs, key) and key != 'uuid' and key != 'create_time' and val:
                info[key] = val
        num_rows_updated = AppImgs.query.filter_by(uuid=uuid).update(info)
        db.session.commit()
        return num_rows_updated

    @staticmethod
    def del_app_img(uuid):
        deleted_objects = AppImgs.__table__.delete().where(AppImgs.uuid == uuid)
        result = db.session.execute(deleted_objects)
        db.session.commit()
        db.session.close()
        return result.rowcount