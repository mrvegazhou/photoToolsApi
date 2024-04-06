# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
from datetime import datetime, timezone
from stock_admin.__init__ import db, utils, func
from stock_admin.model.base import Base
from stock_admin.config.constant import Constant

# https://www.jianshu.com/p/5a27a826866e

class AdminUser(Base):

    __tablename__ = 'admin_user'

    uuid = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    username = db.Column(db.String(255), unique=True, nullable=False, server_default="", comment="管理员名称")
    password = db.Column(db.String(255), nullable=False, server_default="", comment="管理员密码")
    salt = db.Column(db.String(5), nullable=False, server_default="", comment="salt")
    phone = db.Column(db.String(50), nullable=False, server_default="", comment="手机号码")
    email = db.Column(db.String(255), nullable=False, server_default="", comment="email")
    description = db.Column(db.String(255), server_default="", comment="描述")
    status = db.Column(db.SMALLINT, default=1, server_default='1', comment="1 正常 0 禁止")
    create_time = db.Column(db.TIMESTAMP, comment="创建时间", server_default=func.now())
    update_time = db.Column(db.TIMESTAMP, comment="修改时间")
    delete_time = db.Column(db.TIMESTAMP, comment="删除时间")

    def get_keys(self):
        return {
            "uuid": self.uuid,
            "username": self.username,
            "password": self.password,
            "phone": self.phone,
            "email": self.email,
            "description": self.description,
            "status": self.status,
            "create_time": self.create_time
        }

    @staticmethod
    def add_new_admin_user(username, password, phone, email, description, status):
        tmp = AdminUser()
        tmp.username = username
        salt = utils['common'].gen_random_str(5)
        tmp.salt = salt
        tmp.password = utils['common'].md5('{}{}'.format(password, salt))
        tmp.phone = phone
        tmp.email = email
        tmp.description = description
        tmp.status = status
        db.session.add(tmp)
        db.session.commit()
        uuid = tmp.uuid
        return uuid

    @staticmethod
    def update_admin_user_status(uuid, status):
        num_rows_updated = AdminUser.query.filter_by(uuid=uuid).update(
            dict(status=status))
        db.session.commit()
        return num_rows_updated

    @staticmethod
    def update_admin_user_info(uuid, **args):
        info = {'update_time': datetime.now(tz=timezone.utc)}
        for key, val in args.items():
            if hasattr(AdminUser, key) and key != 'uuid' and key != 'create_time' and key != 'password':
                info[key] = val
            elif key=='password':
                info['salt'] = utils['common'].gen_random_str(5)
                info['password'] = utils['common'].md5('{}{}'.format(val, info['salt']))
        num_rows_updated = AdminUser.query.filter_by(uuid=uuid).update(info)
        db.session.commit()
        return num_rows_updated

    @staticmethod
    def get_userinfo_by_name(username):
        return AdminUser.query.filter_by(username=username).first()

    @staticmethod
    def get_userinfo_by_uuid(uuid):
        return AdminUser.query.filter_by(uuid=uuid).first()

    @staticmethod
    def get_users(page_num=1, page_size=Constant.ADMIN_PAGE_SIZE, username=None, phone=None, email=None, status=None):
        total = AdminUser.get_users_total(username, phone, email, status)
        start, end = utils['common'].pagination(page_num, page_size, total)
        exp = AdminUser.query.filter(AdminUser.delete_time==None)
        if status:
            exp = exp.filter(AdminUser.status == status)
        if username:
            exp = exp.filter(AdminUser.username == username)
        if phone:
            exp = exp.filter(AdminUser.phone == phone)
        if email:
            exp = exp.filter(AdminUser.email == email)
        return exp.order_by(AdminUser.uuid.asc()).offset(start).limit(page_size).all(), total

    @staticmethod
    def get_users_total(username=None, phone=None, email=None, status=None):
        exp = db.session.query(db.func.count(AdminUser.uuid))
        if status:
            exp = exp.filter(AdminUser.status == status)
        if username:
            exp = exp.filter(AdminUser.username == username)
        if phone:
            exp = exp.filter(AdminUser.phone == phone)
        if email:
            exp = exp.filter(AdminUser.email == email)
        return exp.scalar()

    @staticmethod
    def del_user(ids):
        info = {'delete_time': datetime.now(tz=timezone.utc)}
        num_rows_updated = AdminUser.query.filter(AdminUser.uuid.in_(ids)).update(info)
        db.session.commit()
        return num_rows_updated





if __name__ == "__main__":
    res = AdminUser.update_admin_user_info(3, email='admin2@qq.com')
    print(res)






