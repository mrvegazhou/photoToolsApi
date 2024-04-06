# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
from datetime import datetime, timezone
from stock_admin.model.base import Base
from stock_admin.__init__ import db, func


class AdminMenu(Base):

    __tablename__ = 'admin_menu'

    uuid = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    parent = db.Column(db.Integer, unique=True)
    title = db.Column(db.String(255), nullable=False, comment="菜单名称")
    icon = db.Column(db.String(255), nullable=False, comment="菜单图标")
    url = db.Column(db.String(255), nullable=False, comment="菜单url")
    description = db.Column(db.String(255), nullable=False, comment="菜单描述")
    sorts = db.Column(db.Integer, nullable=False, default=0, server_default='0', comment="菜单排序")
    status = db.Column(db.SMALLINT, nullable=False, default=1, server_default='1', comment="1 正常 0 禁止")
    create_time = db.Column(db.TIMESTAMP, comment="创建时间", server_default=func.now())
    update_time = db.Column(db.TIMESTAMP, comment="修改时间")
    delete_time = db.Column(db.TIMESTAMP, comment="删除时间")

    def get_keys(self):
        return {
            "uuid": self.uuid,
            "parent": self.parent,
            "title": self.title,
            "icon": self.icon,
            "url": self.url,
            "sorts": self.sorts,
            "description": self.description,
            "status": self.status,
            "create_time": self.create_time
        }

    @staticmethod
    def get_menu_by_id(menu_id):
        return AdminMenu.query.filter(AdminMenu.uuid==menu_id).first()

    @staticmethod
    def get_menu_by_ids(menu_ids):
        return AdminMenu.query.filter(AdminMenu.uuid.in_(menu_ids)).order_by(AdminMenu.sorts.asc()).all()

    @staticmethod
    def get_all_menus():
        return AdminMenu.query.filter(AdminMenu.delete_time==None).order_by(AdminMenu.sorts.asc()).all()

    @staticmethod
    def add_new_menu(parent=0, title='', icon='', url='', sorts=0, description='', status=1):
        tmp = AdminMenu()
        tmp.parent = parent
        tmp.title = title
        tmp.icon = icon
        tmp.url = url
        tmp.sorts = sorts
        tmp.description = description
        tmp.status = status

        db.session.add(tmp)
        db.session.commit()
        uuid = tmp.uuid
        return uuid

    @staticmethod
    def update_menu(uuid, **args):
        info = {'update_time': datetime.now(tz=timezone.utc)}
        for key, val in args.items():
            if hasattr(AdminMenu, key) and key != 'uuid' and key != 'create_time':
                info[key] = val
        num_rows_updated = AdminMenu.query.filter_by(uuid=uuid).update(info)
        db.session.commit()
        return num_rows_updated

    @staticmethod
    def delete_menu(uuid):
        info = {'delete_time': datetime.now(tz=timezone.utc)}
        num_rows_updated = AdminMenu.query.filter_by(uuid=uuid).update(info)
        db.session.commit()
        return num_rows_updated

    @staticmethod
    def true_delete_menu(uuid):
        deleted_objects = AdminMenu.__table__.delete().where(AdminMenu.uuid == uuid)
        result = db.session.execute(deleted_objects)
        db.session.commit()
        return result.rowcount



if __name__ == "__main__":
    res = AdminMenu.get_all_menus()
    print(res)



