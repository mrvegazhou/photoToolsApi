# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/photo-tools-api")
from photo_tools_admin.model.base import Base
from photo_tools_admin.__init__ import db, utils, func
from sqlalchemy import select, and_

class AdminRoleMenuPower(Base):

    __tablename__ = 'admin_role_menu_power'

    uuid = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    role_id = db.Column(db.Integer, nullable=False, unique=True, comment="角色标识")
    menu_id = db.Column(db.Integer, nullable=False, unique=True, comment="菜单标识")
    power_id = db.Column(db.Integer, nullable=False, unique=True, comment="操作标识")
    create_time = db.Column(db.TIMESTAMP, nullable=False, comment="创建时间")

    def get_keys(self):
        return {
            "uuid": self.uuid,
            "role_id": self.role_id,
            "menu_id": self.menu_id,
            "power_id": self.power_id
        }

    @staticmethod
    def add_role_menu_power(role_id, menu_id, power_id):
        tmp = AdminRoleMenuPower()
        tmp.role_id = role_id
        tmp.menu_id = menu_id
        tmp.power_id = power_id

        db.session.add(tmp)
        uuid = tmp.uuid
        db.session.commit()
        return uuid

    @staticmethod
    def del_role_menu_power(uuid):
        deleted_objects = AdminRoleMenuPower.__table__.delete().where(AdminRoleMenuPower.uuid == uuid)
        result = db.session.execute(deleted_objects)
        db.session.commit()
        return result.rowcount

    @staticmethod
    def del_role_menu_power_by_role(role_id):
        deleted_objects = AdminRoleMenuPower.__table__.delete().where(AdminRoleMenuPower.role_id == role_id)
        result = db.session.execute(deleted_objects)
        db.session.commit()
        return result.rowcount

    @staticmethod
    def del_role_menu_power_by_power_id(power_id):
        deleted_objects = AdminRoleMenuPower.__table__.delete().where(AdminRoleMenuPower.power_id == power_id)
        result = db.session.execute(deleted_objects)
        db.session.commit()
        return result.rowcount

    # 通过menu_id和role_ids删除权限
    @staticmethod
    def del_power_by_menuId_roleIds(menu_id, role_ids):
        deleted_objects = AdminRoleMenuPower.__table__.delete().where(and_(AdminRoleMenuPower.menu_id == menu_id, AdminRoleMenuPower.role_id.in_(role_ids)))
        result = db.session.execute(deleted_objects)
        db.session.commit()
        return result.rowcount

    @staticmethod
    def batch_add_role_menu_powers(params):
        '''
        :param params: {'role_id': 1, 'menu_id': 1, 'power_id': 1}
        :return:
        '''
        name = AdminRoleMenuPower.__tablename__
        schema = AdminRoleMenuPower.__table_args__
        schema = schema['schema']
        tbl_name = '{schema}.{table}'.format(schema=schema, table=name)
        sql_insert = []
        sql_insert_dict = {}
        sql_insert_list = []
        i = 0
        for item in params:
            keys = item.keys()
            if ('role_id' not in keys) or ('menu_id' not in keys) or ('power_id' not in keys):
                continue
            if (not utils['common'].is_num(item['role_id'])) or (not utils['common'].is_num(item['menu_id'])) or (not utils['common'].is_num(item['power_id'])):
                continue
            i = i + 1
            role_key = 'role_id' + str(i)
            menu_key = 'menu_id' + str(i)
            power_key = 'power_id' + str(i)
            sql_insert.append("(:{role_id}, :{menu_id}, :{power_id})".format(role_id=role_key, menu_id=menu_key, power_id=power_key))
            sql_insert_dict[role_key] = item['role_id']
            sql_insert_dict[menu_key] = item['menu_id']
            sql_insert_dict[power_key] = item['power_id']
            sql_insert_list.append(sql_insert_dict)

        sql_insert = ','.join(sql_insert)
        result = db.session.connection().execute(db.text(
            'insert into {tbl_name} (role_id, menu_id, power_id) values {sql_str} ON conflict(role_id, menu_id, power_id) DO UPDATE SET create_time=NOW()'
                .format(tbl_name=tbl_name, sql_str=sql_insert)), sql_insert_list)
        db.session.commit()
        return result.rowcount

    @staticmethod
    def transanction_save_role_menu_powers(role_id, menu_power_ids):
        flag = True
        try:
            with db.session.begin(subtransactions=True):
                 for menu_id, power_ids in menu_power_ids.items():
                    deleted_objects = AdminRoleMenuPower.__table__.delete().where(AdminRoleMenuPower.role_id == role_id).where(AdminRoleMenuPower.menu_id == menu_id)
                    res = db.session.execute(deleted_objects)
                    items = []
                    for power_id in power_ids:
                        items.append({'role_id': role_id, 'menu_id': menu_id, 'power_id': power_id})
                    if not items and res.rowcount==0:
                        db.session.rollback()
                        flag = False
                    db.session.execute(
                        AdminRoleMenuPower.__table__.insert(),
                        items
                    )
        except Exception as e:
            db.session.rollback()
        db.session.commit()
        return flag

    @staticmethod
    def transanction_save_roles_menus_powers(roles_menus_powers_dict):
        flag = True
        try:
            # db.session.begin_nested()
            for role_id, menu_power_ids in roles_menus_powers_dict.items():
                if not menu_power_ids:
                    deleted_by_role_id = AdminRoleMenuPower.__table__.delete().where(AdminRoleMenuPower.role_id == role_id)
                    db.session.execute(deleted_by_role_id)
                    db.session.commit()
                for menu_id, power_ids in menu_power_ids.items():
                    db.session.begin_nested()
                    deleted_objects = AdminRoleMenuPower.__table__.delete().where(AdminRoleMenuPower.role_id == role_id).where(AdminRoleMenuPower.menu_id == menu_id)
                    res = db.session.execute(deleted_objects)
                    db.session.commit()
                    items = []
                    for power_id in power_ids:
                        items.append({'role_id': role_id, 'menu_id': menu_id, 'power_id': power_id})
                        if not items and res.rowcount == 0:
                            # db.session.rollback()
                            flag = False
                        else:
                            db.session.execute(
                                AdminRoleMenuPower.__table__.insert(),
                                items
                            )
                            db.session.commit()
            # db.session.commit()
        except Exception as e:
            print(e, "---e---")
            db.session.rollback()
        # db.session.commit()
        db.session.close()
        return flag

    @staticmethod
    def get_role_menu_powers(role_ids):
        if isinstance(role_ids, list):
            return AdminRoleMenuPower.query.filter(AdminRoleMenuPower.role_id.in_(role_ids)).all()
        else:
            return AdminRoleMenuPower.query.filter(AdminRoleMenuPower.role_id==role_ids).all()

    @staticmethod
    def get_role_menu_power_by_menu(menu_ids):
        if isinstance(menu_ids, list):
            return AdminRoleMenuPower.query.filter(AdminRoleMenuPower.menu_id.in_(menu_ids)).all()
        else:
            return AdminRoleMenuPower.query.filter(AdminRoleMenuPower.menu_id==menu_ids).all()

    @staticmethod
    def get_roles_by_menuId_groupBy_roleId(menu_id):
        sql = select(AdminRoleMenuPower.role_id).where(AdminRoleMenuPower.menu_id==menu_id).group_by(AdminRoleMenuPower.role_id)
        datas = db.session.connection().execute(sql).fetchall()
        if datas:
            return [i[0] for i in datas]
        else:
            return []

    @staticmethod
    def get_roless_by_menuId_groupBy_roleId_menuId(menu_id):
        sql = select(AdminRoleMenuPower.role_id, AdminRoleMenuPower.menu_id, func.count(AdminRoleMenuPower.power_id).label("count"))\
            .where(and_(AdminRoleMenuPower.menu_id == menu_id, AdminRoleMenuPower.power_id!=0))\
            .group_by(AdminRoleMenuPower.role_id, AdminRoleMenuPower.menu_id)
        return db.session.connection().execute(sql).fetchall()



if __name__ == "__main__":
    pass