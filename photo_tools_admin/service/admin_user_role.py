# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/photo-tools-api")
import typing
from photo_tools_admin.model.admin_user_role import AdminUserRole
from core.exception.api_exception import ValError


class AdminUserRoleService:

    @staticmethod
    def get_user_role_ids(admin_user_id):
        roles = AdminUserRoleService.get_user_role_list(admin_user_id)
        role_ids = []
        for role in roles:
            role_ids.append(role.role_id)
        return role_ids

    @staticmethod
    def get_user_role_list(admin_user_id):
        if not admin_user_id and not isinstance(admin_user_id, int):
            raise ValError()
        return AdminUserRole.get_user_role_info(admin_user_id)

    @staticmethod
    def assgin_roles(admin_user_id, role_ids):
        if not role_ids:
            res = AdminUserRole.del_by_admin_user(admin_user_id)
        else:
            res = AdminUserRole.assign_user_roles(admin_user_id, role_ids)
        return res

    @staticmethod
    def get_user_role_dict(admin_user_ids: typing.List):
        if not admin_user_ids:
            return []
        return AdminUserRole.get_user_role_dict(admin_user_ids)




