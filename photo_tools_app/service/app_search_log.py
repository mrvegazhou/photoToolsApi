# _*_ coding: utf-8 _*_
from photo_tools_app.model.app_search_log import AppSearchLog as AppSearchLogModel


class AppSearchLogService(object):
    @staticmethod
    def get_search_log_list_by_page(page_num=1, content=None, user_id=None, begin_date=None, end_date=None):
        search_log_list, total = AppSearchLogModel.get_search_log_list_by_page(page_num=page_num,
                                                                               content=content,
                                                                               user_id=user_id,
                                                                               begin_date=begin_date,
                                                                               end_date=end_date)
        return search_log_list, total

    @staticmethod
    def get_search_log_group_by(search_type=None, page_num=1, content=None, user_id=None, begin_date=None, end_date=None):
        search_log_list, total = AppSearchLogModel.get_search_log_list_group_by(search_type=search_type, page_num=page_num, content=content, user_id=user_id, begin_date=begin_date, end_date=end_date)
        lists = []
        for item in search_log_list:
            if search_type == 'group_by_content':
                content = item[0]
                user_id = r'%s%s' % ('搜索的用户总数:', item[1])
            else:
                content = r'%s%s' % ('搜索内容总数:', item[1])
                user_id = item[0]
            tmp = {'uuid': '', 'create_time': '', 'content': content, 'user_id': user_id}
            lists.append(tmp)
        return lists, total


