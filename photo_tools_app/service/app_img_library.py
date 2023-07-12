# _*_ coding: utf-8 _*_
from photo_tools_app.model.app_img_library import AppImgLibrary as AppImgLibraryModel
from photo_tools_app.model.app_search_log import AppSearchLog as AppSearchLogModel
from photo_tools_app.service.static_pages import StaticPages
from photo_tools_app.exception.api_exception import ImgLibParamError
from PIL import Image


class AppImgLibraryService(object):
    @staticmethod
    def get_app_imgs_list(page=1, tags=None, url=None, note=None, load_time=None, begin_date=None, end_date=None):
        list = AppImgLibraryModel.get_app_imgs(page_num=page, tags=tags, url=url, note=note, load_time=load_time, begin_date=begin_date, end_date=end_date)
        for i, item in enumerate(list):
            res = StaticPages.getStaticPageUrl(item.url)
            img = Image.open(res[0])
            size = img.size
            item = dict(item)
            item.update({"width": size[0]})
            item.update({"height": size[1]})
            list[i] = item
        return list

    @staticmethod
    def save_search_log(tags, user_id):
        model = AppSearchLogModel()
        model.content = tags
        model.user_id = user_id
        AppImgLibraryModel.save(model)

    @staticmethod
    def get_app_img_lib_list_by_page(page_num=None, tags=None, url=None, note=None, begin_date=None, end_date=None):
        lists, total = AppImgLibraryModel.get_app_imgs_by_page(page_num=page_num, tags=tags, url=url, note=note, begin_date=begin_date, end_date=end_date)
        return lists, total

    @staticmethod
    def update_app_img_lib(uuid=None, tags=None, url=None, note=None):
        if not uuid:
            raise ImgLibParamError()
        if not tags and not url and not note:
            raise ImgLibParamError()
        return AppImgLibraryModel.update_app_img_lib(uuid=uuid, tags=tags, url=url, note=note)

    @staticmethod
    def del_app_img_lib(uuid=None):
        if not uuid:
            raise ImgLibParamError()
        return AppImgLibraryModel.del_app_img_lib(uuid)
