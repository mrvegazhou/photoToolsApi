# _*_ coding: utf-8 _*_
import subprocess
import shutil
import sys, os, inspect
PACKAGE_PARENT = '../..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(inspect.getfile(inspect.currentframe())))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from ppgan.apps import DeOldifyPredictor
from photo_tools_app.__init__ import CORE_DIR, utils


class FixImgService:

    @staticmethod
    def restore_old_photo(img):
        deoldify = DeOldifyPredictor(output='output', weight_path=CORE_DIR+"/extensions/paddleGan/models/DeOldify_stable.pdparams")
        result = deoldify.run_image(img)
        result.save("output/DeOldify/test.png")

    @staticmethod
    def restore_old_photo_by_microsoft(imgname, ext, save_path, inputs, outputs):
        # common = utils['common']
        retval = os.getcwd()
        service_path = os.path.normpath(os.path.join(CORE_DIR, "../Bringing-Old-Photos-Back-to-Life"))
        os.chdir(service_path)
        args = ['python', 'run.py', '--input_folder', inputs, '--output_folder', outputs, '--GPU', '-1', '--with_scratch', '--HR']
        # str_cmd = "python run.py --input_folder {} --output_folder {} --GPU -1 --with_scratch --HR".format(inputs, outputs)
        # common.run_cmd(str_cmd)
        proc = subprocess.Popen(
            args,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # print("poll: %s" % proc.poll())
        # result = [x.decode("utf8").strip() for x in proc.stdout.readlines()]
        # print(result)
        while proc.poll() is None:
            continue
        # out, err = proc.communicate()
        # print(out.decode())
        os.chdir(retval)
        sep = os.path.sep
        final_path = "{}final_output{}".format(outputs, sep)
        if os.path.isfile(final_path+imgname+".png"):
            f_src = os.path.join(final_path, imgname+".png")
            dst_path = "{}{}restored".format(save_path, sep)
            if not os.path.exists(dst_path):
                os.mkdir(dst_path)
            f_dst = os.path.join(dst_path, imgname+"_fixed.png")
            # 原图移动到restored文件夹内
            shutil.copyfile(os.path.join(inputs, imgname+"."+ext), os.path.join(dst_path, imgname+"_old."+ext))
            shutil.move(f_src, f_dst)
            # input和output文件夹都存在 upload / 文件名命名的目录 / (input/output) / (final_output/ )
            shutil.rmtree(os.path.join(save_path, imgname))
            return True
        return False


if __name__ == "__main__":
    import cv2, numpy as np

    image = '/Users/vega/workspace/codes/py_space/working/photo-tools-api/photo_tools_app/service/shuiyin.png'
    image2 = '/Users/vega/workspace/codes/py_space/working/photo-tools-api/photo_tools_app/service/rrrr.png'