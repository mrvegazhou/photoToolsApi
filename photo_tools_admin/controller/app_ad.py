# -*- coding: utf-8 -*-
from photo_tools_admin.__init__ import send, reqparse, g
from photo_tools_admin.decorator.oath2_tool import need_login
from . import admin
from photo_tools_app.service.app_ad import AppAdService


@admin.route('/getAdList', methods=['POST', 'GET'])
def get_ads():
    parser = reqparse.RequestParser()
    parser.add_argument('page_num', help='当前页错误', type=int, location='json')
    parser.add_argument('content', help='广告内容出错', type=str, location='json')
    parser.add_argument('url', help='广告地址错误', type=str, location='json')
    parser.add_argument('type', help='广告类型出错', type=int, location='json')
    parser.add_argument('begin_date', help='开始时间', type=str, location='json')
    parser.add_argument('end_date', help='结束时间', type=str, location='json')
    entry = parser.parse_args(http_error_code=50003)
    page_num = entry.get('page_num')
    type = entry.get('type')
    content = entry.get('content')
    url = entry.get('url')
    begin_date = entry.get('begin_date')
    end_date = entry.get('end_date')
    ad_list, total = AppAdService.get_ad_list_by_page(page_num=page_num, type=type, content=content, url=url, begin_date=begin_date, end_date=end_date)
    return send(200, data={"list": ad_list, "total": total})


@admin.route('/delAd', methods=['POST'])
def del_ad():
    parser = reqparse.RequestParser()
    parser.add_argument('uuid', help='反馈标识出错', type=int, location='json')
    entry = parser.parse_args(http_error_code=50003)
    uuid = entry.get('uuid')
    res = AppAdService.del_ad_by_id(uuid)
    return send(200, data=res)


@admin.route('/addAd', methods=['POST'])
def add_ad():
    parser = reqparse.RequestParser()
    parser.add_argument('content', help='广告内容出错', type=str, location='json')
    parser.add_argument('url', help='广告地址错误', type=str, location='json')
    parser.add_argument('type', help='广告类型出错', type=int, location='json')
    entry = parser.parse_args(http_error_code=50003)
    type = entry.get('type')
    content = entry.get('content')
    url = entry.get('url')
    res = AppAdService.save_ad(type, content, url)
    return send(200, data=res)

