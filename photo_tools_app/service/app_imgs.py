# _*_ coding: utf-8 _*_
import os
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/photo-tools-api")

from photo_tools_app.model.app_imgs import AppImgs as AppImgsModel
from photo_tools_app.service.image_upload import UploadImg
from photo_tools_app.service.static_pages import StaticPages
from PIL import Image
from io import BytesIO
import base64
import re


class AppImgsService(object):
    @staticmethod
    def get_app_imgs_list(page=1, tags=None, url=None, type=None, load_time=None, begin_date=None, end_date=None):
        list = AppImgsModel.get_app_imgs(page_num=page, tags=tags, url=url, type=type, load_time=load_time, begin_date=begin_date, end_date=end_date)
        for i, item in enumerate(list):
            res = StaticPages.getStaticPageUrl(item.url)
            img = Image.open(res[0])
            size = img.size
            item = dict(item)
            item.update({"width": size[0]})
            item.update({"height": size[1]})
            list[i] = item
        return list

    # 分页查询图片列表
    @staticmethod
    def get_app_imgs_list_by_page(page=1, tags=None, url=None, type=None, begin_date=None, end_date=None):
        list, total = AppImgsModel.get_app_imgs_by_page(page_num=page, tags=tags, url=url, type=type, begin_date=begin_date, end_date=end_date)
        for index, img in enumerate(list):
            list[index].type = AppImgsModel.get_type_name(list[index].type)
        return list, total

    @staticmethod
    def save_app_img_file_info(img, type='base64'):
        if not img:
            return False
        new_file_name, file_dir, _ = UploadImg.createUploadPathAndFileName()
        path = r"{}{}{}".format(file_dir, os.path.sep, new_file_name)  # 图片路径
        res = ''
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        if type=='base64':
            base64_data = re.sub('^data:image/.+;base64,', '', img)
            image_data = BytesIO(base64.b64decode(base64_data))
            new_img = Image.open(image_data)
            new_img.save(path + '.png', "PNG")
            res = new_file_name + '.png'
        elif type=='img':
            ext = img.rsplit('.', 1)[1]
            if not ext:
                return False
            new_img = Image.open(img)
            new_img.save(path + '.png', ext)
            res = new_file_name + '.' + ext
        return res, file_dir

    @staticmethod
    def save_app_imgs(imgs):
        if len(imgs)==0:
            return
        return AppImgsModel.batch_save_imgs(imgs)

    @staticmethod
    def update_app_img(uuid, url=None, tags=None, type=0, base_dir=None):
        if not uuid:
            return False
        return AppImgsModel.update_app_img(uuid, url=url, tags=tags, type=type, base_dir=base_dir)

    @staticmethod
    def del_app_img(uuid):
        if not uuid:
            return False
        return AppImgsModel.del_app_img(uuid)


if __name__ == "__main__":
    import threading, time


    class Boss(threading.Thread):
        def run(self):
            print("BOSS：今晚大家都要加班。")
            event.set()
            time.sleep(5)
            print("BOSS：可以下班了。")
            event.set()


    class Worker(threading.Thread):
        def run(self):
            event.wait()
            print("Worker：哎……命苦啊！")
            time.sleep(0.25)
            event.clear()
            event.wait()
            print("Worker：Yeah!")


    event = threading.Event()
    threads = []
    for i in range(5):
        threads.append(Worker())
    threads.append(Boss())
    for t in threads:
        t.start()
    for t in threads:
        t.join()