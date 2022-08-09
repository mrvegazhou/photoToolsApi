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
            'gif': 'image/gif'
        }

    @staticmethod
    def getStaticPageUrl(fileName):
        cur_sep = os.path.sep
        upload_dir = app.config['UPLOAD_FOLDER']
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
        dir1, dir2 = getUploadDirs(name)
        imgPath = '{}{}{}{}{}{}{}'.format(upload_dir, cur_sep, dir1, cur_sep, dir2, cur_sep, fileName)
        return imgPath, name, ext

