# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/flask-api")
from stock_admin.model.admin_user import AdminUser
from stock_admin.__init__ import utils
from core.exception.api_exception import UserNotFoundError, AddUserError, UserHaveExistedError, UserPasswordError
from core.decorator.oath2_tool import clear_token
from stock_admin.service.admin_user_role import AdminUserRoleService
from stock_admin.config.constant import Constant

class AdminUserService:

    @staticmethod
    def on_login(username, password):
        user_info = AdminUser.get_userinfo_by_name(username)
        if not user_info:
            raise UserNotFoundError()
        salt = user_info.salt
        pwd = user_info.password
        if pwd != utils['common'].md5('{}{}'.format(password, salt)):
            raise UserPasswordError()
        #拥有的角色ids
        tmp_user_info = dict(user_info)
        del tmp_user_info['password']
        tmp_user_info['roles'] = AdminUserRoleService.get_user_role_ids(user_info.uuid)
        return tmp_user_info

    @staticmethod
    def logout(uuid):
        if not uuid:
            raise UserNotFoundError()
        res = clear_token(uuid)
        if res:
            return True
        else:
            return False

    @staticmethod
    def get_user_info(uuid):
        user_info = AdminUser.get_userinfo_by_uuid(uuid)
        del user_info.password
        del user_info.salt
        return user_info

    @staticmethod
    def update_password():
        pass

    @staticmethod
    def update_user(kwargs):
        uuid = kwargs['uuid']
        del kwargs['uuid']
        return AdminUser.update_admin_user_info(uuid, **kwargs)

    @staticmethod
    def del_user(uuid):
        return AdminUser.del_user([uuid])

    @staticmethod
    def register(username, password, phone, email, description, status=1):
        user_info = AdminUser.get_userinfo_by_name(username)
        if user_info is not None:
            raise UserHaveExistedError()
        res = AdminUser.add_new_admin_user(username, password, phone, email, description, status)
        if not res:
            raise AddUserError()
        return res

    @staticmethod
    def get_admin_user_list(page_num=1, page_size=Constant.ADMIN_PAGE_SIZE, username=None, status=None):
        list, total = AdminUser.get_users(page_num=page_num, page_size=page_size, username=username, status=status)
        admin_user_ids = [item.uuid for item in list]
        user_roles = AdminUserRoleService.get_user_role_dict(admin_user_ids)
        for i, val in enumerate(list):
            tmp = dict(val)
            del tmp['password']
            for i2, val2 in enumerate(user_roles):
                if val.uuid==val2[0]:
                    tmp['roles'] = val2[1].split(',')
            list[i] = tmp
        return list, total


if __name__ == "__main__":
    list = AdminUserService.register('admin000', 'admin@123', '18600521898', '234@qq.com', '描述')
    print(list)


