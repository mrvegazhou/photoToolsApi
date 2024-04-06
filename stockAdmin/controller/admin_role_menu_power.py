# -*- coding: utf-8 -*-
from stock_admin.__init__ import send, reqparse, request
from . import admin
from stock_admin.service.admin_role_menu_power import AdminRoleMenuPowerService


# 通过角色id获取菜单和权限列表信息
@admin.route('/roleMenuPowers', methods=['POST'])
def get_role_menu_power_list():
    parser = reqparse.RequestParser()
    parser.add_argument('role_ids', help='角色标识不能为空', action='append')
    args = parser.parse_args(http_error_code=50009)
    role_ids = args['role_ids']
    if role_ids and len(role_ids):
        list = AdminRoleMenuPowerService.get_role_powers_list(role_ids)
    else:
        list = []
    return send(200, data=list)


# 获取所有角色的菜单和权限列表信息
@admin.route('/allRolesMenuPowers', methods=['POST'])
def get_all_roles_menu_power_list():
    list = AdminRoleMenuPowerService.get_roles_menu_powers()
    return send(200, data=list)


# 通过角色ID给指定角色设置菜单及权限
@admin.route('/setPowersByRoleId', methods=['POST'])
def set_powers_by_role_id():
    parser = reqparse.RequestParser()
    parser.add_argument('role_id', help='角色标识不能为空', required=True)
    parser.add_argument('menus', action='append')
    parser.add_argument('powers', action='append')
    args = parser.parse_args(http_error_code=50009)
    res = AdminRoleMenuPowerService.set_powers_by_role_id(args['role_id'], args['menus'], args['powers'])
    return send(200, data=res)


@admin.route('/setPowersByRoleIds', methods=['POST'])
def set_powers_by_role_ids():
    datas = request.get_json()
    res = AdminRoleMenuPowerService.set_powers_by_role_ids(datas)
    return send(200, data=res)



