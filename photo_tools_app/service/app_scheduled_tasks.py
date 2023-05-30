# _*_ coding: utf-8 _*_
from photo_tools_app.config.constant import Constant
from photo_tools_app.model.app_scheduled_tasks import AppScheduledTasks as AppScheduledTasksModel


class AppScheduledTasksService(object):
    @staticmethod
    def save_scheduled_task_info(info):
        if 'type' not in info or 'content' not in info or 'status' not in info or 'user_id' not in info or 'expire_age' not in info:
            return
        task = AppScheduledTasksModel()
        task.type = info['type']
        if info['content']:
            task.content = ','.join(info['content']) if isinstance(info['content'], list) else info['content']
        task.status = info['status']
        task.user_id = info['user_id']
        if 'title' in info and info['title']!='':
            task.title = info['title']
        task.expire_age = info['expire_age']
        return AppScheduledTasksModel.save_scheduled_task(task)

    @staticmethod
    def get_type_content(name):
        types = {
            # key:方法名 【 类型id，content内容，过期时间段 】
            'faceImgMatting': [1, '删除人像抠图后的图片', 1800],
            'imageCompose': [2, '删除人像和背景合成图片', 1800],
            Constant.FIX_IMG_JOB_ID.value: [3, '修复老照片', 1800],
            Constant.OP_FIX_IMG_JOB_ID.value: [3, '删除已修复完的老照片遗留的图片', 1800],
        }
        if name in types:
            return types[name]
        else:
            return 0

    @staticmethod
    def get_status(num):
        types = {
            1: '正常处理',
            2: '已删除',
            3: '异常',
        }
        if num in types:
            return types[num]
        else:
            return 3

    @staticmethod
    def get_scheduled_task_list_by_user(user_id, type):
        return AppScheduledTasksModel.get_scheduled_task_list_by_user(user_id, type)

    @staticmethod
    def get_scheduled_task_list_by_user_total(user_id, type):
        return AppScheduledTasksModel.get_scheduled_task_list_by_user_total(user_id, type)