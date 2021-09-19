# -*- coding: utf-8 -*-
import json
from flask import request
from werkzeug.exceptions import HTTPException
from ..http.response import CODE


class APIException(HTTPException):
    http_code = 200
    msg = 'sorry，internal error'
    data = ''
    res_code = 500

    def __init__(self, msg=None, http_code=None, res_code=None, data=None, **kwargs):
        if http_code:
            self.code = http_code
        if msg:
            self.msg = msg
        if res_code:
            self.res_code = res_code
        if data:
            self.data = data
        self.kwargs = kwargs
        super(APIException, self).__init__(msg, None)

    def get_body(self, environ=None):
        body = dict(
            code=self.res_code,
            msg=self.msg,
            request=request.method + ' ' + self.get_url_no_parm(),
            data=self.data
        )
        # sort_keys 取消排序规则，ensure_ascii 中文显示
        text = json.dumps(body, sort_keys=False, ensure_ascii=False)
        return text

    def get_headers(self, environ=None):
        return [('Content-Type', 'application/json')]

    @staticmethod
    def get_url_no_parm():
        full_path = str(request.path)
        return full_path


class ServerError(APIException):
    res_code = 40001
    msg = CODE[40001]
    http_code = 500


class AddUserError(APIException):
    res_code = 10022
    msg = CODE[10022]
    http_code = 400


class UserNotFoundError(APIException):
    res_code = 10001
    msg = CODE[10001]
    http_code = 400

class UserPasswordError(APIException):
    res_code = 10002
    msg = CODE[10002]
    http_code = 400


class UserHaveExistedError(APIException):
    res_code = 10006
    msg = CODE[10006]
    http_code = 400


class ParameterException(APIException):
    res_code = 50002
    msg = CODE[50002]
    http_code = 400
    data = ''


class AuthFailed(APIException):
    res_code = 50001
    msg = CODE[50001]
    http_code = 400
    data = ''


class ValError(APIException):
    res_code = 50008
    msg = CODE[50008]
    http_code = 400
    data = ''