# coding: utf-8

import numpy as np
import hashlib
from PIL import Image


def check_img_by_MD5_hash(img1, img2):
    img_data1 = np.array(Image.open(img1))
    img_data2 = np.array(Image.open(img2))
    imgMD51 = hashlib.md5(img_data1).hexdigest()
    imgMD52 = hashlib.md5(img_data2).hexdigest()
    if imgMD51 == imgMD52:
        return True
    else:
        return False