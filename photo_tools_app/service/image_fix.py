# _*_ coding: utf-8 _*_

import os
import shutil
import sys, os, inspect
PACKAGE_PARENT = '../..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(inspect.getfile(inspect.currentframe())))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from ppgan.apps import DeOldifyPredictor
from photo_tools_app.__init__ import CORE_DIR, utils


class FixImg:

    @staticmethod
    def restoreOldPhoto(img):
        deoldify = DeOldifyPredictor(output='output', weight_path=CORE_DIR+"/extensions/paddleGan/models/DeOldify_stable.pdparams")
        result = deoldify.run_image(img)
        result.save("output/DeOldify/test.png")

    @staticmethod
    def restoreOldPhotoByMicrosoft(imgname, ext, save_path, inputs, outputs):
        common = utils['common']
        retval = os.getcwd()
        service_path = os.path.normpath(os.path.join(CORE_DIR, "../Bringing-Old-Photos-Back-to-Life"))
        os.chdir(service_path)
        str_cmd = "python run.py --input_folder {} --output_folder {} --GPU -1 --with_scratch --HR".format(inputs, outputs)
        common.run_cmd(str_cmd)
        os.chdir(retval)
        sep = os.path.sep
        final_path = "{}{}final_output{}".format(outputs, sep, sep)
        if os.path.isfile(final_path+imgname+".png"):
            f_src = os.path.join(final_path, imgname+".png")
            dst_path = "{}{}restored".format(save_path, sep)
            if not os.path.exists(dst_path):
                os.mkdir(dst_path)
            f_dst = os.path.join(dst_path, imgname+"_fixed.png")
            # 原图移动到restored文件夹内
            shutil.copyfile(os.path.join(inputs, imgname+"."+ext), os.path.join(dst_path, imgname+"_old."+ext))
            shutil.move(f_src, f_dst)
            shutil.rmtree(os.path.join(save_path, imgname))
            return True
        return False

    @staticmethod
    def inpaintingImg():
        pass

if __name__ == "__main__":
    import cv2, numpy as np

    image = cv2.imread('/Users/vega/workspace/codes/py_space/working/photo-tools-api/photo_tools_app/service/shuiyin.png')
    hue_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    low_range = np.array([140, 100, 90])
    high_range = np.array([185, 255, 255])
    mask = cv2.inRange(hue_image, low_range, high_range)

    kernel = np.ones((3, 3), np.uint8)
    dilate_img = cv2.dilate(mask, kernel, iterations=1)
    res = cv2.inpaint(image, dilate_img, 5, flags=cv2.INPAINT_TELEA)

    cv2.imshow('mask_img', mask)
    cv2.imshow('res', res)
    cv2.waitKey(0)
    cv2.destroyAllWindows()