# -*- coding: utf-8 -*-
from stock_admin.__init__ import send, reqparse, utils
from . import admin
from stock_admin.service.admin_user_role import AdminUserRoleService


@admin.route('/assignRole', methods=['POST'])
def assign_roles():
    parser = reqparse.RequestParser()
    parser.add_argument('admin_user_id', help='用户标识不能为空', type=int, required=True)
    parser.add_argument('role_ids', help='角色标识不能为空', action='append')
    args = parser.parse_args(http_error_code=50003)
    res = AdminUserRoleService.assgin_roles(args['admin_user_id'], args['role_ids'])
    return send(200, data=res)