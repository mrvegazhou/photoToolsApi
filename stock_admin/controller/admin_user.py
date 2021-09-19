# -*- coding: utf-8 -*-
from stock_admin.__init__ import send, reqparse, utils
from . import admin
from stock_admin.service.admin_user import AdminUserService


def check_password(password):
    res = utils['common'].is_password(password)
    if not res:
        raise ValueError("密码需要满足:1.全英文;2.最少一个大写字母;3.最少一个英文特殊字符;4.最少一个数字;5.范围在6-18位;")
    return password


@admin.route('/login', methods=['POST'])
def login():
    parser = reqparse.RequestParser()
    parser.add_argument('username', help='用户名不能为空', type=str, required=True)
    parser.add_argument('password', help='密码不能为空', type=str, required=True)
    args = parser.parse_args(http_error_code=50003)
    username = args['username']
    password = args['password']
    user_info = AdminUserService.on_login(username, password)
    return send(200, data=user_info)


@admin.route('/addAdminUser', methods=['POST'])
def register():
    parser = reqparse.RequestParser()
    parser.add_argument('username', help='用户名不能为空addAdminUser', type=str, required=True)
    parser.add_argument('password', help='密码不能为空', type=str, required=True)
    parser.add_argument('password', type=check_password)
    parser.add_argument('phone', help='电话不能为空', type=str, required=True)
    parser.add_argument('email', help='邮箱不能为空', type=str, required=True)
    parser.add_argument('description', help='描述不能为空', type=str, required=True)
    args = parser.parse_args(http_error_code=50003)
    res = AdminUserService.register(args['username'], args['password'], args['phone'], args['email'], args['description'])
    return send(200, data=res)


@admin.route('/logout', methods=['POST'])
def logout():
    parser = reqparse.RequestParser()
    parser.add_argument('uuid', help='用户标识为空', type=int, required=True)
    args = parser.parse_args(http_error_code=50003)
    res = AdminUserService.logout(args['uuid'])
    if not res:
        return send(30008, data=res)
    return send(200, data=res)


@admin.route('/userInfo', methods=['POST'])
def get_admin_user_info():
    parser = reqparse.RequestParser()
    parser.add_argument('uuid', help='用户标识为空', type=int, required=True)
    args = parser.parse_args(http_error_code=50003)
    user_info = AdminUserService.get_user_info(args['uuid'])
    return send(200, data=user_info)


@admin.route('/userList', methods=['POST'])
def get_admin_user_list():
    parser = reqparse.RequestParser()
    parser.add_argument('page_num', help='当前页错误', type=int)
    parser.add_argument('page_size', help='每页显示总数错误', type=int)
    parser.add_argument('status', help='用户状态参数错误', type=int)
    parser.add_argument('username', help='用户名错误', type=str, required=False)
    args = parser.parse_args(http_error_code=50003)
    list, total = AdminUserService.get_admin_user_list(args['page_num'], args['page_size'], args['username'], args['status'])
    return send(200, data={"list":list, "total":total})


@admin.route('/delAdminUser', methods=['POST'])
def del_admin_user():
    parser = reqparse.RequestParser()
    parser.add_argument('uuid', help='用户标识错误', type=int)
    args = parser.parse_args(http_error_code=50003)
    res = AdminUserService.del_user(args['uuid'])
    if res:
        return send(200, data=res)
    else:
        return send(60005, data=False)


@admin.route('/updateAdminUser', methods=['POST'])
def update_admin_user():
    parser = reqparse.RequestParser()
    parser.add_argument('uuid', help='用户标识错误', type=int)
    parser.add_argument('description', help='用户描述错误', type=str)
    parser.add_argument('email', help='用户邮箱错误', type=str)
    parser.add_argument('password', help='用户密码错误', type=str)
    parser.add_argument('phone', help='用户电话错误', type=str)
    parser.add_argument('status', help='用户状态错误', type=int)
    parser.add_argument('username', help='用户名错误', type=str)
    kwargs = parser.parse_args(http_error_code=50003)
    print(kwargs)
    res = AdminUserService.update_user(kwargs)
    return send(200, data=res)
