# -*- coding: utf-8 -*-
import json
from datetime import datetime
from sqlalchemy import BigInteger, String, or_
from photo_tools_app.model.base import Base
from photo_tools_app.__init__ import db, utils, func
from photo_tools_app.config.constant import Constant


class AppImgLibrary(Base):
    __tablename__ = 'app_img_library'
    __table_args__ = {'extend_existing': True, 'schema': 'app'}

    uuid = db.Column(BigInteger, primary_key=True, autoincrement=True, unique=True)
    tags = db.Column(String, nullable=False, server_default="", comment="标签")
    note = db.Column(String, nullable=False, server_default="", comment="备注")
    url = db.Column(String, nullable=False, server_default="", comment="地址")
    base_dir = db.Column(String, nullable=False, server_default="", comment="存储根目录")
    hash_str = db.Column(String, nullable=False, server_default="", comment="img hash")
    create_time = db.Column(db.DateTime(timezone=True), comment="创建时间", server_default=func.now(), default=datetime.now)
    update_time = db.Column('update_time', db.DateTime(timezone=True), comment="修改时间")

    def get_keys(self):
        return {
            "uuid": self.uuid,
            "tags": self.tags,
            "note": self.note,
            "url": self.url,
            "base_dir": self.base_dir,
            "hash_str": self.hash_str,
            "create_time": self.create_time,
            "update_time": self.update_time
        }

    def __repr__(self):
        obj = AppImgLibrary.get_keys(self)
        return json.dumps(obj, cls=utils["common"].ComplexEncoder)

    def keys(self):
        return ('uuid', 'tags', 'url', 'base_dir', 'note', 'hash_str', 'create_time')

    def __getitem__(self, item):
        return getattr(self, item)

    @staticmethod
    def get_app_imgs(page_num=1,
                     page_size=Constant.PAGE_SIZE.value,
                     tags=None,
                     url=None,
                     note=None,
                     load_time=None,
                     begin_date=None,
                     end_date=None):
        exp = AppImgLibrary.query
        if page_num<=0:
            page_num = 1
        start = (page_num - 1) * page_size
        if tags:
            tags_list = tags.split()
            if len(tags_list)==1:
                exp = exp.filter(AppImgLibrary.tags.ilike('%{keyword}%'.format(keyword=tags)))
            else:
                or_ilike_list = []
                for tag in tags_list:
                    or_ilike_list.append(AppImgLibrary.tags.ilike('%{keyword}%'.format(keyword=tag)))
                exp = exp.filter(or_(*or_ilike_list))
        if url:
            exp = exp.filter(AppImgLibrary.url == url)
        if note:
            exp = exp.filter(AppImgLibrary.note == note)
        if load_time:
            exp = exp.filter(AppImgLibrary.create_time <= load_time)
        if begin_date and end_date:
            exp = exp.filter(db.and_(AppImgLibrary.create_time <= begin_date, AppImgLibrary.create_time >= end_date))
        return exp.order_by(AppImgLibrary.uuid.asc()).offset(start).limit(page_size).all()

    @staticmethod
    def get_app_imgs_by_page(page_num=1,
                             page_size=Constant.PAGE_SIZE.value,
                             tags=None,
                             url=None,
                             note=None,
                             begin_date=None,
                             end_date=None):
        total = AppImgLibrary.get_app_imgs_total(tags, url, note, begin_date, end_date)
        start, end, _ = utils['common'].pagination(page_num, page_size, total)
        exp = AppImgLibrary.query
        if tags:
            tags = tags.strip()
            tags_list = tags.split()
            if len(tags_list)==1:
                exp = exp.filter(AppImgLibrary.tags.ilike('%{keyword}%'.format(keyword=tags)))
            else:
                or_ilike_list = []
                for tag in tags_list:
                    or_ilike_list.append(AppImgLibrary.tags.ilike('%{keyword}%'.format(keyword=tag)))
                exp = exp.filter(or_(*or_ilike_list))
        if url:
            url = url.strip()
            exp = exp.filter(AppImgLibrary.url == url)
        if note:
            exp = exp.filter(AppImgLibrary.note == note)
        if begin_date and end_date:
            exp = exp.filter(db.and_(AppImgLibrary.create_time <= begin_date, AppImgLibrary.create_time >= end_date))
        return exp.order_by(AppImgLibrary.uuid.asc()).offset(start).limit(page_size).all(), total


    @staticmethod
    def get_app_imgs_total(tags=None, url=None, note=None, begin_date=None, end_date=None):
        exp = db.session.query(db.func.count(AppImgLibrary.uuid))
        if tags:
            tags_list = tags.split()
            if len(tags_list)==1:
                exp = exp.filter(AppImgLibrary.tags.ilike('%{keyword}%'.format(keyword=tags)))
            else:
                or_ilike_list = []
                for tag in tags_list:
                    or_ilike_list.append(AppImgLibrary.tags.ilike('%{keyword}%'.format(keyword=tag)))
                exp = exp.filter(or_(*or_ilike_list))
        if url:
            exp = exp.filter(AppImgLibrary.url == url)
        if note:
            exp = exp.filter(AppImgLibrary.note == note)
        if begin_date and end_date:
            exp = exp.filter(db.and_(AppImgLibrary.create_time <= begin_date, AppImgLibrary.create_time >= end_date))
        return exp.scalar()

    @staticmethod
    def get_app_imgs_by_ids(img_ids):
        if not isinstance(img_ids, list):
            return False
        if not img_ids:
            return False
        return AppImgLibrary.query.filter(AppImgLibrary.uuid.in_(img_ids)).all()

    @staticmethod
    def save_imgs(obj):
        db.session.add(obj)
        db.session.commit()
        uuid = obj.uuid
        db.session.close()
        return uuid

    @staticmethod
    def del_app_img_lib(uuid):
        deleted_objects = AppImgLibrary.__table__.delete().where(AppImgLibrary.uuid == uuid)
        result = db.session.execute(deleted_objects)
        db.session.commit()
        db.session.close()
        return result.rowcount

    @staticmethod
    def update_app_img_lib(uuid=None, tags=None, url=None, note=None):
        if not uuid:
            return None
        args = {}
        if tags:
            args['tags'] = tags
        if url:
            args['url'] = url
        if note:
            args['note'] = note
        num_rows_updated = AppImgLibrary.query.filter(AppImgLibrary.uuid == uuid).update(args)
        db.session.commit()
        db.session.close()
        return num_rows_updated
