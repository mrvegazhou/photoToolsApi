# -*- coding: utf-8 -*-
from photo_tools_app.__init__ import g, send, reqparse, Redprint, CODE, utils, app
from photo_tools_app.service.app_feedback import AppFeedbackService
from photo_tools_app.utils.jwt_required import jwt_required

api = Redprint(name='msg')


@api.route('/add', methods=["POST"])
@jwt_required
def AppFeedback():
    parser = reqparse.RequestParser()
    parser.add_argument('type', type=str, help="反馈类型", location='json')
    parser.add_argument('content', type=str, help="反馈内容", location='json')
    parser.add_argument('contact', type=str, help="联系方式", default='', location='json')
    parser.add_argument('imgs', type=str, action='append', help="附件", default='', location='json')
    entry = parser.parse_args(http_error_code=50003)
    user_id = g.uuid or 111
    info = {
        'type': entry.get('type'),
        'content': entry.get('content'),
        'contact': entry.get('contact'),
        'imgs': entry.get('imgs'),
        'user_id': user_id
    }
    res = AppFeedbackService.save_feedback_info(info)
    return send(200, data={"res": res})





