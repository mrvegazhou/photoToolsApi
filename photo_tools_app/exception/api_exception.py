# -*- coding: utf-8 -*-
from photo_tools_app.__init__ import APIException
from photo_tools_app.__init__ import CODE


class WeChatException(APIException):
    res_code = 70000
    msg = CODE[70000]
    http_code = 500
    data = ''

class JWTExpiredSignatureError(APIException):
    res_code = 20007
    msg = CODE[20007]
    http_code = 401
    data = ''

class JWTDecodeError(APIException):
    res_code = 20006
    msg = CODE[20006]
    http_code = 401
    data = ''

class JWTInvalidTokenError(APIException):
    res_code = 20008
    msg = CODE[20008]
    http_code = 401
    data = ''

class FaceDetModelParseeFailed(APIException):
    res_code = 80001
    msg = CODE[80001]
    http_code = 401

class FaceDetModelLoaderFailed(APIException):
    res_code = 80002
    msg = CODE[80002]
    http_code = 401

class FaceDetectionImgFailed(APIException):
    res_code = 80003
    msg = CODE[80003]
    http_code = 401

class CreateImgParamFailed(APIException):
    res_code = 80004
    msg = CODE[80004]
    http_code = 401

class FaceImgSaveDirFailed(APIException):
    res_code = 80007
    msg = CODE[80007]
    http_code = 401

class FaceImgNotExists(APIException):
    res_code = 80008
    msg = CODE[80008]
    http_code = 401

class FeedbackContentIsNull(APIException):
    res_code = 11001
    msg = CODE[11001]
    http_code = 401

class FeedbackTypeIsNull(APIException):
    res_code = 11002
    msg = CODE[11002]
    http_code = 401

class FeedbackIdIsNull(APIException):
    res_code = 11005
    msg = CODE[11005]
    http_code = 401

class FeedbackReplyContentIsNull(APIException):
    res_code = 11003
    msg = CODE[11003]
    http_code = 401

class FeedbackReplyReplyUserIsNull(APIException):
    res_code = 11004
    msg = CODE[11004]
    http_code = 401

class FeedbackReplyToUserIsNull(APIException):
    res_code = 11006
    msg = CODE[11006]
    http_code = 401

class AdTpyeIsNull(APIException):
    res_code = 12001
    msg = CODE[12001]
    http_code = 401

class AdContentIsNull(APIException):
    res_code = 12002
    msg = CODE[12002]
    http_code = 401

class AdUrlIsNull(APIException):
    res_code = 12003
    msg = CODE[12003]
    http_code = 401

class DatabaseError(APIException):
    res_code = 40007
    msg = CODE[40007]
    http_code = 401