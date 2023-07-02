# -*- coding: utf-8 -*-
import os, shutil, datetime
from werkzeug.datastructures import FileStorage

from photo_tools_app.__init__ import send, reqparse, Redprint, CODE, utils, g, scheduler, app, Logger
from photo_tools_app.utils.common_util import allowedFile
from photo_tools_app.utils.jwt_required import jwt_required
from photo_tools_app.service.image_upload import UploadImg
from photo_tools_app.service.static_pages import StaticPages
from photo_tools_app.service.image_scan import ScanImage
from core.cache.redis import RedisCache
from photo_tools_app.config.constant import Constant
from photo_tools_app.service.app_scheduled_tasks import AppScheduledTasksService
from photo_tools_app.crontab.scheduler_tasks import fix_img_scheduler_task, op_fix_img_scheduler_task


cache = RedisCache(app=app)
app_logger = Logger.setup_new_logger(logger_name="app_tool_api", log_path=Constant.BASE_PATH.value)

'''
修复老照片
'''
api = Redprint(name='fix')


@api.route('/restore', methods=["POST"])
@jwt_required
def ImageFix():
    # job_id = Constant.OP_FIX_IMG_JOB_ID.value
    # scheduler_obj = scheduler.scheduler
    # scheduler_obj.redis_client = cache.get_client()
    # scheduler_obj.lock_timeoout = 1800
    # scheduler.add_job(func=op_fix_img_scheduler_task, args=(job_id,), id=job_id, trigger="interval", seconds=5,
    #                   jobstore='redis')
    # return

    parser = reqparse.RequestParser()
    parser.add_argument('imgFile', required=True, type=FileStorage, location='files', help="图片错误")
    parser.add_argument('openid', type=str, required=True, help="用户标识错误", location='form')
    entry = parser.parse_args(http_error_code=50003)

    openid = entry.get('openid')
    if not openid or not g.uid:
        return send(10001, data=CODE[10001])

    # 先判断用户是否已经超过三张要修复的照片
    op_type = AppScheduledTasksService.get_type_content(Constant.FIX_IMG_JOB_ID.value)
    if not op_type:
        return send(500, data=CODE[500])
    total = AppScheduledTasksService.get_scheduled_task_list_by_user_total(g.uid, op_type[0])
    if total>=3:
        return send(80014, data=CODE[80014])

    img_file = entry.get('imgFile')

    ios = img_file.stream.read()

    file_size = len(ios)
    convertFileSize = utils['common'].convertFileSize

    if file_size>=app.config['MAX_UPLOAD_IMG_SIZE']:
        return send(80012, data=CODE[80012]+", 请上传小于"+convertFileSize(app.config['MAX_UPLOAD_IMG_SIZE']))

    # 上传文件
    new_file_name, file_dir, _ = UploadImg.createUploadPathAndFileName()
    sep = os.path.sep
    if img_file and allowedFile(img_file.filename):
        fname = utils['common'].secure_filename(img_file.filename)
        ext = fname.rsplit('.', 1)[1]

        # 文件输入地址
        file_input_file_path = r"{}{}{}{}input{}".format(file_dir, sep, new_file_name, sep, sep)
        try:
            if not os.path.exists(file_input_file_path):
                os.makedirs(file_input_file_path)
        except Exception:
            if os.path.exists(file_dir):
                shutil.rmtree(file_dir, ignore_errors=False, onerror=None)

        # 文件输出地址
        file_output_dir_path = r"{}{}{}{}output{}".format(file_dir, sep, new_file_name, sep, sep)
        try:
            if not os.path.exists(file_output_dir_path):
                os.makedirs(file_output_dir_path)
        except Exception:
            if os.path.exists(file_dir):
                shutil.rmtree(file_dir, ignore_errors=False, onerror=None)

        # 用户的老照片存储路径
        full_file_path = file_input_file_path + new_file_name + '.' + ext
        try:
            with open(full_file_path, 'wb') as f:
                f.write(ios)
        except Exception:
            #递归删除文件夹下的所有子文件夹和子文件
            if os.path.exists(file_dir):
                shutil.rmtree(file_dir, ignore_errors=False, onerror=None)
            return send(80005, data=CODE[80005])

        del ios

        val = "|".join([str(g.uid), new_file_name, ext, file_dir, file_input_file_path, file_output_dir_path])
        res = cache.lpush(Constant.R_FIX_OLD_IMG.value, [val])
        if not res:
            if os.path.exists(file_dir):
                shutil.rmtree(file_dir, ignore_errors=False, onerror=None)
            return send(30008, CODE[30008])
        else:
            # redis
            r_len = cache.llen(Constant.R_FIX_OLD_IMG.value)
            msg = '由于修复需消耗时间,请耐心等待.' if r_len>0 else '服务器还有{}张图片需要处理，请耐心等待.'.format(str(r_len))
            # 查看定时任务的状态
            job_id = Constant.FIX_IMG_JOB_ID.value
            job_status = scheduler.get_job(job_id)
            if job_status==None:
                scheduler_obj = scheduler.scheduler
                scheduler_obj.redis_client = cache.get_client()
                scheduler_obj.lock_timeoout = 1800
                scheduler.add_job(func=fix_img_scheduler_task, args=(job_id, ), id=job_id, trigger="interval", seconds=5, jobstore='redis')

            return send(200, data=msg)
    else:
        del ios
        return send(80005, data=CODE[80005])


@api.route('/list', methods=["POST", "GET"])
@jwt_required
def ImageFixList():
    parser = reqparse.RequestParser()
    parser.add_argument('openid', type=str, required=True, help="用户标识错误", location='json')
    entry = parser.parse_args(http_error_code=50003)
    openid = entry.get('openid')
    if g.uid and openid:
        op_type = AppScheduledTasksService.get_type_content(Constant.FIX_IMG_JOB_ID.value)
        if not op_type:
            return send(500, data=CODE[500])
        img_list = AppScheduledTasksService.get_scheduled_task_list_by_user(g.uid, op_type[0])
        res_list = []
        for img in img_list:
            new_img = {}
            new_img['status'] = img.status
            new_img['expire_age'] = (datetime.datetime.now()+datetime.timedelta(minutes=img.expire_age//60)).strftime("%Y-%m-%d %H:%M:%S")
            urls = img.content
            urls = urls.split(',')
            new_img['old_img'] = StaticPages.get_static_img_url_by_file_path(urls[0])
            new_img['new_img'] = StaticPages.get_static_img_url_by_file_path(urls[1]) if len(urls)==2 and img.status!=3 else "无法修复"
            res_list.append(new_img)
        return send(200, data=res_list)
    else:
        return send(10001, data=CODE[10001])


@api.route('/scan', methods=["POST"])
@jwt_required
def ImageScan():
    parser = reqparse.RequestParser()
    parser.add_argument('imgFile', required=True, type=FileStorage, location='files', help="图片错误")
    parser.add_argument('openid', type=str, required=True, help="用户标识错误", location='form')
    entry = parser.parse_args(http_error_code=50003)

    openid = entry.get('openid')

    img_file = entry.get('imgFile')

    ios = img_file.stream.read()

    file_size = len(ios)
    convertFileSize = utils['common'].convertFileSize

    if file_size >= app.config['MAX_UPLOAD_IMG_SIZE']:
        return send(80012, data=CODE[80012] + ", 请上传小于" + convertFileSize(app.config['MAX_UPLOAD_IMG_SIZE']))
    # 上传文件
    new_file_name, file_dir, _ = UploadImg.createUploadPathAndFileName()
    sep = os.path.sep
    if img_file and allowedFile(img_file.filename):
        fname = utils['common'].secure_filename(img_file.filename)
        ext = fname.rsplit('.', 1)[1]
        new_filename = new_file_name + '.' + ext
        # 文件输入地址
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        ori_file = os.path.join(file_dir, new_filename)
        try:
            with open(ori_file, 'wb') as f:
                f.write(ios)
        except Exception:
            return send(80005, data=CODE[80005])

        scanned_img = new_file_name + '_s.' + ext
        dst_path = "{}{}scan".format(file_dir, sep)
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)
        dst_file = os.path.join(dst_path, scanned_img)
        flag = ScanImage.get_outline_scan_img(ori_file, dst_file)
        if not flag:
            return send(80013, data=CODE[80013])
        else:
            return send(200, data={"oldImg": new_filename, "scannedImg": scanned_img})