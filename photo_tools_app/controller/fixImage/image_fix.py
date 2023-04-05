# -*- coding: utf-8 -*-
import os
from werkzeug.datastructures import FileStorage

from photo_tools_app.__init__ import send, reqparse, Redprint, CODE, utils, app
from photo_tools_app.utils.common_util import allowedFile
from photo_tools_app.utils.jwt_required import jwt_required
from photo_tools_app.service.image_upload import UploadImg
from photo_tools_app.service.image_fix import FixImg
from photo_tools_app.service.image_scan import ScanImage

api = Redprint(name='fix')


@api.route('/restore', methods=["POST"])
@jwt_required
def ImageFix():
    parser = reqparse.RequestParser()
    parser.add_argument('imgFile', required=True, type=FileStorage, location='files', help="图片错误")
    parser.add_argument('openid', type=str, required=True, help="用户标识错误", location='form')
    entry = parser.parse_args(http_error_code=50003)

    openid = entry.get('openid')

    img_file = entry.get('imgFile')

    ios = img_file.stream.read()

    file_size = len(ios)
    convertFileSize = utils['common'].convertFileSize

    if file_size>=app.config['MAX_UPLOAD_IMG_SIZE']:
        return send(80012, data=CODE[80012]+", 请上传小于"+convertFileSize(app.config['MAX_UPLOAD_IMG_SIZE']))

    # 上传文件
    new_file_name, file_dir = UploadImg.createUploadPathAndFileName()
    sep = os.path.sep
    if img_file and allowedFile(img_file.filename):
        fname = utils['common'].secure_filename(img_file.filename)
        ext = fname.rsplit('.', 1)[1]
        new_filename = new_file_name + '.' + ext
        # 文件输入地址
        file_input_file_path = "{}{}{}{}input{}".format(file_dir, sep, new_file_name, sep, sep)
        if not os.path.exists(file_input_file_path):
            os.makedirs(file_input_file_path)
        try:
            with open(file_input_file_path+new_filename, 'wb') as f:
                f.write(ios)
        except Exception:
            return send(80005, data=CODE[80005])
        #文件输出地址
        file_output_dir_path = "{}{}{}{}output{}".format(file_dir, sep, new_file_name, sep, sep)
        if not os.path.exists(file_output_dir_path):
            os.makedirs(file_output_dir_path)
        #修复图片
        try:
            flag = FixImg.restoreOldPhotoByMicrosoft(new_file_name, ext, file_dir, file_input_file_path, file_output_dir_path)
            if not flag:
                return send(80011, data=CODE[80011])
        except Exception:
            return send(80011, data=CODE[80011])

        old_img = new_file_name + '_old.' + ext
        fixed_img = new_file_name + '_fixed.' + ext
        return send(200, data={"oldImg": old_img, "fixedImg": fixed_img})

    else:
        return send(80005, data=CODE[80005])



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
    new_file_name, file_dir = UploadImg.createUploadPathAndFileName()
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