# -*- coding: utf-8 -*-
from photo_tools_admin.__init__ import send, reqparse, g
from photo_tools_admin.decorator.oath2_tool import need_login
from . import admin
from photo_tools_app.service.app_feedback import AppFeedbackService


@admin.route('/getFeedbackList', methods=['POST', 'GET'])
def get_feedbacks():
    parser = reqparse.RequestParser()
    parser.add_argument('page_num', help='当前页错误', type=int, location='json')
    parser.add_argument('content', help='反馈内容出错', type=str, location='json')
    parser.add_argument('contact', help='联系方式错误', type=str, location='json')
    parser.add_argument('type', help='反馈类型出错', type=int, location='json')
    parser.add_argument('begin_date', help='开始时间', type=str, location='json')
    parser.add_argument('end_date', help='结束时间', type=str, location='json')
    entry = parser.parse_args(http_error_code=50003)
    page_num = entry.get('page_num')
    type = entry.get('type')
    content = entry.get('content')
    contact = entry.get('contact')
    begin_date = entry.get('begin_date')
    end_date = entry.get('end_date')
    list, total = AppFeedbackService.get_feedback_list(page_num=page_num, content=content, contact=contact, type=type, begin_date=begin_date, end_date=end_date)
    return send(200, data={"list": list, "total": total})


@admin.route('/delFeedback', methods=['POST'])
def del_feedback():
    parser = reqparse.RequestParser()
    parser.add_argument('uuid', help='反馈标识出错', type=int, location='json')
    entry = parser.parse_args(http_error_code=50003)
    uuid = entry.get('uuid')
    res = AppFeedbackService.del_feedback(uuid)
    return send(200, data=res)


@admin.route('/replyFeedback', methods=['POST'])
@need_login
def reply_feedback():
    parser = reqparse.RequestParser()
    parser.add_argument('feedback_id', help='反馈信息标识', type=int, location='json')
    parser.add_argument('content', help='反馈信息的回复内容', type=str, location='json')
    parser.add_argument('to_user_id', help='反馈信息的被回复人', type=int, location='json')
    entry = parser.parse_args(http_error_code=50003)
    feedback_id = entry.get('feedback_id')
    content = entry.get('content')
    to_user_id = entry.get('to_user_id')
    # 0 代表admin
    reply_user_id = -g.admin_user_id
    res = AppFeedbackService.reply_feedback(feedback_id, content, to_user_id, reply_user_id)
    return send(200, data=res)


@admin.route('/replyFeedbackList', methods=['POST', 'GET'])
def reply_feedback_list():
    parser = reqparse.RequestParser()
    parser.add_argument('feedback_id', help='反馈信息标识', type=int, location='json')
    entry = parser.parse_args(http_error_code=50003)
    feedback_id = entry.get('feedback_id')
    list = AppFeedbackService.get_reply_feedback_list(feedback_id)
    return send(200, data=list)






