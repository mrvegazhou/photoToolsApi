# -*- coding: utf-8 -*-

import os, uuid
from werkzeug.datastructures import FileStorage
import json

from photo_tools_app.__init__ import send, reqparse, Redprint
from photo_tools_app.utils.common_util import allowedFile
from photo_tools_app.utils.jwt_required import jwt_required
from photo_tools_app.utils.common_util import getUploadDirs
from photo_tools_app.__init__ import CODE


api = Redprint(name='fix')

@api.route('/faceImgMatting', methods=["POST"])
@jwt_required
def ImageFix():
    parser = reqparse.RequestParser()
    parser.add_argument('imgFile', required=True, type=FileStorage, location='files', help="图片错误")
    entry = parser.parse_args(http_error_code=50003)

    img_file = entry.get('imgFile')
    ios = img_file.stream.read()

    #修复图片



