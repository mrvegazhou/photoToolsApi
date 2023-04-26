# -*- coding: utf-8 -*-

from photo_tools_admin.__init__ import send, reqparse
from . import admin
from photo_tools_admin.service.admin_menu import AdminMenuService
from photo_tools_admin.decorator.oath2_tool import need_login


@admin.route('/menusByIds', methods=['POST'])
def get_menu_by_ids():
    parser = reqparse.RequestParser()
    parser.add_argument('menu_ids', help='角色标识不能为空', type=int, action='append')
    args = parser.parse_args(http_error_code=50009)
    menu_ids = args['menu_ids']
    if menu_ids:
        list = AdminMenuService.get_menu_by_ids(menu_ids)
    else:
        list = []
    return send(200, data=list)


@admin.route('/allMenus', methods=['POST'])
@need_login
def get_all_menus():
    return send(200, data=AdminMenuService.get_all_menus())


@admin.route('/addMenu', methods=['POST'])
@need_login
def add_menu():
    parser = reqparse.RequestParser()
    parser.add_argument('url', help='菜单链接不能为空', type=str)
    parser.add_argument('title', help='菜单标题不能为空', type=str, required=True)
    parser.add_argument('sorts', help='菜单标题不能为空', type=int, required=True)
    parser.add_argument('icon', help='菜单icon不能为空', type=str)
    parser.add_argument('description', help='菜单描述不能为空', type=str)
    parser.add_argument('status', help='菜单状态不能为空', type=str, required=True)
    parser.add_argument('parent', help='父菜单不能为空', type=int, default=0)
    args = parser.parse_args(http_error_code=50009)
    res = AdminMenuService.add_menu(parent=args['parent'],
                                    title=args['title'],
                                    url=args['url'],
                                    icon=args['icon'],
                                    description=args['description'],
                                    status=args['status'],
                                    sorts=args['sorts'])
    if not res:
        return send(200, data=res)
    return send(200, data=res)


@admin.route('/updateMenu', methods=['POST'])
def update_menu():
    parser = reqparse.RequestParser()
    parser.add_argument('uuid', help='菜单编码不能为空', type=int, required=True)
    parser.add_argument('url', help='菜单链接不能为空', type=str, required=True)
    parser.add_argument('title', help='菜单标题不能为空', type=str, required=True)
    parser.add_argument('sorts', help='菜单标题不能为空', type=int, required=True)
    parser.add_argument('icon', help='菜单icon不能为空', type=str, required=True)
    parser.add_argument('description', help='菜单描述不能为空', type=str, required=True)
    parser.add_argument('status', help='菜单状态不能为空', type=str, required=True)
    parser.add_argument('parent', help='父菜单不能为空', type=int, required=True)
    args = parser.parse_args(http_error_code=50009)
    res = AdminMenuService.update_menu(args)
    return send(200, data=res)


@admin.route('/delMenu', methods=['POST'])
def del_menu():
    parser = reqparse.RequestParser()
    parser.add_argument('menu_id', help='菜单编码不能为空', type=int, required=True)
    args = parser.parse_args(http_error_code=50009)
    res = AdminMenuService.del_menu(args['menu_id'])
    return send(200, data=res)

