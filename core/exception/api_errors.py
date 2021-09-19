# -*- coding: utf-8 -*-
from .api_exception import APIException
from ..decorator.oath2_tool import TokenErr
from ..__init__ import app
from ..utils.common import get_error_info
from ..http.response import send, CODE


@app.errorhandler(TokenErr)
def error_token(error):
    app.logger.debug("Token错误：{0}, {1}".format(error.desc, str(error.kwargs)))
    return send(error.code, error.msg)


@app.errorhandler(APIException)
def catch_error(error):
    file, line, func, _ = get_error_info()
    app.logger.error('代码错误：{0}, {1}({2})[{3}]'.format(str(error), file, line, func))
    return send(error.code, error.msg, error.data)


@app.errorhandler(404)
def handle_404_error(error):
    return send(404, CODE[404])
