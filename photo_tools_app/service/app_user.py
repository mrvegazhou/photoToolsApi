# _*_ coding: utf-8 _*_
from photo_tools_app.model.app_user import AppUser as AppUserModel

class AppUserService(object):
    @staticmethod
    def getAppUserList():
        pass

    @staticmethod
    def getAppUserInfo(openid, type_name='wechat'):
        type = 1
        if type_name=='wechat':
            type = 1
        elif type_name=='':
            type = 2
        attrs = [{'name': 'type', 'op': '=', 'val': type}, {'name': 'openid', 'op': '=', 'val': openid}]
        return AppUserModel.get_app_user_info_by_attr(attrs)
