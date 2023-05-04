# -*- coding: utf-8 -*-

import functools
from photo_tools_app import g, request
import jwt
from photo_tools_app.exception.api_exception import JWTExpiredSignatureError, JWTDecodeError, JWTInvalidTokenError
from photo_tools_app import send
from photo_tools_app.utils.jwt_util import JwtUtil
from photo_tools_app.service.app_user import AppUserService

def jwt_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            if g.session_key == -1:
                raise JWTExpiredSignatureError()
            elif g.session_key == -2:
                raise JWTDecodeError()
            elif g.session_key == -3:
                raise JWTInvalidTokenError()
            elif g.session_key == None:
                raise BaseException()
        except JWTExpiredSignatureError as e:
            return send(e.res_code)
        except JWTDecodeError as e:
            return send(e.res_code)
        except JWTInvalidTokenError as e:
            return send(e.res_code)
        except BaseException as e:
            return send(20006)
        return f(*args, **kwargs)
    return wrapper


def jwt_wx_authentication():
    """
    1.获取请求头Authorization中的token
    2.判断是否以 Bearer开头
    3.使用jwt模块进行校验
    4.判断校验结果,成功就提取token中的载荷信息,赋值给g对象保存
    """
    g.session_key = None
    auth = request.headers.get('Authorization')
    if auth and auth.startswith('Bearer '):
        """提取token 0-6 被Bearer和空格占用 取下标7以后的所有字符"""
        token = auth[7:]
        try:
            """判断token的校验结果"""
            # payload = jwt.decode(token, Constant.JWT_SALT.value, algorithms=['HS256'])
            payload = JwtUtil.decode_token(token)
            """获取载荷中的信息赋值给g对象"""
            if isinstance(payload, dict) and 'data' in payload.keys():
                data = payload['data']
                session_key = data['session_key']
                openid = data['openid']
                g.session_key = session_key
                g.openid = openid
                user_info = AppUserService.getAppUserInfo(openid)
                if user_info:
                    g.uid = user_info.uuid
                else:
                    g.uid = 0
            else:
                g.session_key = -3
        except jwt.exceptions.ExpiredSignatureError:  # 'token已失效'
            g.session_key = -1
        except jwt.DecodeError:  # 'token认证失败'
            g.session_key = -2
        except jwt.InvalidTokenError:  # '非法的token'
            g.session_key = -3
        except jwt.exceptions.DecodeError:
            g.session_key = -2