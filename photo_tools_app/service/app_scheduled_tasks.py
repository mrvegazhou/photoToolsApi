# _*_ coding: utf-8 _*_
from photo_tools_app.model.app_scheduled_tasks import AppScheduledTasks as AppScheduledTasksModel


class AppScheduledTasksService(object):
    @staticmethod
    def save_scheduled_task_info(info):
        if 'type' not in info or 'content' not in info or 'status' not in info or 'user_id' not in info:
            return
        task = AppScheduledTasksModel()
        task.type = info['type']
        if info['content']:
            task.content = ','.join(info['content']) if isinstance(info['content'], list) else info['content']
        task.status = info['status']
        task.user_id = info['user_id']
        if 'title' in info and info['title']!='':
            task.title = info['title']
        return AppScheduledTasksModel.save_scheduled_task(task)

    @staticmethod
    def get_content(name):
        contents = {
            'faceImgMatting': '删除人像抠图后的图片',
            'imageCompose': '删除人像和背景合成图片',
            'input_full_file_path': '修复老照片',
        }
        if name in contents:
            return contents[name]
        else:
            return ''

    @staticmethod
    def get_type_content(name):
        types = {
            'faceImgMatting': [1],
            'imageCompose': [2],
            'input_full_file_path': 3,
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