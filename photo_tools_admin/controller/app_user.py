# -*- coding: utf-8 -*-
from photo_tools_admin.__init__ import send, reqparse, func, request
from . import admin
from photo_tools_admin.service.app_user import AppUserService
from photo_tools_app.model.app_user import AppUser
import json

@admin.route('/appUserList', methods=['POST'])
def AppUserList():
    entry = request.get_json()
    username = entry.get('username')
    email = entry.get('email')
    phone = entry.get('phone')
    description = entry.get('description')
    status = entry.get('status')
    beginDate = entry.get('begin_date')
    endDate = entry.get('end_date')
    pageNum = entry.get('page_num')
    pageSize = entry.get('page_size')
    list, total = AppUserService.getAppUserList(page_num=pageNum,
                                                page_size=pageSize,
                                                username=username,
                                                phone=phone,
                                                email=email,
                                                description=description,
                                                status=status,
                                                begin_date=beginDate,
                                                end_date=endDate)
    return send(200, data={"list": list, "total": total})


@admin.route('/updateAppUserInfo', methods=['POST'])
def UpdateAppUserInfo():
    parser = reqparse.RequestParser()
    parser.add_argument('uuid', type=int, required=True, help="用户标识错误", location='form')
    parser.add_argument('username', type=str, help="用户名错误", location='form')
    parser.add_argument('email', type=str, help="邮箱错误", location='form')
    parser.add_argument('phone', type=str, help="电话错误", location='form')
    parser.add_argument('status', type=str, help="状态错误", location='form')
    parser.add_argument('description', type=str, help="备注错误", location='form')
    parser.add_argument('beginDate', type=str, help="创建的开始时间错误", location='form')
    parser.add_argument('endDate', type=str, help="创建的结束时间错误", location='form')
    entry = parser.parse_args(http_error_code=50003)
    res = AppUserService.updateAppUserInfo(entry.get('uuid'),
                                             username=entry.get('username'),
                                             email=entry.get('email'),
                                             phone=entry.get('phone'),
                                             status=entry.get('status'),
                                             description=entry.get('description'))
    return send(200, data=res)


@admin.route('/getAppUserInfo', methods=['POST'])
def getAppUserInfo():
    parser = reqparse.RequestParser()
    parser.add_argument('uuid', type=int, required=True, help="用户标识错误", location='form')
    entry = parser.parse_args(http_error_code=50003)
    uuid = entry.get('uuid')
    user_info = AppUserService.getAppUserInfo(uuid)
    return send(200, data=user_info)


@admin.route('/delAppUser', methods=['POST'])
def delAppUserInfo():
    parser = reqparse.RequestParser()
    parser.add_argument('uuid', help='用户标识错误', type=int)
    args = parser.parse_args(http_error_code=50003)
    res = AppUserService.delAppUser(args['uuid'])
    if res:
        return send(200, data=res)
    else:
        return send(90002, data=False)


@admin.route('/addAppUser', methods=['POST'])
def addAppUser():
    entry = request.get_json()
    appUserObj = AppUser()
    appUserObj.username = entry.get('username')
    appUserObj.email = entry.get('email')
    appUserObj.phone = entry.get('phone')
    appUserObj.status = entry.get('status')
    appUserObj.description = entry.get('description')
    appUserObj.create_time = func.now()
    res = AppUserService.addAppUserInfo(appUserObj)
    if res:
        return send(200, data=res)
    else:
        return send(90000, data=False)
