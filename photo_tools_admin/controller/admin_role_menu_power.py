# -*- coding: utf-8 -*-
from photo_tools_admin.__init__ import send, reqparse, request, CODE
from . import admin
from photo_tools_admin.service.admin_role_menu_power import AdminRoleMenuPowerService


# 获取所有角色的菜单和权限列表信息
@admin.route('/allRolesMenuPowers', methods=['POST'])
def get_all_roles_menu_power_list():
    return send(200, data=AdminRoleMenuPowerService.get_roles_menu_powers())


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
    parser = reqparse.RequestParser()
    parser.add_argument('role_ids', help="角色ids", action='append', location='json', required=True)
    parser.add_argument('menu_id', type=int, help="菜单", location='json', required=True)
    parser.add_argument('power_id', type=int, help="权限", location='json', required=True)
    args = parser.parse_args(http_error_code=50009)
    role_ids = args['role_ids']
    menu_id = args['menu_id']
    power_id = args['power_id']
    res = AdminRoleMenuPowerService.set_powers_by_role_ids(role_ids, menu_id, power_id)
    if res:
        return send(200, data=res)
    else:
        return send(60007, msg=CODE[60007], data=None)


# 单独给菜单赋予角色权限
@admin.route('/setMenuRoles', methods=['POST'])
def set_menu_roles():
    parser = reqparse.RequestParser()
    parser.add_argument('menu_id', help='菜单标识不能为空', type=int, required=True)
    parser.add_argument('role_ids', help='角色标识不能为空', action='append')
    args = parser.parse_args(http_error_code=50009)
    role_ids = args['role_ids']
    menu_id = args['menu_id']
    add_count, delete_count, no_delete_role_infos = AdminRoleMenuPowerService.set_menu_roles(menu_id, role_ids)
    res = "成功为菜单添加{}角色;".format(add_count)
    if delete_count>0:
        res = res + "删除取消的角色{};".format(delete_count)
    if len(no_delete_role_infos)>0:
        res = res + "因角色{}拥有此菜单下的操作权限,无法取消".format("、".join(no_delete_role_infos))
    return send(200, data=res)



