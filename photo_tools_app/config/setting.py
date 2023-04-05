# _*_ coding: utf-8 _*_

ALL_RP_API_LIST = {'appImgs.app_imgs': 'appImgs', 'wechat.auth': 'wechat', 'idCardPhoto.photo_manage': 'idCardPhoto', 'fixImage.image_fix': 'fixImage', 'static.pages': 'static'}
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
UPLOAD_FOLDER = "/Users/vega/workspace/codes/py_space/working/photo-tools-api/uploads"
MAX_CONTENT_LENGTH = 16 * 1000 * 1000
MAX_UPLOAD_IMG_SIZE = 50 * 1000 * 1000