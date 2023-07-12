# -*- coding: utf-8 -*-
from photo_tools_admin.__init__ import send, reqparse
from photo_tools_admin.decorator.oath2_tool import need_login
from . import admin
from photo_tools_app.service.app_img_library import AppImgLibraryService


@admin.route('/getAppImgLib', methods=['POST', 'GET'])
def get_img_lib():
    parser = reqparse.RequestParser()
    parser.add_argument('page_num', help='当前页错误', type=int, location='json')
    parser.add_argument('tags', help='图片标签', type=int, location='json')
    parser.add_argument('note', help='图片备注', type=str, location='json')
    parser.add_argument('url', help='图片地址', type=str, location='json')
    parser.add_argument('begin_date', help='开始时间', type=str, location='json')
    parser.add_argument('end_date', help='结束时间', type=str, location='json')
    entry = parser.parse_args(http_error_code=50003)
    page_num = entry.get('page_num')
    note = entry.get('note')
    tags = entry.get('tags')
    url = entry.get('url')
    begin_date = entry.get('begin_date')
    end_date = entry.get('end_date')
    lists, total = AppImgLibraryService.get_app_img_lib_list_by_page(page_num=page_num, tags=tags, url=url, note=note,
                                                                     begin_date=begin_date, end_date=end_date)
    return send(200, data={"list": lists, "total": total, "pageSize": 20})


@admin.route('/updateImgLib', methods=['POST'])
def update_img_lib():
    parser = reqparse.RequestParser()
    parser.add_argument('uuid', help='图片id', type=int, location='json')
    parser.add_argument('tags', help='图片标签', type=int, location='json')
    parser.add_argument('note', help='图片备注', type=str, location='json')
    parser.add_argument('url', help='图片地址', type=str, location='json')
    entry = parser.parse_args(http_error_code=50003)
    uuid = entry.get('uuid')
    type = entry.get('type')
    tags = entry.get('tags')
    url = entry.get('url')
    res = AppImgLibraryService.update_app_img_lib(uuid, type=type, tags=tags, url=url)
    return send(200, data={"res": res})


@admin.route('/delImgLib', methods=['POST'])
def del_img_lib():
    parser = reqparse.RequestParser()
    parser.add_argument('uuid', help='图片id', type=int, location='json')
    entry = parser.parse_args(http_error_code=50003)
    uuid = entry.get('uuid')
    res = AppImgLibraryService.del_app_img_lib(uuid)
    return send(200, data={"res": res})

