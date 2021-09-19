# -*- coding: utf-8 -*-

from stock_admin.__init__ import send, reqparse
from . import admin
from stock_admin.service.admin_role import AdminRoleService
from stock_admin.service.admin_role_menu_power import AdminRoleMenuPowerService


@admin.route('/sysRoles', methods=['POST'])
def get_sys_role_list():
    parser = reqparse.RequestParser()
    parser.add_argument('page_size', type=int)
    parser.add_argument('page_num', help='页码为空', type=int)
    parser.add_argument('title', help='角色名称出错', type=str)
    parser.add_argument('status', help='角色状态出错', type=int)
    args = parser.parse_args(http_error_code=50009)
    res, total = AdminRoleMenuPowerService.get_role_powers_list_by_condition(page_size=args['page_size'], page_num=args['page_num'], role_title=args['title'], status=args['status'])
    return send(200, data={'list': res, 'total': total})


@admin.route('/addRole', methods=['POST'])
def add_role():
    parser = reqparse.RequestParser()
    parser.add_argument('title', help='角色名称不能为空', type=str, required=True)
    parser.add_argument('description', help='角色描述不能为空', type=str, required=True)
    parser.add_argument('sorts', help='角色排序不能为空', type=int, required=True)
    parser.add_argument('status', help='角色状态不能为空', type=int, required=True)
    args = parser.parse_args(http_error_code=50003)
    res = AdminRoleService.add_role(args['title'], args['description'], args['status'], args['sorts'])
    return send(200, data=res)


@admin.route('/updateRole', methods=['POST'])
def update_role():
    parser = reqparse.RequestParser()
    parser.add_argument('uuid', help='角色标识不能为空', type=int, required=True)
    parser.add_argument('title', help='角色名称不能为空', type=str)
    parser.add_argument('description', help='角色描述不能为空', type=str)
    parser.add_argument('sorts', help='角色排序不能为空', type=int)
    parser.add_argument('status', help='角色状态不能为空', type=int)
    args = parser.parse_args(http_error_code=50003)
    res = AdminRoleService.update_role_info(args)
    return send(200, data=res)


@admin.route('/delRole', methods=['POST'])
def del_role():
    parser = reqparse.RequestParser()
    parser.add_argument('role_id', help='角色标识不能为空', type=int, required=True)
    args = parser.parse_args(http_error_code=50003)
    res = AdminRoleService.del_role_info(args['role_id'])
    return send(200, data=res)