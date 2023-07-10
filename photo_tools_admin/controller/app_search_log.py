# -*- coding: utf-8 -*-
from photo_tools_admin.__init__ import send, reqparse, g
from photo_tools_admin.decorator.oath2_tool import need_login
from . import admin
from photo_tools_app.service.app_search_log import AppSearchLogService


@admin.route('/getSearchLogList', methods=['POST', 'GET'])
def get_search_log_list():
    parser = reqparse.RequestParser()
    parser.add_argument('page_num', help='当前页错误', type=int, location='json')
    parser.add_argument('content', help='搜索内容', type=str, location='json')
    parser.add_argument('user_id', help='用户', type=int, location='json')
    parser.add_argument('search_type', help='搜索类型', type=str, location='json')
    parser.add_argument('begin_date', help='开始时间', type=str, location='json')
    parser.add_argument('end_date', help='结束时间', type=str, location='json')
    entry = parser.parse_args(http_error_code=50003)
    page_num = entry.get('page_num')
    content = entry.get('content')
    user_id = entry.get('user_id')
    begin_date = entry.get('begin_date')
    end_date = entry.get('end_date')
    search_type = entry.get('search_type')
    if search_type=='group_by_content':
        log_list, total = AppSearchLogService.get_search_log_group_by(page_num=page_num,
                                                                              content=content,
                                                                              user_id=user_id,
                                                                              begin_date=begin_date,
                                                                              end_date=end_date,
                                                                              search_type='group_by_content')
    elif search_type=='group_by_user_id':
        log_list, total = AppSearchLogService.get_search_log_group_by(page_num=page_num,
                                                                              content=content,
                                                                              user_id=user_id,
                                                                              begin_date=begin_date,
                                                                              end_date=end_date,
                                                                              search_type='group_by_user_id')
    else:
        log_list, total = AppSearchLogService.get_search_log_list_by_page(page_num=page_num,
                                                                          content=content,
                                                                          user_id=user_id,
                                                                          begin_date=begin_date,
                                                                          end_date=end_date)
    return send(200, data={"list": log_list, "total": total})

