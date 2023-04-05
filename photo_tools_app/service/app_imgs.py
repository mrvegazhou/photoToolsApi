# _*_ coding: utf-8 _*_
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/photo-tools-api")

from photo_tools_app.model.app_imgs import AppImgs as AppImgsModel
from photo_tools_app.service.static_pages import StaticPages
from PIL import Image


class AppImgsService(object):
    @staticmethod
    def getAppImgsList(page=1, tags=None, url=None, type=None, load_time=None, begin_date=None, end_date=None):
        list = AppImgsModel.getAppImgs(page_num=page, tags=tags, url=url, type=type, load_time=load_time, begin_date=begin_date, end_date=end_date)
        for i, item in enumerate(list):
            res = StaticPages.getStaticPageUrl(item.url)
            img = Image.open(res[0])
            size = img.size
            item = dict(item)
            item.update({"width": size[0]})
            item.update({"height": size[1]})
            list[i] = item
        return list


if __name__ == "__main__":
    list = AppImgsService.getAppImgsList()
    print(list[0], '---')
    # print(StaticPages.getStaticPageUrl('3531e743a1de4217ab8395ee07bb518a.png'))