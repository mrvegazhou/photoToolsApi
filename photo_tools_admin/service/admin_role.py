# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/photo-tools-api")
from itertools import groupby
from operator import itemgetter
from photo_tools_admin.model.admin_role import AdminRole
from core.exception.api_exception import APIException

class AdminRoleService:

    @staticmethod
    def get_roles():
        return AdminRole.get_roles()

    @staticmethod
    def add_role(title, description, status, sorts):
        res = AdminRole.get_role_by_condition(title=title)
        if res:
            raise APIException(msg='角色名称已存在', code=50009)
        title = title.strip()
        description = description.strip()
        return AdminRole.add_new_admin_role(title=title, sorts=sorts, description=description, status=status)

    @staticmethod
    def update_role_info(kwargs):
        uuid = kwargs['uuid']
        del kwargs['uuid']
        return AdminRole.update_role_info(uuid, **kwargs)

    @staticmethod
    def del_role_info(role_id):
        return AdminRole.del_role(role_id)


if __name__ == "__main__":
    from core.utils.common import md5
    print(md5("admin0r4uo"))

