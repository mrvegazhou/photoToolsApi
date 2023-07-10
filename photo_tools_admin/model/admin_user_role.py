# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/photo-tools-api")
import typing
from datetime import datetime
from sqlalchemy import BigInteger
from photo_tools_admin.model.base import Base
from photo_tools_admin.__init__ import db, func


class AdminUserRole(Base):

    __tablename__ = 'admin_user_role'

    uuid = db.Column(BigInteger, primary_key=True, autoincrement=True, unique=True)
    role_id = db.Column(BigInteger, nullable=False, unique=True, comment="角色标识")
    admin_user_id = db.Column(BigInteger, nullable=False, unique=True, comment="管理员标识")
    create_time = db.Column(db.DateTime(timezone=True), comment="创建时间", server_default=func.now(), default=datetime.now)

    def get_keys(self):
        return {
            "uuid": self.uuid,
            "role_id": self.role_id,
            "admin_user_id": self.admin_user_id,
            "create_time": self.create_time
        }

    @staticmethod
    def get_user_role_info(user_id):
        return AdminUserRole.query.filter_by(admin_user_id=user_id).order_by(AdminUserRole.uuid.asc()).all()

    @staticmethod
    def assign_user_roles(admin_user_id, role_ids: typing.List):
        '''insert into admin.admin_user_role (role_id, admin_user_id) values (4, 3) ON conflict(role_id, admin_user_id) DO UPDATE SET create_time=NOW()'''
        name = AdminUserRole.__tablename__
        schema = AdminUserRole.__table_args__
        schema = schema['schema']
        tbl_name = '{schema}.{table}'.format(schema=schema, table=name)
        sql_insert = []
        sql_insert_dict = {'user_id': admin_user_id}
        i = 0
        for role_id in role_ids:
            i = i + 1
            key = 'role_id'+str(i)
            sql_insert.append("(:user_id, :{role_id})".format(role_id=key))
            sql_insert_dict[key] = role_id
        sql_insert = ','.join(sql_insert)
        result = db.session.connection().execute(db.text(
            'insert into {tbl_name} (admin_user_id, role_id) values {sql_str} ON conflict(admin_user_id, role_id) DO UPDATE SET create_time=NOW()'
                .format(tbl_name=tbl_name, sql_str=sql_insert)), sql_insert_dict)
        db.session.commit()
        return result.rowcount

    @staticmethod
    def add_user_role(admin_user_id, role_id):
        tmp = AdminUserRole()
        tmp.role_id = role_id
        tmp.admin_user_id = admin_user_id
        db.session.add(tmp)
        db.session.flush()
        uuid = tmp.uuid
        db.session.commit()
        return uuid

    @staticmethod
    def del_by_admin_user(uuid):
        # app.config["SQLALCHEMY_ECHO"] = True
        deleted_objects = AdminUserRole.__table__.delete().where(AdminUserRole.uuid==uuid)
        result = db.session.execute(deleted_objects)
        db.session.commit()
        return result.rowcount

    @staticmethod
    def get_user_role_dict(admin_user_ids):
        name = AdminUserRole.__tablename__
        schema = AdminUserRole.__table_args__
        schema = schema['schema']
        admin_user_ids = ','.join('%s' %id for id in admin_user_ids)
        tbl_name = '{schema}.{table}'.format(schema=schema, table=name)
        return db.session.connection().execute(db.text(
            "SELECT  admin_user_id, array_to_string(ARRAY(SELECT unnest(array_agg(role_id))),',') AS role_ids FROM {schema}.admin_user_role where admin_user_id in ({admin_user_ids}) GROUP BY admin_user_id"
                .format(schema=schema, tbl_name=tbl_name, admin_user_ids=admin_user_ids))).fetchall()



if __name__ == "__main__":
    res = AdminUserRole.get_user_role_dict([1])
    print(res, "---s---")







