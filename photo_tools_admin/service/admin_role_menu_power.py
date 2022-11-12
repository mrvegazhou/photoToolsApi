# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/photo-tools-api")
from itertools import groupby
from operator import itemgetter
from photo_tools_admin.model.admin_role_menu_power import AdminRoleMenuPower
from photo_tools_admin.model.admin_role import AdminRole
from photo_tools_admin.model.admin_menu_power import AdminMenuPower
from photo_tools_admin.exception.api_exception import RoleNotFoundFailed, DelRoleFailed
from photo_tools_admin.config.constant import Constant
from core.exception.api_exception import ValError, APIException


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

    '''
        参数：
        [{
        'role_id': 1,
        'menus': [14, 6, 2, 3, 4, 5, 15],
        'powers': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 24, 25, 22, 23, 26, 27]
        }] 
        批量设置角色权限
    '''
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
                    if new_menu_powers_dict.get(menu) is not None:
                        res_menu_power_dict[menu] = list(set(new_menu_powers_dict[menu]) & set(item['powers']))
                    else:
                        res_menu_power_dict[menu] = [0]
                roles_menus_powers_dict[item['role_id']] = res_menu_power_dict
            else:
                roles_menus_powers_dict[item['role_id']] = {}

        return AdminRoleMenuPower.transanction_save_roles_menus_powers(roles_menus_powers_dict)


    @staticmethod
    def set_menu_roles(menu_id, role_ids):
        # 查看菜单下拥有的额角色有哪些
        if not menu_id:
            raise APIException(msg='菜单标识不能为空', code=50009)
        role_exist_ids = AdminRoleMenuPower.get_roless_by_menuId_groupBy_roleId_menuId(menu_id)
        ids = [i[0] for i in role_exist_ids]
        # 对比出哪些角色没有选择
        diff_roleIds_1 = list(set(ids) - set(role_ids))
        # 无法删除的角色 做提示
        no_delete_role_infos = []
        if len(diff_roleIds_1)>0:
            no_delete_role_infos = AdminRole.get_roles(diff_roleIds_1)
        # 可以删除的角色
        all_role_ids = AdminRoleMenuPower.get_roles_by_menuId_groupBy_roleId(menu_id)
        diff_roleIds_2 = list(set(all_role_ids) - set(ids))
        delete_role_ids = list(filter(lambda id: id not in role_ids, diff_roleIds_2))
        delete_count = 0
        if len(delete_role_ids)>0:
            delete_count = AdminRoleMenuPower.del_power_by_menuId_roleIds(menu_id, delete_role_ids)
        # 需要添加到菜单下的角色
        diff_roleIds_3 = list(set(role_ids) - set(ids))
        add_role_ids = list(filter(lambda id: id not in all_role_ids, diff_roleIds_3))
        add_count = 0
        if add_role_ids:
            params = [{'role_id': i, 'menu_id': menu_id, 'power_id': 0} for i in add_role_ids]
            add_count = AdminRoleMenuPower.batch_add_role_menu_powers(params)
        return add_count, delete_count, [item.title for item in no_delete_role_infos]


if __name__ == "__main__":
    # res = AdminRoleMenuPower.get_roless_by_menuId_groupBy_roleId_menuId(7)
    # print(res)
    print(AdminRoleMenuPowerService.set_menu_roles(999, [6, 5]))
