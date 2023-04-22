# -*- coding: utf-8 -*-

from photo_tools_app.__init__ import send, reqparse, Redprint, g, CODE
import requests
from photo_tools_app.config.constant import Constant
from photo_tools_app.utils.jwt_util import JwtUtil
from photo_tools_app.utils.jwt_required import jwt_required, jwt_wx_authentication

api = Redprint(name='auth')

@api.route('/login', methods=["POST"])
def login():
    """
    请求获得用户的openid
    属性	类型	默认值	必填	说明
    appid	string		是	小程序 appId
    secret	string		是	小程序 appSecret
    js_code	string		是	登录时获取的 code
    grant_type	string		是	授权类型，此处只需填写 authorization_code
    :return:
    返回的 JSON 数据包
    属性	类型	说明
    openid	string	用户唯一标识
    session_key	string	会话密钥
    unionid	string	用户在开放平台的唯一标识符，在满足 UnionID 下发条件的情况下会返回，详见 UnionID 机制说明。
    errcode	number	错误码
    errmsg	string	错误信息
    """
    parser = reqparse.RequestParser()
    parser.add_argument('platCode')
    args = parser.parse_args(http_error_code=50003)
    code = args['platCode']
    appid = Constant.APP_ID.value
    secret = Constant.APP_SECRET.value
    url = Constant.WX_LOGIN.value
    url = url.format(appid, secret, code)
    rq = requests.get(url)
    rq_json = rq.json()
    if rq_json.get('errcode') is not None:
        data = {"error": rq_json.get('errmsg')}
        return send(50010, data=data)
    else:
        openid = rq_json.get('openid')
        session_key = rq_json.get('session_key')
        print(openid,session_key,'---session_key----' )
        # jwt生成
        jwt_token = JwtUtil.encode_token({'openid': openid, 'session_key': session_key})
        return send(200, data={'jwt': jwt_token, 'openid': openid})


@api.route('/check', methods=["POST"])
@jwt_required
def checkOpenid():
    parser = reqparse.RequestParser()
    parser.add_argument('openid')
    args = parser.parse_args(http_error_code=50003)
    openid = args['openid']
    # jwt_wx_authentication()
    data = g.session_key
    if openid!=data['openid']:
        data = {"error": CODE[50010]}
        return send(50010, data=data)
    return send(200, data={'openid': openid})





