# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
import typing
from stock_admin.model.admin_menu import AdminMenu
from stock_admin.model.admin_menu_power import AdminMenuPower
from core.exception.api_exception import ValError, APIException


class AdminMenuPowerService:

    @staticmethod
    def get_menu_powers():
        menus = AdminMenu.get_all_menus()
        ids = []
        menus_dict = {}
        for item in menus:
            ids.append(item.uuid)
            item = dict(item)
            item['powers'] = []
            menus_dict[item['uuid']] = item

        list_powers = AdminMenuPower.get_powers_by_menu_ids(ids)
        for item in list_powers:
            menus_dict[item.menu_id]['powers'].append(item)
        return list(menus_dict.values())

    @staticmethod
    def get_menu_powers_by_power_ids(power_ids):
        if not isinstance(power_ids, list):
            raise ValError()
        return AdminMenuPower.get_powers_by_power_ids(power_ids, order=False)

    @staticmethod
    def get_menu_powers_by_menu_id(menu_ids: typing.List):
        return AdminMenuPower.get_powers_by_menu_ids(ids=menu_ids, order=False)

    @staticmethod
    def add_menu_power(menu_id, title, code, description, sorts, status):
        if not menu_id:
            raise APIException(msg='菜单标识不能为空', code=50009)
        if not title:
            raise APIException(msg='标题不能为空', code=50009)
        if not code:
            raise APIException(msg='code不能为空', code=50009)
        return AdminMenuPower.add_menu_power(menu_id, title, code, description, sorts, status)

    @staticmethod
    def update_menu_power(kwargs):
        if not kwargs['uuid']:
            raise APIException(msg='权限标识不能为空', code=50009)
        uuid = kwargs['uuid']
        del kwargs['uuid']
        return AdminMenuPower.update_menu_power(uuid, **kwargs)


    @staticmethod
    def del_menu_power(uuid):
        if not uuid:
            raise APIException(msg='权限标识不能为空', code=50009)
        return AdminMenuPower.del_menu_power(uuid)




if __name__ == "__main__":
    res = AdminMenuPowerService.get_menu_powers()
    print(res)