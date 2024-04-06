# -*- coding: utf-8 -*-
from stock_admin.__init__ import send, reqparse
from stock_admin.service.admin_menu_power import AdminMenuPowerService
from . import admin


@admin.route('/menuPowerByMenuIds', methods=['GET'])
def get_menu_powers_by_menu():
    parser = reqparse.RequestParser()
    parser.add_argument('menu_ids', help='菜单标识不能为空', action='append', required=True)
    args = parser.parse_args(http_error_code=50009)
    menu_ids = args['menu_ids']
    res = AdminMenuPowerService.get_menu_by_ids([menu_ids])
    return send(200, data=res)


@admin.route('/menuPowers', methods=['POST'])
def get_menu_powers():
    res = AdminMenuPowerService.get_menu_powers()
    return send(200, data=res)


@admin.route('/menuPowersByPowerIds', methods=['POST'])
def get_menu_powers_by_power_ids():
    parser = reqparse.RequestParser()
    parser.add_argument('power_ids', help='权限动作标识不能为空', type=int, action='append')
    args = parser.parse_args(http_error_code=50009)
    power_ids = args['power_ids']
    if power_ids:
        res = AdminMenuPowerService.get_menu_powers_by_power_ids(power_ids)
    else:
        res = []
    return send(200, data=res)


# 根据menu_id获取权限列表
@admin.route('/menuPowersByMenuId', methods=['POST'])
def get_menu_powers_by_menu_id():
    parser = reqparse.RequestParser()
    parser.add_argument('menu_id', help='菜单标识不能为空', type=int, required=True)
    args = parser.parse_args(http_error_code=50009)
    res = AdminMenuPowerService.get_menu_powers_by_menu_id([args['menu_id']])
    if res==None:
        res = []
    return send(200, data=res)


@admin.route('/addPower', methods=['POST'])
def add_menu_power():
    parser = reqparse.RequestParser()
    # menu_id, title, code, description, sorts, status
    parser.add_argument('menu_id', help='菜单标识不能为空', type=int, required=True)
    parser.add_argument('title', help='标题不能为空', type=str, required=True)
    parser.add_argument('code', help='code不能为空', type=str, required=True)
    parser.add_argument('description', type=str)
    parser.add_argument('sorts', type=int)
    parser.add_argument('status', type=int)
    args = parser.parse_args(http_error_code=50009)
    menu_id = args['menu_id']
    title = args['title']
    code = args['code']
    description = args['description']
    sorts = args['sorts']
    status = args['status']
    res = AdminMenuPowerService.add_menu_power(menu_id, title, code, description, sorts, status)
    return send(200, data=res)


@admin.route('/updatePower', methods=['POST'])
def update_menu_power():
    parser = reqparse.RequestParser()
    parser.add_argument('uuid', help='权限标识不能为空', type=int)
    parser.add_argument('menu_id', help='菜单标识不能为空', type=int)
    parser.add_argument('title', help='标题不能为空', type=str)
    parser.add_argument('code', help='code不能为空', type=str)
    parser.add_argument('description', type=str)
    parser.add_argument('sorts', type=int)
    parser.add_argument('status', type=int)
    args = parser.parse_args(http_error_code=50009)
    res = AdminMenuPowerService.update_menu_power(args)
    return send(200, data=res)


@admin.route('/delPower', methods=['POST'])
def del_menu_power():
    parser = reqparse.RequestParser()
    parser.add_argument('uuid', help='权限标识不能为空', type=int)
    args = parser.parse_args(http_error_code=50009)
    res = AdminMenuPowerService.del_menu_power(args['uuid'])
    return send(200, data=res)