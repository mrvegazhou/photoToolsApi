# -*- coding: utf-8 -*-
import json
from datetime import datetime, timezone
from sqlalchemy import BigInteger, String, SmallInteger
from photo_tools_app.model.base import Base
from photo_tools_app.__init__ import db, utils, func
from photo_tools_app.config.constant import Constant


class AppUser(Base):

    __tablename__ = 'app_user'
    __table_args__ = {'extend_existing': True, 'schema': 'app'}

    uuid = db.Column(BigInteger, primary_key=True, autoincrement=True, unique=True)  # id 整型，主键，自增，唯一
    username = db.Column(String, unique=True, nullable=False, server_default="", comment="用户名")
    phone = db.Column(String, nullable=False, server_default="", comment="手机号码")
    email = db.Column(String, nullable=False, server_default="", comment="email")
    description = db.Column(String, server_default="", comment="描述")
    type = db.Column(SmallInteger, default=1, server_default='1', comment="1 wechat 2 其他")
    openid = db.Column(String, default=1, server_default='', comment="wechat openid")
    status = db.Column(SmallInteger, default=1, server_default='1', comment="1 正常 0 禁止")
    create_time = db.Column(db.DateTime(timezone=True), comment="创建时间", server_default=func.now(), default=datetime.now)
    update_time = db.Column(db.DateTime(timezone=True), comment="修改时间", onupdate=datetime.utcnow)
    delete_time = db.Column(db.DateTime(timezone=True), comment="删除时间")

    def get_keys(self):
        return {
            "uuid": self.uuid,
            "username": self.username,
            "phone": self.phone,
            "email": self.email,
            "description": self.description,
            "type": self.type,
            "openid": self.openid,
            "status": self.status,
            "create_time": self.create_time,
            "update_time": self.update_time,
            "delete_time": self.delete_time
        }

    def __repr__(self):
        obj = {
            "uuid": self.uuid,
            "username": self.username,
            "phone": self.phone,
            "email": self.email,
            "status": self.status,
            "description": self.description,
            "type": self.type
        }
        return json.dumps(obj, cls=utils["common"].ComplexEncoder)

    @staticmethod
    def add_app_user_info(obj):
        db.session.add(obj)
        db.session.commit()
        uuid = obj.uuid
        return uuid

    @staticmethod
    def get_userinfo_by_uuid(uuid):
        return AppUser.query.filter_by(uuid=uuid).first()

    @staticmethod
    def get_user_list_by_uuids(uuids):
        return AppUser.query.filter(AppUser.uuid.in_(uuids)).order_by(AppUser.uuid.asc()).all()

    @staticmethod
    def get_app_user_info_by_attr(attrs, cols=None):
        name = AppUser.__tablename__
        schema = AppUser.__table_args__
        schema = schema['schema']
        tbl_name = '{schema}.{table}'.format(schema=schema, table=name)
        if cols:
            cols = ['{}.{}'.format(tbl_name, col) for col in cols]
            cols = ','.join(cols)
        else:
            cols = '*'
        attrs_str = []
        vals_str = {}
        for attr in attrs:
            attrs_str.append('{}{}:{}'.format(attr['name'], attr['op'], attr['name']))
            vals_str[attr['name']] = attr['val']
        attrs_str = ' and '.join(attrs_str)
        result = db.session.connection().execute(db.text(
            'select {cols} from {tbl_name} where {attrs_str}'.format(
                cols=cols, tbl_name=tbl_name, attrs_str=attrs_str)),
            vals_str)
        return result.fetchone()

    def get_all(self):
        return self.query.all()

    @staticmethod
    def update_status(uuid, status):
        num_rows_updated = AppUser.query.filter_by(uuid=uuid).update(
            dict(status=status))
        db.session.commit()
        db.session.close()
        return num_rows_updated

    @staticmethod
    def update_role_info(uuid, **kwargs):
        info = {'update_time': datetime.now(tz=timezone.utc)}
        for key, val in kwargs.items():
            if hasattr(AppUser, key) and key != 'uuid' and key != 'create_time':
                info[key] = val
        num_rows_updated = AppUser.query.filter_by(uuid=uuid).update(info)
        db.session.commit()
        return num_rows_updated

    @staticmethod
    def get_app_users(page_num=1,
                      page_size=Constant.PAGE_SIZE.value,
                      username=None,
                      phone=None,
                      email=None,
                      description=None,
                      type=None,
                      status=None,
                      begin_date=None,
                      end_date=None):
        total = AppUser.get_app_users_total(username, phone, email, description, status, begin_date, end_date)
        start, end, _ = utils['common'].pagination(page_num, page_size, total)
        exp = AppUser.query.filter(AppUser.delete_time == None)
        if status:
            exp = exp.filter(AppUser.status == status)
        if username:
            exp = exp.filter(AppUser.username == username)
        if phone:
            exp = exp.filter(AppUser.phone == phone)
        if email:
            exp = exp.filter(AppUser.email == email)
        if description:
            exp = exp.filter(AppUser.description == description)
        if type:
            exp = exp.filter(AppUser.type == type)
        if begin_date and end_date:
            exp = exp.filter(db.and_(AppUser.create_time <= begin_date, AppUser.create_time >= end_date))
        return exp.order_by(AppUser.uuid.asc()).offset(start).limit(page_size).all(), total

    @staticmethod
    def get_app_users_total(username=None,
                            phone=None,
                            email=None,
                            description=None,
                            type=None,
                            status=None,
                            begin_date=None,
                            end_date=None):
        exp = db.session.query(db.func.count(AppUser.uuid))
        if status:
            exp = exp.filter(AppUser.status == status)
        if username:
            exp = exp.filter(AppUser.username == username)
        if phone:
            exp = exp.filter(AppUser.phone == phone)
        if email:
            exp = exp.filter(AppUser.email == email)
        if description:
            exp = exp.filter(AppUser.description == description)
        if type:
            exp = exp.filter(AppUser.type == type)
        if begin_date and end_date:
            exp = exp.filter(db.and_(AppUser.create_time <= begin_date, AppUser.create_time >= end_date))
        return exp.scalar()

    @staticmethod
    def del_user(ids):
        info = {'delete_time': datetime.now(tz=timezone.utc)}
        num_rows_updated = AppUser.query.filter(AppUser.uuid.in_(ids)).update(info)
        db.session.commit()
        return num_rows_updated

    @staticmethod
    def update_app_user_info(uuid, **args):
        info = {'update_time': datetime.now(tz=timezone.utc)}
        for key, val in args.items():
            if hasattr(AppUser, key) and key != 'uuid' and key != 'create_time':
                info[key] = val
        num_rows_updated = AppUser.query.filter_by(uuid=uuid).update(info)
        db.session.commit()
        return num_rows_updated


