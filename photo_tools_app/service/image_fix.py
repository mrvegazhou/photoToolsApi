# _*_ coding: utf-8 _*_

import os
import shutil

from ppgan.apps import DeOldifyPredictor
from photo_tools_app.__init__ import CORE_DIR, utils

class ImageFix:

    @staticmethod
    def createNewPhoto(img):
        deoldify = DeOldifyPredictor(output='output', weight_path=CORE_DIR+"/extensions/paddleGan/models/DeOldify_stable.pdparams")
        result = deoldify.run_image(img)
        result.save("output/DeOldify/test.png")

    @staticmethod
    def createNewPhotoByMicrosoft(imgname, inputs, outputs):
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
            f_src = os.path.join(final_path, imgname+"_fixed.png")
            os.rename(os.path.join(final_path, imgname+".png"), f_src)
            dst_path = "{}{}restored".format(inputs, sep)
            if not os.path.exists(dst_path):
                os.mkdir(dst_path)
            f_dst = os.path.join(dst_path, imgname+"_fixed.png")
            shutil.move(f_src, f_dst)
            shutil.rmtree(outputs)
            return True
        return False

if __name__ == "__main__":

    # run_cmd("python run.py --input_folder inputs  --output_folder results  --GPU -1 --with_scratch --HR")
    # print(os.listdir('/Users/vega/workspace/codes/py_space/working/photo-tools-api/uploads/inputs'))
    ImageFix.createNewPhotoByMicrosoft('oldsss', '/Users/vega/workspace/codes/py_space/working/photo-tools-api/uploads/inputs', '/Users/vega/workspace/codes/py_space/working/photo-tools-api/uploads/outputs')