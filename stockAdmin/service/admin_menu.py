# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
from stock_admin.model.admin_menu import AdminMenu
from stock_admin.model.admin_role_menu_power import AdminRoleMenuPower


class AdminMenuService:

    @staticmethod
    def get_menu_by_ids(menu_ids):
        return AdminMenu.get_menu_by_ids(menu_ids)

    @staticmethod
    def get_all_menus():
        return AdminMenu.get_all_menus()

    @staticmethod
    def add_menu(parent, title, url, icon, description, status, sorts):
        return AdminMenu.add_new_menu(parent=parent, title=title, url=url, icon=icon, description=description, status=status, sorts=sorts)

    @staticmethod
    def update_menu(kwargs):
        uuid = kwargs['uuid']
        del kwargs['uuid']
        return AdminMenu.update_menu(uuid, **kwargs)

    @staticmethod
    def del_menu(uuid):
        res = AdminRoleMenuPower.get_role_menu_power_by_menu(uuid)
        if not res:
            return AdminMenu.true_delete_menu(uuid)
        else:
            return AdminMenu.delete_menu(uuid)

