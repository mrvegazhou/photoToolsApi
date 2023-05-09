# _*_ coding: utf-8 _*_
import os, sys
import math
from datetime import datetime
from PIL import Image
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
    name = sys._getframe().f_code.co_name
    if job_id!=name:
        return None
    OP_FIX_IMG_JOB_ID = Constant.OP_FIX_IMG_JOB_ID.value
    type_dict = AppScheduledTasksService.get_type_content(OP_FIX_IMG_JOB_ID)
    if not type_dict:
        return None
    with app.app_context():
        total = AppScheduledTasksModel.get_scheduled_task_list_total(type=type_dict[0])
    page_size = Constant.PAGE_SIZE.value
    page_num = 1
    max_page_num = math.ceil(total / page_size)
    while max_page_num>0:
        start, end, _ = utils['common'].pagination(page_num, page_size, total)
        with app.app_context():
            tasks_list = AppScheduledTasksModel.get_scheduled_task_list_by_type(page_size=page_size, start=start, type=type_dict[0])
            for task in tasks_list:
                try:
                    create_time_struct = task['create_time']
                    create_time_struct = create_time_struct.replace(tzinfo=None)
                    now_struct = datetime.today()
                    dela = (now_struct - create_time_struct).total_seconds()
                    dela = math.ceil(dela)
                    if dela<=0:
                        if dela>=task['expire_age']:
                            # 老照片修复类型=3
                            if task['status'] and task['status']!=3:
                                if task['url']:
                                    urls = task['url']
                                    urls = urls.split(",")
                                    for url in urls:
                                        if os.path.exists(url):
                                            os.remove(url)
                            AppScheduledTasksModel.del_scheduled_task_info(task['uuid'])
                except Exception as e:
                    print("error:", str(e))


        page_num += 1
        max_page_num -= 1


# 处理redis队列中的待修复图片
def fix_img_scheduler_task(job_id=None):
    if not job_id:
        return None
    key = Constant.R_FIX_OLD_IMG.value
    total = cache.llen(key)
    if total==0:
        return None
    name = sys._getframe().f_code.co_name

    while total>0:
        task = cache.rpop(key)
        total -= 1
        task = str(task, encoding='utf-8')
        arr = task.split('|')
        if len(arr) == 6:
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
                flag = FixImgService.restore_old_photo_by_microsoft(new_file_name, ext, file_dir, file_input_file_path,
                                                                    file_output_dir_path)
                if flag:
                    old_img = new_file_name + '_old.' + ext
                    fixed_img = new_file_name + '_fixed.' + ext
                    content = ",".join([old_img, fixed_img])
                    img = Image.open(fixed_img)
                    extrema = img.convert("L").getextrema()
                    if extrema[0] == extrema[1]:
                        content = old_img+","
                        status = 3
                    del img
                    del extrema
                else:
                    content = full_file_path
                    status = 2
            except Exception as ex:
                content = full_file_path
                status = 2
                if os.path.exists(file_output_dir_path):
                    os.rmdir(file_output_dir_path)

            # 添加修复图片到AppScheduledTasksModel
            type_dict = AppScheduledTasksService.get_type_content(name)
            args = {
                'title': type_dict[1],
                'content': content,
                'type': type_dict[0],
                'status': status,
                'user_id': user_id,
                'expire_age': 60*60*24*7  # 一周
            }
            with app.app_context():
                AppScheduledTasksService.save_scheduled_task_info(args)
