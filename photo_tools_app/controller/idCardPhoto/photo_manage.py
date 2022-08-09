# -*- coding: utf-8 -*-
import os, uuid
from werkzeug.datastructures import FileStorage
import json

from photo_tools_app.__init__ import app
from photo_tools_app.__init__ import send, reqparse, Redprint
from photo_tools_app.utils.common_util import allowedFile
from photo_tools_app.__init__ import utils
from photo_tools_app.utils.jwt_required import jwt_required
from photo_tools_app.utils.common_util import getUploadDirs
from photo_tools_app.__init__ import CODE
from photo_tools_app.service.face_detect import FaceDetect
from photo_tools_app.service.face_division import FaceDivision
from photo_tools_app.service.image_compose import ImageCompose
from photo_tools_app.service.static_pages import StaticPages
from photo_tools_app.service.image_upload import UploadImg

api = Redprint(name='photo')


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
    new_file_name, file_dir = UploadImg.createUploadPathAndFileName()
    cur_sep = os.path.sep

    if img_file and allowedFile(img_file.filename):

        fname = utils['common'].secure_filename(img_file.filename)
        ext = fname.rsplit('.', 1)[1]
        new_filename = new_file_name + '.' + ext
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
    bgImg = ImageCompose.createImage(tuple(baseImgObj['bgc']), bgWidth, bgHeight)

    peopleImgObj = json.loads(peopleImg)
    imgFile = peopleImgObj['img']
    _, imgFullName = imgFile.rsplit('/', 1)
    imgPath, fileName, ext = StaticPages.getStaticPageUrl(imgFullName)
    peopleNewImg = ImageCompose.imageResize(imgPath, int(peopleImgObj['width']), int(peopleImgObj['height']))

    newBgAndPeopleImg = ImageCompose.drawRectImg(bgImg, peopleNewImg, round(peopleImgObj['x']), round(peopleImgObj['y']))
    cur_sep = os.path.sep
    savePath = "{}{}compose".format(imgPath.rsplit('/', 2)[0], cur_sep)
    if not os.path.exists(savePath):
        os.makedirs(savePath)
    newBgAndPeopleImg.save("{}{}{}_c.png".format(savePath, cur_sep, fileName))

    return send(200, data={"composeImgPath": "/static/page/img/{}_c.png".format(fileName)})