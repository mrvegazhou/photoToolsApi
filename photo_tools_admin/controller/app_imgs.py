# -*- coding: utf-8 -*-
from photo_tools_admin.__init__ import send, reqparse
from photo_tools_admin.decorator.oath2_tool import need_login
from . import admin
from photo_tools_app.service.app_imgs import AppImgsService


@admin.route('/getAppImgs', methods=['POST', 'GET'])
def get_imgs():
    parser = reqparse.RequestParser()
    parser.add_argument('page_num', help='当前页错误', type=int, location='json')
    # parser.add_argument('page_size', help='每页显示总数错误', type=int, location='json')
    parser.add_argument('type', help='图片类型', type=int, location='json')
    parser.add_argument('tags', help='图片标签', type=str, location='json')
    parser.add_argument('url', help='图片地址', type=str, location='json')
    parser.add_argument('begin_date', help='开始时间', type=str, location='json')
    parser.add_argument('end_date', help='结束时间', type=str, location='json')
    entry = parser.parse_args(http_error_code=50003)
    page_num = entry.get('page_num')
    # page_size = entry.get('page_size')
    type = entry.get('type')
    tags = entry.get('tags')
    url = entry.get('url')
    begin_date = entry.get('begin_date')
    end_date = entry.get('end_date')
    list, total = AppImgsService.get_app_imgs_list_by_page(page=page_num, tags=tags, url=url, type=type, begin_date=begin_date, end_date=end_date)
    return send(200, data={"list": list, "total": total})


@admin.route('/updateImg', methods=['POST'])
def update_img():
    parser = reqparse.RequestParser()
    parser.add_argument('uuid', help='图片id', type=int, location='json')
    parser.add_argument('type', help='图片类型', type=int, location='json')
    parser.add_argument('tags', help='图片标签', type=str, location='json')
    parser.add_argument('url', help='图片地址', type=str, location='json')
    entry = parser.parse_args(http_error_code=50003)
    uuid = entry.get('uuid')
    type = entry.get('type')
    tags = entry.get('tags')
    url = entry.get('url')
    res = AppImgsService.update_app_img(uuid, type=type, tags=tags, url=url)
    return send(200, data={"res": res})


@admin.route('/delImg', methods=['POST'])
def del_img():
    parser = reqparse.RequestParser()
    parser.add_argument('uuid', help='图片id', type=int, location='json')
    entry = parser.parse_args(http_error_code=50003)
    uuid = entry.get('uuid')
    res = AppImgsService.del_app_img(uuid)
    return send(200, data={"res": res})
