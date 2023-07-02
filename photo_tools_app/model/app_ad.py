# -*- coding: utf-8 -*-
import json
from datetime import datetime
from sqlalchemy import BigInteger, String, SmallInteger
from photo_tools_app.model.base import Base
from photo_tools_app.__init__ import db, utils, func
from photo_tools_app.config.constant import Constant


class AppAd(Base):
    __tablename__ = 'app_ad'
    __table_args__ = {'extend_existing': True, 'schema': 'app'}

    uuid = db.Column(BigInteger, primary_key=True, autoincrement=True, unique=True)
    type = db.Column(SmallInteger, default=1, server_default='1', comment="1 首页顶层广告")
    url = db.Column(String, unique=False, nullable=False, server_default="", comment="广告图片")
    content = db.Column(String, unique=False, nullable=False, server_default="", comment="广告内容")
    create_time = db.Column(db.DateTime(timezone=True), comment="创建时间", server_default=func.now(), default=datetime.now)
    update_time = db.Column('update_time', db.DateTime(timezone=True), comment="修改时间")

    def get_keys(self):
        return {
            "uuid": self.uuid,
            "type": self.type,
            "content": self.content,
            "url": self.img,
            "create_time": self.create_time,
            "update_time": self.update_time
        }

    def __repr__(self):
        obj = AppAd.get_keys(self)
        return json.dumps(obj, cls=utils["common"].ComplexEncoder)

    def keys(self):
        return ('uuid', 'type', 'content', 'url', 'create_time', 'update_time')

    @staticmethod
    def get_app_ads_by_type(type=None):
        return AppAd.query.filter(AppAd.type == type).order_by(AppAd.uuid.asc()).all()

    @staticmethod
    def get_app_ads_by_page(page_num=1,
                            page_size=Constant.PAGE_SIZE.value,
                            content=None,
                            url=None,
                            type=None,
                            begin_date=None,
                            end_date=None):
        total = AppAd.get_app_imgs_total(content, url, type, begin_date, end_date)
        start, end, _ = utils['common'].pagination(page_num, page_size, total)
        exp = AppAd.query
        if content:
            content = content.strip()
            exp = exp.filter(AppAd.content.ilike('%{keyword}%'.format(keyword=content)))
        if url:
            url = url.strip()
            exp = exp.filter(AppAd.url.ilike('%{keyword}%'.format(keyword=url)))
        if type:
            exp = exp.filter(AppAd.type == type)
        if begin_date and end_date:
            exp = exp.filter(db.and_(AppAd.create_time <= begin_date, AppAd.create_time >= end_date))
        return exp.order_by(AppAd.uuid.asc()).offset(start).limit(page_size).all(), total

    @staticmethod
    def get_app_ads_total(content=None, url=None, type=None, begin_date=None, end_date=None):
        exp = db.session.query(db.func.count(AppAd.uuid))
        if content:
            content = content.split()
            exp = exp.filter(AppAd.content.ilike('%{keyword}%'.format(keyword=content)))
        if url:
            url = url.strip()
            exp = exp.filter(AppAd.url.ilike('%{keyword}%'.format(keyword=url)))
        if type:
            exp = exp.filter(AppAd.type == type)
        if begin_date and end_date:
            exp = exp.filter(db.and_(AppAd.create_time <= begin_date, AppAd.create_time >= end_date))
        return exp.scalar()

    @staticmethod
    def update_ad_info(uuid, content=None, url=None, tp=None):
        if not uuid:
            return None
        info = {}
        if content:
            info['content'] = content
        if url:
            info['url'] = url
        if tp:
            info['type'] = tp
        num_rows_updated = AppAd.query.filter_by(uuid=uuid).update(info)
        db.session.commit()
        return num_rows_updated

    @staticmethod
    def del_ad(uuid):
        if not uuid:
            return False
        deleted_objects = AppAd.__table__.delete().where(AppAd.uuid == uuid)
        result = db.session.execute(deleted_objects)
        db.session.commit()
        db.session.close()
        return result.rowcount






