# -*- coding: utf-8 -*-
import json
from photo_tools_app.model.base import Base
from photo_tools_app.__init__ import db, utils, func
from photo_tools_app.config.constant import Constant


class AppScheduledTasks(Base):
    __tablename__ = 'app_scheduled_tasks'
    __table_args__ = {'extend_existing': True, 'schema': 'app'}

    uuid = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = db.Column(db.Integer, nullable=False, server_default="", comment="用户id")
    type = db.Column(db.Integer, nullable=False, server_default="", comment="类型 1.图片处理 ")
    status = db.Column(db.Integer, nullable=False, server_default="", comment="1:正常;2:处理异常;3:无法处理")
    title = db.Column(db.String(), nullable=False, server_default="", comment="执行标题")
    content = db.Column(db.String(), nullable=False, server_default="", comment="执行内容")
    expire_age = db.Column(db.Integer, nullable=False, server_default="0", comment="过期时间段")
    create_time = db.Column('create_time', db.TIMESTAMP, comment="创建时间", server_default=func.now())
    update_time = db.Column('update_time', db.TIMESTAMP, comment="修改时间")

    def get_keys(self):
        return {
            "uuid": self.uuid,
            "user_id": self.user_id,
            "type": self.type,
            "status": self.status,
            "title": self.title,
            "content": self.content,
            "expire_age": self.expire_age,
            "create_time": self.create_time,
            "update_time": self.update_time
        }

    def __repr__(self):
        obj = AppScheduledTasks.get_keys(self)
        return json.dumps(obj, cls=utils["common"].ComplexEncoder)

    def __getitem__(self, item):
        return getattr(self, item)


    @staticmethod
    def save_scheduled_task(obj):
        db.session.add(obj)
        db.session.flush()
        uuid = obj.uuid
        db.session.commit()
        db.session.close()
        return uuid

    @staticmethod
    def get_scheduled_task_list_by_type(start=0,
                                        page_size=Constant.PAGE_SIZE.value,
                                        type=None):
        if not type:
            return None
        exp = AppScheduledTasks.query.filter(AppScheduledTasks.type == type)
        return exp.order_by(AppScheduledTasks.uuid.asc()).offset(start).limit(page_size).all()

    @staticmethod
    def get_scheduled_task_list_total(type=None):
        if not type:
            return None
        try:
            exp = db.session.query(db.func.count(AppScheduledTasks.uuid))
            exp = exp.filter(AppScheduledTasks.type == type)
            return exp.scalar()
        except Exception as ex:
            print(str(ex))

    @staticmethod
    def del_scheduled_task_info(uuid):
        deleted_objects = AppScheduledTasks.__table__.delete().where(AppScheduledTasks.uuid == uuid)
        result = db.session.execute(deleted_objects)
        db.session.commit()
        db.session.close()
        return result.rowcount

    @staticmethod
    def get_scheduled_task_list_by_user(user_id, type):
        if not type or not user_id:
            return None
        exp = AppScheduledTasks.query.filter(AppScheduledTasks.type == type).filter(AppScheduledTasks.user_id == user_id)
        return exp.all()