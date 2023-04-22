# -*- coding: utf-8 -*-
from photo_tools_app.__init__ import send, reqparse, Redprint, CODE, utils, app
from photo_tools_app.utils.jwt_required import jwt_required
from photo_tools_app.service.app_imgs import AppImgsService

api = Redprint(name='search')


@api.route('/list', methods=["POST"])
# @jwt_required
def AppImgs():
    parser = reqparse.RequestParser()
    parser.add_argument('tags', type=str, help="搜索内容", location='json')
    parser.add_argument('load_time', type=str, help="搜索时间戳", location='json')
    parser.add_argument('page', type=int, help="页码", default=1, location='json')
    entry = parser.parse_args(http_error_code=50003)

    tags = entry.get('tags')
    page = entry.get('page')
    load_time = entry.get('load_time')
    list = AppImgsService.get_app_imgs_list(page=page, tags=tags, load_time=load_time)
    return send(200, data={"list": list})