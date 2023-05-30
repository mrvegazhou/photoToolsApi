# -*- coding: utf-8 -*-
import json
from datetime import datetime
from sqlalchemy import BigInteger, String, SmallInteger
from photo_tools_app.model.base import Base
from photo_tools_app.__init__ import db, utils, func
from photo_tools_app.config.constant import Constant


class AppFeedback(Base):
    __tablename__ = 'app_feedback'
    __table_args__ = {'extend_existing': True, 'schema': 'app'}

    uuid = db.Column(BigInteger, primary_key=True, autoincrement=True, unique=True)
    type = db.Column(SmallInteger, default=1, server_default='1', comment="1 suggest 2 bug")
    content = db.Column(String, unique=False, nullable=False, server_default="", comment="反馈内容")
    contact = db.Column(String, unique=False, nullable=False, server_default="", comment="联系方式")
    imgs = db.Column(String, unique=False, nullable=False, server_default="", comment="图片附件")
    user_id = db.Column(BigInteger, unique=False, nullable=False, server_default="", comment="用户id")
    create_time = db.Column(db.DateTime(timezone=True), comment="创建时间", server_default=func.now(), default=datetime.now)

    def get_keys(self):
        return {
            "uuid": self.uuid,
            "type": self.type,
            "content": self.content,
            "contact": self.contact,
            "create_time": self.create_time,
            "user_id": self.user_id,
            "imgs": self.imgs,
        }

    @staticmethod
    def get_type_str(num):
        if not num:
            return ""
        types = {1:"建议", 2:"bug"}
        if num in types:
            return types[num]
        else:
            return ""

    def __repr__(self):
        obj = AppFeedback.get_keys(self)
        return json.dumps(obj, cls=utils["common"].ComplexEncoder)

    def keys(self):
        return ('uuid', 'type', 'content', 'contact', 'user_id', 'create_time', 'imgs')

    def __getitem__(self, item):
        return getattr(self, item)

    @staticmethod
    def save_feedback_info(obj):
        db.session.add(obj)
        db.session.flush()
        uuid = obj.uuid
        db.session.commit()
        db.session.close()
        return uuid

    @staticmethod
    def update_feedback_imgs(uuid, imgs):
        if not uuid or not imgs:
            return None
        info = {'imgs': imgs}
        num_rows_updated = AppFeedback.query.filter_by(uuid=uuid).update(info)
        db.session.commit()
        return num_rows_updated

    @staticmethod
    def del_feedback(uuid):
        if not uuid:
            return False
        deleted_objects = AppFeedback.__table__.delete().where(AppFeedback.uuid == uuid)
        result = db.session.execute(deleted_objects)
        db.session.commit()
        db.session.close()
        return result.rowcount

    @staticmethod
    def get_feedback_list_by_page(page_num=1,
                                  page_size=Constant.PAGE_SIZE.value,
                                  contact=None,
                                  content=None,
                                  type=None,
                                  begin_date=None,
                                  end_date=None):
        with db.session.no_autoflush:
            exp = AppFeedback.query
            total = AppFeedback.get_app_feedback_total(contact, content, type, begin_date, end_date)
            start, end, _ = utils['common'].pagination(page_num, page_size, total)
            if contact:
                contact = contact.strip()
                exp = exp.filter(AppFeedback.contact.ilike('%{keyword}%'.format(keyword=contact)))
            if content:
                content = content.strip()
                exp = exp.filter(AppFeedback.content.ilike('%{keyword}%'.format(keyword=content)))
            if type:
                exp = exp.filter(AppFeedback.type == type)
            if begin_date and end_date:
                exp = exp.filter(db.and_(AppFeedback.create_time <= begin_date, AppFeedback.create_time >= end_date))
            return exp.order_by(AppFeedback.uuid.asc()).offset(start).limit(page_size).all(), total

    @staticmethod
    def get_app_feedback_total( contact=None,
                                content=None,
                                type=None,
                                begin_date=None,
                                end_date=None):
        exp = db.session.query(db.func.count(AppFeedback.uuid))
        if contact:
            exp = exp.filter(AppFeedback.contact.ilike('%{keyword}%'.format(keyword=contact)))
        if content:
            exp = exp.filter(AppFeedback.content.ilike('%{keyword}%'.format(keyword=content)))
        if type:
            exp = exp.filter(AppFeedback.type == type)
        if begin_date and end_date:
            exp = exp.filter(db.and_(AppFeedback.create_time <= begin_date, AppFeedback.create_time >= end_date))
        return exp.scalar()