# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
from datetime import datetime, timezone
from stock_admin.model.base import Base
from stock_admin.__init__ import db, func
from stock_admin.model.admin_role_menu_power import AdminRoleMenuPower


class AdminMenuPower(Base):
    __tablename__ = 'admin_menu_power'

    uuid = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    menu_id = db.Column(db.Integer, nullable=False, unique=True)
    title = db.Column(db.String(255), nullable=False, comment="操作名称")
    code = db.Column(db.String(255), nullable=False, comment="操作code")
    description = db.Column(db.String(255), server_default="", comment="描述")
    status = db.Column(db.SMALLINT, default=1, server_default='1', comment="1 正常 0 禁止")
    sorts = db.Column(db.Integer, nullable=False, default=0, server_default='0', comment="操作排序")
    create_time = db.Column(db.TIMESTAMP, comment="创建时间", server_default=func.now())
    update_time = db.Column(db.TIMESTAMP, comment="修改时间")

    def get_keys(self):
        return {
            "uuid": self.uuid,
            "menu_id": self.menu_id,
            "title": self.title,
            "code": self.code,
            "sorts": self.sorts,
            "description": self.description,
            "status": self.status
        }

    @staticmethod
    def get_powers_by_menu_ids(ids=[], order=True):
        if order:
            return AdminMenuPower.query.filter(AdminMenuPower.menu_id.in_(ids)).order_by(AdminMenuPower.sorts.asc()).all()
        else:
            return AdminMenuPower.query.filter(AdminMenuPower.menu_id.in_(ids)).order_by(AdminMenuPower.uuid.asc()).all()

    @staticmethod
    def get_powers_by_power_ids(ids=[], order=True):
        if order:
            return AdminMenuPower.query.filter(AdminMenuPower.uuid.in_(ids)).order_by(AdminMenuPower.sorts.asc()).all()
        else:
            return AdminMenuPower.query.filter(AdminMenuPower.uuid.in_(ids)).all()

    @staticmethod
    def add_menu_power(menu_id, title, code, description, sorts=1, status=1):
        tmp = AdminMenuPower()

        tmp.menu_id = menu_id
        tmp.title = title
        tmp.code = code
        tmp.sorts = sorts
        tmp.description = description
        tmp.status = status

        db.session.add(tmp)
        db.session.commit()
        uuid = tmp.uuid
        return uuid

    @staticmethod
    def update_menu_power(uuid, **args):
        info = {'update_time': datetime.now(tz=timezone.utc)}
        for key, val in args.items():
            if hasattr(AdminMenuPower, key) and key != 'uuid' and key != 'create_time':
                info[key] = val
        num_rows_updated = AdminMenuPower.query.filter_by(uuid=uuid).update(info)
        db.session.commit()
        return num_rows_updated

    @staticmethod
    def del_menu_power(uuid):
        flag = False
        try:
            with db.session.begin(subtransactions=True):
                deleted_objects = AdminMenuPower.__table__.delete().where(AdminMenuPower.uuid == uuid)
                db.session.execute(deleted_objects)
                deleted_objects = AdminRoleMenuPower.__table__.delete().where(AdminRoleMenuPower.power_id == uuid)
                db.session.execute(deleted_objects)
                flag = True
        except Exception as e:
            flag = False
            db.session.rollback()
        db.session.commit()
        return flag

    @staticmethod
    def get_menu_powers_by_group_menu_id(menu_ids):
        name = AdminMenuPower.__tablename__
        schema = AdminMenuPower.__table_args__
        schema = schema['schema']
        menu_ids = ','.join('%s' % id for id in menu_ids)
        tbl_name = '{schema}.{table}'.format(schema=schema, table=name)
        return db.session.connection().execute(db.text(
            "SELECT  menu_id, array_to_string(ARRAY(SELECT unnest(array_agg(uuid))),',') AS uuids FROM stock.admin_menu_power where menu_id in ({menu_ids}) GROUP BY menu_id"
                .format(tbl_name=tbl_name, menu_ids=menu_ids))).fetchall()





