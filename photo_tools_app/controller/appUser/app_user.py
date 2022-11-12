# -*- coding: utf-8 -*-
from photo_tools_app.__init__ import send, reqparse, Redprint, CODE, utils, app
from photo_tools_app.utils.jwt_required import jwt_required

api = Redprint(name='appUser')

@api.route('/info', methods=["POST"])
@jwt_required
def AppUser():
    parser = reqparse.RequestParser()
    parser.add_argument('uuid', type=int, help="用户标识错误", location='form')
    parser.add_argument('username', type=str, help="用户名错误", location='form')
    parser.add_argument('email', type=str, help="邮箱错误", location='form')
    parser.add_argument('phone', type=str, help="电话错误", location='form')
    parser.add_argument('status', type=str, help="状态错误", location='form')
    parser.add_argument('status', type=str, help="状态错误", location='form')
    entry = parser.parse_args(http_error_code=50003)

    uuid = entry.get('uuid')
    username = entry.get('username')
