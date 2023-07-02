# -*- coding: utf-8 -*-
from photo_tools_app.__init__ import g, send, reqparse, Redprint, CODE, utils, app
from photo_tools_app.service.app_ad import AppAdService
from photo_tools_app.utils.jwt_required import jwt_required

api = Redprint(name='ad')


@api.route('/list', methods=["GET", "POST"])
@jwt_required
def AppAds():
    parser = reqparse.RequestParser()
    parser.add_argument('type', type=str, help="类型", location='json')
    entry = parser.parse_args(http_error_code=50003)
    ad_list = AppAdService.get_ad_list_by_type(entry.get('type'))
    return send(200, data={"list": ad_list})

