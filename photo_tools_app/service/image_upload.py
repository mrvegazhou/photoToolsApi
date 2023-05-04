# -*- coding: utf-8 -*-
import os, uuid
from photo_tools_app.__init__ import app
from photo_tools_app.utils.common_util import getUploadDirs


class UploadImg:

    @staticmethod
    def createUploadPathAndFileName():
        upload_dir = app.config['UPLOAD_FOLDER']
        new_file_name = uuid.uuid4().hex
        cur_sep = os.path.sep
        file_dir = getUploadDirs(new_file_name)
        file_dir = '{}{}{}{}{}'.format(upload_dir, cur_sep, file_dir[0], cur_sep, file_dir[1])
        # if not os.path.exists(file_dir):
        #     os.makedirs(file_dir)
        return new_file_name, file_dir, upload_dir
