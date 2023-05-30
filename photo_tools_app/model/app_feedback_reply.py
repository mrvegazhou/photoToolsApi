# -*- coding: utf-8 -*-
import json
from datetime import datetime
from sqlalchemy import BigInteger, String
from photo_tools_app.model.base import Base
from photo_tools_app.__init__ import db, utils, func


class AppFeedbackRelpy(Base):
    __tablename__ = 'app_feedback_reply'
    __table_args__ = {'extend_existing': True, 'schema': 'app'}

    uuid = db.Column(BigInteger, primary_key=True, autoincrement=True, unique=True)
    content = db.Column(String, unique=False, nullable=False, server_default="", comment="反馈内容")
    to_user_id = db.Column(BigInteger, unique=False, nullable=False, server_default="", comment="用户id")
    reply_user_id = db.Column(BigInteger, unique=False, nullable=False, server_default="", comment="用户id")
    # 需要加索引
    feedback_id = db.Column(BigInteger, unique=False, nullable=False, server_default="", comment="反馈id")
    create_time = db.Column(db.DateTime(timezone=True), comment="创建时间", server_default=func.now(), default=datetime.now)


    def get_keys(self):
        return {
            "uuid": self.uuid,
            "content": self.content,
            "to_user_id": self.to_user_id,
            "reply_user_id": self.reply_user_id,
            "feedback_id": self.feedback_id,
            "create_time": self.create_time,
        }

    def __repr__(self):
        obj = AppFeedbackRelpy.get_keys(self)
        return json.dumps(obj, cls=utils["common"].ComplexEncoder)

    def keys(self):
        return ('uuid', 'content', 'to_user_id', 'reply_user_id', 'feedback_id', 'create_time')

    def __getitem__(self, item):
        return getattr(self, item)

    @staticmethod
    def save_feedback_reply_info(obj):
        db.session.add(obj)
        db.session.flush()
        uuid = obj.uuid
        db.session.commit()
        db.session.close()
        return uuid

    @staticmethod
    def get_relpy_list_by_feedback_id(feedback_id, content, to_user_id, reply_user_id):
        if not feedback_id:
            return False
        exp = AppFeedbackRelpy.query
        if feedback_id:
            exp = exp.filter(AppFeedbackRelpy.feedback_id == feedback_id)
        if content:
            exp = exp.filter(AppFeedbackRelpy.content.ilike('%{keyword}%'.format(keyword=content)))
        if to_user_id:
            exp = exp.filter(AppFeedbackRelpy.to_user_id == to_user_id)
        if reply_user_id:
            exp = exp.filter(AppFeedbackRelpy.reply_user_id == reply_user_id)
        return exp.order_by(AppFeedbackRelpy.create_time.desc()).all()

    @staticmethod
    def del_feedback_reply(feedback_id):
        if not feedback_id:
            return False
        deleted_objects = AppFeedbackRelpy.__table__.delete().where(AppFeedbackRelpy.feedback_id == feedback_id)
        result = db.session.execute(deleted_objects)
        db.session.commit()
        db.session.close()
        return result.rowcount

    @staticmethod
    def get_reply_feedback_list(feedback_id):
        if not feedback_id:
            return False
        return AppFeedbackRelpy.query.filter(AppFeedbackRelpy.feedback_id == feedback_id).order_by(AppFeedbackRelpy.create_time.desc()).all()


    @staticmethod
    def test_sesson_tran(uuid=2):
        db.session.begin_nested()
        deleted_by_role_id = AppFeedbackRelpy.__table__.delete().where(AppFeedbackRelpy.uuid == uuid)
        db.session.execute(deleted_by_role_id)
        db.session.flush()
        info = AppFeedbackRelpy.query.filter(AppFeedbackRelpy.uuid == uuid).order_by(AppFeedbackRelpy.create_time.desc()).first()
        print(info, "---info----")
        cur = db.session.connection().execute(db.text("INSERT INTO app.app_feedback_reply (content, to_user_id, reply_user_id, feedback_id) VALUES ('test', 1, 1, 1) RETURNING app.app_feedback_reply.uuid"))
        db.session.flush()

        if cur.lastrowid==0:
            print(cur.lastrowid, "----cur----")
            db.session.rollback()

        db.session.commit()


