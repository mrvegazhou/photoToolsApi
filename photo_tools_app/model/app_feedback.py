# -*- coding: utf-8 -*-
import json
from photo_tools_app.model.base import Base
from photo_tools_app.__init__ import db, utils, func


class AppFeedback(Base):
    __tablename__ = 'app_feedback'
    __table_args__ = {'extend_existing': True, 'schema': 'app'}

    uuid = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    type = db.Column(db.SMALLINT, default=1, server_default='1', comment="1 suggest 2 bug")
    content = db.Column(db.Text, unique=False, nullable=False, server_default="", comment="反馈内容")
    contact = db.Column(db.Text, unique=False, nullable=False, server_default="", comment="联系方式")
    imgs = db.Column(db.String(50), unique=False, nullable=False, server_default="", comment="图片附件")
    user_id = db.Column(db.Integer, unique=False, nullable=False, server_default="", comment="用户id")
    create_time = db.Column(db.TIMESTAMP, comment="创建时间", server_default=func.now())

    def get_keys(self):
        return {
            "uuid": self.uuid,
            "type": self.type,
            "content": self.content,
            "contact": self.contact,
            "create_time": self.create_time,
            "user_id": self.user_id
        }

    def __repr__(self):
        obj = AppFeedback.get_keys(self)
        return json.dumps(obj, cls=utils["common"].ComplexEncoder)

    def keys(self):
        return ('uuid', 'tyoe', 'content', 'contact', 'user_id', 'create_time')

    def __getitem__(self, item):
        return getattr(self, item)

    @staticmethod
    def save_feedback_info(obj):
        db.session.add(obj)
        db.session.flush()
        uuid = obj.uuid
        db.session.commit()
        return uuid

    @staticmethod
    def update_feedback_imgs(uuid, imgs):
        if not uuid or not imgs:
            return None
        info = {'imgs': imgs}
        num_rows_updated = AppFeedback.query.filter_by(uuid=uuid).update(info)
        db.session.commit()
        return num_rows_updated