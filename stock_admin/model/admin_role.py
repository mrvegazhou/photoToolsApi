# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
from datetime import datetime, timezone
from stock_admin.model.base import Base
from stock_admin.__init__ import db, utils, func
from stock_admin.config.constant import Constant

class AdminRole(Base):

    __tablename__ = 'admin_role'
    __table_args__ = {'extend_existing': True, 'schema': 'stock'}

    uuid = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    title = db.Column(db.String(255), nullable=False, comment="角色名称")
    sorts = db.Column(db.Integer, nullable=False, default=0, server_default='0', comment="角色排序")
    description = db.Column(db.String(255), server_default="", comment="角色描述")
    status = db.Column(db.SMALLINT, nullable=False, default=1, server_default='1', comment="1 正常 0 禁止")
    create_time = db.Column(db.TIMESTAMP, comment="创建时间", server_default=func.now())
    update_time = db.Column(db.TIMESTAMP, comment="修改时间")
    delete_time = db.Column(db.TIMESTAMP, comment="删除时间")

    def get_keys(self):
        return {
            "uuid": self.uuid,
            "title": self.title,
            "sorts": self.sorts,
            "description": self.description,
            "status": self.status
        }

    @staticmethod
    def add_new_admin_role(title=None, sorts=0, description=None, status=1):
        tmp = AdminRole()
        tmp.title = title
        tmp.sorts = sorts
        tmp.description = description
        tmp.status = status

        db.session.add(tmp)
        db.session.flush()
        uuid = tmp.uuid
        db.session.commit()
        db.session.close()
        return uuid

    @staticmethod
    def get_roles(role_ids=[]):
        if not role_ids:
            return AdminRole.query.filter_by(delete_time=None).order_by(AdminRole.sorts.asc()).all()
        else:
            return AdminRole.query.filter(AdminRole.uuid.in_(role_ids)).filter(AdminRole.delete_time == None).order_by(AdminRole.sorts.asc()).all()

    @staticmethod
    def get_roles_by_condition(page_num=1, page_size=Constant.ADMIN_PAGE_SIZE.value, **kargs):
        total = AdminRole.get_roles_total_by_condition(**kargs)
        start, end = utils['common'].pagination(page_num, page_size, total)
        exp = AdminRole.query
        exp = exp.filter(AdminRole.delete_time == None)
        new_kwargs = {}
        for key, val in kargs.items():
            if hasattr(AdminRole, key) and (val is not None):
                if key=='title':
                    exp = exp.filter(AdminRole.title.like('%{0}%'.format(val)))
                elif key=='description':
                    exp = exp.filter(AdminRole.description.like('%{0}%'.format(val)))
                else:
                    new_kwargs[key] = val
        if new_kwargs:
            exp = exp.filter_by(**new_kwargs)
        return exp.order_by(AdminRole.uuid.asc()).offset(start).limit(page_size).all(), total

    @staticmethod
    def get_roles_total_by_condition(**kwargs):
        exp = db.session.query(db.func.count(AdminRole.uuid))
        exp = exp.filter(AdminRole.delete_time == None)
        for key, val in kwargs.items():
            if hasattr(AdminRole, key) and (val is not None):
                if key == 'title':
                    exp = exp.filter(AdminRole.title.like('%{0}%'.format(val)))
                elif key == 'description':
                    exp = exp.filter(AdminRole.description.like('%{0}%'.format(val)))
                elif key == 'status':
                    exp = exp.filter(AdminRole.status==val)
        return exp.scalar()

    @staticmethod
    def get_role(role_id):
        return AdminRole.query.filter_by(delete_time=None).filter_by(uuid=role_id).first()

    @staticmethod
    def get_role_by_condition(**kwargs):
        exp = AdminRole.query
        new_kwargs = {}
        for key, val in kwargs.items():
            if hasattr(AdminRole, key) and (val is not None):
                new_kwargs[key] = val
        if new_kwargs:
            exp = exp.filter_by(**new_kwargs)
        return exp.filter_by(delete_time=None).order_by(AdminRole.uuid.asc()).all()

    @staticmethod
    def update_role_info(uuid, **kwargs):
        info = {'update_time': datetime.now(tz=timezone.utc)}
        for key, val in kwargs.items():
            if hasattr(AdminRole, key) and key != 'uuid' and key != 'create_time':
                info[key] = val
        num_rows_updated = AdminRole.query.filter_by(uuid=uuid).update(info)
        db.session.commit()
        return num_rows_updated

    @staticmethod
    def del_role(uuid):
        num_rows_updated = AdminRole.query.filter_by(uuid=uuid).update(
            dict(delete_time=datetime.now(tz=timezone.utc)))
        db.session.commit()
        return num_rows_updated.rowcount



