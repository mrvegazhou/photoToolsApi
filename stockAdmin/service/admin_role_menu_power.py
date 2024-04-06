# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
from itertools import groupby
from operator import itemgetter
from stock_admin.model.admin_role_menu_power import AdminRoleMenuPower
from stock_admin.model.admin_role import AdminRole
from stock_admin.model.admin_menu_power import AdminMenuPower
from stock_admin.exception.api_exception import RoleNotFoundFailed, DelRoleFailed
from stock_admin.config.constant import Constant


class AdminRoleMenuPowerService:

    @staticmethod
    def get_role_powers_list_by_condition(page_num=1, page_size=Constant.ADMIN_PAGE_SIZE.value, role_title=None, status=None):
        roles, total = AdminRole.get_roles_by_condition(page_num=page_num, page_size=page_size, title=role_title, status=status)
        if not list:
            return [], 0
        else:
            role_ids = []
            for role in roles:
                role_ids.append(role.uuid)
            role_menu_powers = AdminRoleMenuPower.get_role_menu_powers(role_ids)
            role_menu_powers_dict = {}
            for item in role_menu_powers:
                if item.role_id in role_menu_powers_dict:
                    role_menu_powers_dict[item.role_id].append({"menu_id": item.menu_id, "power_id": item.power_id})
                else:
                    role_menu_powers_dict.setdefault(item.role_id, [{"menu_id": item.menu_id, "power_id": item.power_id}])
            res = []
            for role in roles:
                role = dict(role)
                role['menu_powers'] = []

                if role['uuid'] in role_menu_powers_dict:
                    role_menu_powers_by_role = role_menu_powers_dict[role['uuid']]
                    lstg = groupby(role_menu_powers_by_role, itemgetter('menu_id'))
                    for key, group in lstg:
                        powers = []
                        for g in group:
                            powers.append(g['power_id'])
                        role['menu_powers'].append({'menu_id': key, 'powers': powers})
                res.append(role)

            return res, total



    @staticmethod
    def get_role_powers_list(role_ids):
        roles = AdminRole.get_roles(role_ids)
        if not roles:
            raise RoleNotFoundFailed()
        role_ids = []
        for role in roles:
            role_ids.append(role.uuid)
        role_menu_powers = AdminRoleMenuPower.get_role_menu_powers(role_ids)
        role_menu_powers_dict = {}
        for item in role_menu_powers:
            if item.role_id in role_menu_powers_dict:
                role_menu_powers_dict[item.role_id].append({"menu_id": item.menu_id, "power_id": item.power_id})
            else:
                role_menu_powers_dict.setdefault(item.role_id, [{"menu_id": item.menu_id, "power_id": item.power_id}])
        res = []
        for role in roles:
            role_menu_powers_by_role = role_menu_powers_dict[role.uuid]
            role = dict(role)
            role['menu_powers'] = []
            lstg = groupby(role_menu_powers_by_role, itemgetter('menu_id'))
            for key, group in lstg:
                powers = []
                for g in group:
                    powers.append(g['power_id'])
                role['menu_powers'].append({'menu_id': key, 'powers': powers})
            res.append(role)
        return res

    @staticmethod
    def get_roles_menu_powers():
        roles = AdminRole.get_roles()
        role_ids = []
        for item in roles:
            role_ids.append(item.uuid)
        role_menu_powers = AdminRoleMenuPower.get_role_menu_powers(role_ids)
        lstg = groupby(role_menu_powers, itemgetter('role_id', 'menu_id'))
        res = {}
        for key, group in lstg:
            powers = []
            for g in group:
                powers.append(g.power_id)
            if key[0] in res:
                res[key[0]].append({'menu_id': key[1], 'powers': powers})
            else:
                res[key[0]] = [{'menu_id': key[1], 'powers': powers}]
        res_list = []
        for role in roles:
            role = dict(role)
            if role['uuid'] in res:
                role['menu_powers'] = res[role['uuid']]
            else:
                role['menu_powers'] = []
            res_list.append(role)
        return res_list

    @staticmethod
    def del_role_menu_powers(role_id):
        # 角色逻辑删
        del_role_res = AdminRole.del_role(role_id)
        if not del_role_res:
            raise DelRoleFailed()
        # 权限物理删
        del_power_res = AdminRoleMenuPower.del_role_menu_power_by_role(role_id)
        if not del_power_res:
            raise DelRoleFailed()
        return True

    @staticmethod
    def set_powers_by_role_id(role_id, menus, powers):
        # 判断powers属于哪个menu
        res = AdminMenuPower.get_menu_powers_by_group_menu_id(menus)
        res_menu_power_dict = {}
        for item in res:
            tmp_power_ids = item[1].split(',')
            res_menu_power_dict[item[0]] = list(set(tmp_power_ids) & set(powers))

        return AdminRoleMenuPower.transanction_save_role_menu_powers(role_id, res_menu_power_dict)

    @staticmethod
    def set_powers_by_role_ids(roles_menus_powers_list):
        all_menus = []
        for item in roles_menus_powers_list:
            all_menus.extend(item['menus'])
        # 判断powers属于哪个menu
        res = AdminMenuPower.get_menu_powers_by_group_menu_id(list(set(all_menus)))

        new_menu_powers_dict = {}
        for item in res:
            tmp_power_ids = item[1].split(',')
            new_menu_powers_dict[item[0]] = [int(x) for x in tmp_power_ids]

        roles_menus_powers_dict = {}
        for item in roles_menus_powers_list:
            if item['menus']:
                res_menu_power_dict = {}
                for menu in item['menus']:
                    res_menu_power_dict[menu] = list(set(new_menu_powers_dict[menu]) & set(item['powers']))
                roles_menus_powers_dict[item['role_id']] = res_menu_power_dict
            else:
                roles_menus_powers_dict[item['role_id']] = {}

        return AdminRoleMenuPower.transanction_save_roles_menus_powers(roles_menus_powers_dict)





if __name__ == "__main__":

    res = AdminRoleMenuPowerService.get_roles_menu_powers()
    print(res)
    # lstg = groupby(res, itemgetter('menu_id'))
    # for key, group in lstg:
    #     # print(key, list(group))
    #     for g in group:  # group是一个迭代器，包含了所有的分组列表
    #         print(key, g)