# -*- coding: utf-8 -*-
import os
from photo_tools_app.__init__ import app
from photo_tools_app.utils.common_util import getUploadDirs


class StaticPages(object):

    @staticmethod
    def getImgTypes():
        return {
            'jpeg': 'image/jpeg',
            'jpg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }

    @staticmethod
    def getFontTypes():
        return {
            'ttf': 'font/truetype',
            'otf': 'font/opentype',
            'woff': 'application/font-woff',
            'woff2': 'application/font-woff2'
        }

    @staticmethod
    def getStaticPageUrl(fileName):
        cur_sep = os.path.sep
        upload_dir = "/Users/vega/workspace/codes/py_space/working/photo-tools-api/uploads" #app.config['UPLOAD_FOLDER']
        name, ext = fileName.rsplit('.', 1)
        if "_rgba" in name: # 抠图
            name = fileName.rsplit('_rgba', 1)[0]
            fileName = '{}{}{}_rgba.png'.format('matting', cur_sep, name)
        elif "_c" in name: # 寸照合成
            name = fileName.rsplit('_c', 1)[0]
            fileName = '{}{}{}_c.png'.format('compose', cur_sep, name)
        elif "_fixed" in name: # 图片修复
            name = fileName.rsplit('_fixed', 1)[0]
            fileName = '{}{}{}_fixed.png'.format('restored', cur_sep, name)
        elif "_old" in name: # 图片修复
            name = fileName.rsplit('_old', 1)[0]
            fileName = '{}{}{}_old.{}'.format('restored', cur_sep, name, ext)
        elif "_s" in name: # 扫描后的图片
            name = fileName.rsplit('_s', 1)[0]
            fileName = '{}{}{}_s.{}'.format('scan', cur_sep, name, ext)

        dir1, dir2 = getUploadDirs(name)
        imgPath = '{}{}{}{}{}{}{}'.format(upload_dir, cur_sep, dir1, cur_sep, dir2, cur_sep, fileName)
        # 文件的全路径,  文件名, 后缀名
        return imgPath, name, ext

    @staticmethod
    def getStaticFile(fileName, type=''):
        if not type:
            type = 'wechat'
        cur_sep = os.path.sep
        upload_dir = app.config['UPLOAD_FOLDER']
        img_path = '{}{}static{}{}{}{}'.format(upload_dir, cur_sep, cur_sep, type, cur_sep, fileName)
        return img_path

    @staticmethod
    def get_static_img_url_by_file_path(file_path):
        if not file_path:
            return None
        file_path_arr = file_path.rsplit('/', 1)
        if len(file_path_arr)>1:
            return file_path_arr[1]
        else:
            return None