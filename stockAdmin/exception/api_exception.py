# -*- coding: utf-8 -*-
from stock_admin.__init__ import APIException
from stock_admin.__init__ import CODE


class RoleNotFoundFailed(APIException):
    res_code = 60001
    msg = CODE[60001]
    http_code = 400
    data = ''


class MenuNotFoundFailed(APIException):
    res_code = 60002
    msg = CODE[60002]
    http_code = 400
    data = ''


class DelRoleFailed(APIException):
    res_code = 60003
    msg = CODE[60003]
    http_code = 400
    data = ''



