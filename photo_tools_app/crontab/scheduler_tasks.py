# _*_ coding: utf-8 _*_
import os, math, sys
from core.cache.redis import RedisCache
from photo_tools_app.__init__ import utils, app
from photo_tools_app.config.constant import Constant
from photo_tools_app.model.app_scheduled_tasks import AppScheduledTasks as AppScheduledTasksModel
from photo_tools_app.service.app_scheduled_tasks import AppScheduledTasksService
from photo_tools_app.service.image_fix import FixImgService

cache = RedisCache(app=app)

# 删除修复图片
def op_fix_img_scheduler_task(job_id=None):
    if not job_id:
        return None
    type = AppScheduledTasksModel.get_type(job_id)
    if not type:
        return None
    total = AppScheduledTasksModel.get_scheduled_task_list_total(type=type)
    page_size = Constant.PAGE_SIZE.value
    page_num = 1
    max_page_num = math.ceil(total / page_size)
    while max_page_num>0:
        start, end, _ = utils['common'].pagination(page_num, page_size, total)
        tasks_list = AppScheduledTasksModel.get_scheduled_task_list_by_type(page_size=page_size,start=start, type=type)
        for task in tasks_list:
            # 文件输出地址
            file_output_dir_path = task['content']
            if not os.path.exists(file_output_dir_path):
                os.makedirs(file_output_dir_path)
            # #修复图片
            # try:
            #     flag = FixImg.restore_old_photo_by_microsoft(new_file_name, ext, file_dir, file_input_file_path, file_output_dir_path)
            #     if not flag:
            #         return send(80011, data=CODE[80011])
            # except Exception:
            #     return send(80011, data=CODE[80011])
            #
            # old_img = new_file_name + '_old.' + ext
            # fixed_img = new_file_name + '_fixed.' + ext
        page_num += 1
        max_page_num -= 1


# 处理redis队列中的待修复图片
def fix_img_scheduler_task(job_id=None):
    if not job_id:
        return None
    page_size = Constant.PAGE_SIZE.value
    total = cache.llen(Constant.R_FIX_OLD_IMG)
    max_page_num = math.ceil(total / page_size)
    page_num = 1
    name = sys._getframe().f_code.co_name
    while max_page_num>0:
        start, end, _ = utils['common'].pagination(page_num, page_size, total)
        tasks_list = cache.lrange(Constant.R_FIX_OLD_IMG.value, start, page_size)
        if len(tasks_list)>0:
            for task in tasks_list:
                arr = task.split('|')
                if len(arr)==6:
                    user_id = arr[0]
                    new_file_name = arr[1]
                    ext = arr[2]
                    file_dir = arr[3]
                    file_input_file_path = arr[4]
                    file_output_dir_path = arr[5]
                    content = ''
                    status = 1
                    # 用户的老照片存储路径
                    full_file_path = file_input_file_path + new_file_name + '.' + ext

                    # 开始修复
                    try:
                       flag = FixImgService.restore_old_photo_by_microsoft(new_file_name, ext, file_dir, file_input_file_path, file_output_dir_path)
                       if flag:
                           old_img = new_file_name + '_old.' + ext
                           fixed_img = new_file_name + '_fixed.' + ext
                           content = ",".join([old_img, fixed_img])
                       else:
                           content = full_file_path
                           status = 2
                    except Exception:
                        content = full_file_path
                        status = 2
                        if os.path.exists(file_output_dir_path):
                            os.rmdir(file_output_dir_path)

                    # 添加修复图片到AppScheduledTasksModel
                    args = {
                        'title': AppScheduledTasksService.get_content(name),
                        'content': content,
                        'type': AppScheduledTasksService.get_type(name),
                        'status': status,
                        'user_id': user_id,
                    }
                    AppScheduledTasksService.save_scheduled_task_info(args)

        page_num += 1
        max_page_num -= 1


