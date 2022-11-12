# _*_ coding: utf-8 _*_
from photo_tools_app.model.app_user import AppUser
from photo_tools_admin.config.constant import Constant
from photo_tools_admin.service.app_user import AppUser
from core.exception.api_exception import UserNotFoundError

class AppUserService(object):
    @staticmethod
    def getAppUserList(page_num=1,
                       page_size=Constant.ADMIN_PAGE_SIZE.value,
                       username=None,
                       email=None,
                       phone=None,
                       description=None,
                       type=None,
                       status=None,
                       begin_date=None,
                       end_date=None):
        list, total = AppUser.get_app_users(page_num=page_num,
                                            page_size=page_size,
                                            username=username,
                                            phone=phone,
                                            email=email,
                                            description=description,
                                            type=type,
                                            status=status,
                                            begin_date=begin_date,
                                            end_date=end_date)
        return list, total

    @staticmethod
    def updateAppUserInfo( uuid=None,
                           username=None,
                           email=None,
                           phone=None,
                           description=None,
                           type=None,
                           status=None):
        if not uuid:
            raise UserNotFoundError()
        return AppUser.update_app_user_info( uuid,
                                             username=username,
                                             email=email,
                                             phone=phone,
                                             description=description,
                                             type=type,
                                             status=status)

    @staticmethod
    def getAppUserInfo(uuid=None):
        if not uuid:
            raise UserNotFoundError()
        return AppUser.get_userinfo_by_uuid(uuid)

    @staticmethod
    def delAppUser(uuid=None):
        if not uuid:
            raise UserNotFoundError()
        return AppUser.del_user([uuid])
