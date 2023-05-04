# -*- coding: utf-8 -*-
import os
from werkzeug.datastructures import FileStorage
import json
import sys
from photo_tools_app.__init__ import send, reqparse, Redprint, utils, CODE, g
from photo_tools_app.utils.common_util import allowedFile
from photo_tools_app.utils.jwt_required import jwt_required
from photo_tools_app.service.face_detect import FaceDetect
from photo_tools_app.service.face_division import FaceDivision
from photo_tools_app.service.image_compose import ImageCompose
from photo_tools_app.service.static_pages import StaticPages
from photo_tools_app.service.image_upload import UploadImg
from photo_tools_app.service.app_scheduled_tasks import AppScheduledTasksService
from concurrent.futures import ThreadPoolExecutor

api = Redprint(name='photo')

executor = ThreadPoolExecutor()

@api.route('/faceImgMatting', methods=["POST"])
@jwt_required
def faceImgMatting():
    parser = reqparse.RequestParser()
    parser.add_argument('imgFile', required=True, type=FileStorage, location='files', help="图片错误")
    entry = parser.parse_args(http_error_code=50003)
    img_file = entry.get('imgFile')
    ios = img_file.stream.read()
    # 验证图片是否包含人像
    model, cfg = FaceDetect.getLibFaceDetection()
    dets = FaceDetect.libFaceDetection(model, cfg, ios)
    if len(dets) == 0:
        return send(80009, data=CODE[80009])

    # 上传文件
    new_file_name, file_dir, _ = UploadImg.createUploadPathAndFileName()
    cur_sep = os.path.sep

    if img_file and allowedFile(img_file.filename):

        fname = utils['common'].secure_filename(img_file.filename)
        ext = fname.rsplit('.', 1)[1]
        new_filename = new_file_name + '.' + ext

        if not os.path.exists(file_dir + cur_sep):
            os.makedirs(file_dir + cur_sep)

        try:
            # img_file.save(file_dir + cur_sep + new_filename)
            with open(file_dir + cur_sep + new_filename, 'wb') as f:
                f.write(ios)
        except Exception:
            return send(80005, data=CODE[80005])
        saved_img_file = '{}{}{}'.format(file_dir, cur_sep, new_filename)

        # 人脸抠图
        matting_face_img_path = '{}{}matting'.format(file_dir, cur_sep)
        if not os.path.exists(matting_face_img_path):
            os.makedirs(matting_face_img_path)
        try:
            FaceDivision.libFaceDivision(matting_face_img_path, saved_img_file)
        except Exception:
            return send(80010, data=CODE[80010])

        faceImgUrl = "/static/page/img/{}".format(new_filename)
        mattingFaceImgUrl = "/static/page/img/{}_rgba.png".format(new_file_name)

        # 异步删除图片
        name = sys._getframe().f_code.co_name
        args = {
            'type': AppScheduledTasksService.get_type(name),
            'content': [file_dir + cur_sep + new_filename,  file_dir + cur_sep + new_file_name + '_rgba.png'],
            'status': 1,
            'user_id': g.uid or 0,
            'name': AppScheduledTasksService.get_content(name),
        }
        executor.submit(AppScheduledTasksService.save_scheduled_task_info, args)

        return send(200, data={'faceImg': faceImgUrl, 'mattingFaceImg': mattingFaceImgUrl})
    else:
        return send(80005, data=CODE[80005])


@api.route('/imageCompose', methods=["POST"])
@jwt_required
def imageCompose():
    parser = reqparse.RequestParser()
    parser.add_argument('baseImg', type=str, required=True, help="背景图参数错误")
    parser.add_argument('peopleImg', type=str, required=True, help="人像参数错误")
    args = parser.parse_args(http_error_code=50009)
    baseImg = args['baseImg']
    peopleImg = args['peopleImg']
    try:
        baseImg = json.dumps(eval(baseImg))
        peopleImg = json.dumps(eval(peopleImg))
    except Exception:
        return send(50011, data=CODE[50011])

    baseImgObj = json.loads(baseImg)
    bgWidth = int(baseImgObj['width'])
    bgHeight = int(baseImgObj['height'])
    # 生成背景图
    bgImg = ImageCompose.createImage(tuple(baseImgObj['bgc']), bgWidth, bgHeight)

    peopleImgObj = json.loads(peopleImg)
    # 人像图片地址
    imgFile = peopleImgObj['img']
    _, imgFullName = imgFile.rsplit('/', 1)
    imgPath, fileName, ext = StaticPages.getStaticPageUrl(imgFullName)
    # imgPath为原始图片路径
    peopleNewImg = ImageCompose.imageResize(imgPath, int(peopleImgObj['width']), int(peopleImgObj['height']))

    newBgAndPeopleImg = ImageCompose.drawRectImg(bgImg, peopleNewImg, round(peopleImgObj['x']), round(peopleImgObj['y']))
    cur_sep = os.path.sep
    savePath = "{}{}compose".format(imgPath.rsplit('/', 2)[0], cur_sep)
    if not os.path.exists(savePath):
        os.makedirs(savePath)
    c_png = "{}{}{}_c.png".format(savePath, cur_sep, fileName)
    newBgAndPeopleImg.save(c_png)

    # 异步删除图片
    name = sys._getframe().f_code.co_name
    args = {
        'type': 1,
        'content': [imgPath, c_png],
        'status': 1,
        'name': AppScheduledTasksService.get_content(name),
    }
    executor.submit(AppScheduledTasksService.save_scheduled_task_info, args)

    del bgImg
    del newBgAndPeopleImg

    return send(200, data={"composeImgPath": "/static/page/img/{}_c.png".format(fileName)})