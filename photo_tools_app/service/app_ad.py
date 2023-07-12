# _*_ coding: utf-8 _*_
from photo_tools_app.model.app_ad import AppAd as AppAdModel
from photo_tools_app.exception.api_exception import AdUrlIsNull, AdContentIsNull, AdTpyeIsNull

class AppAdService(object):
    @staticmethod
    def get_ad_list_by_page(page_num=1, content=None, url=None, type=None, begin_date=None, end_date=None):
        ad_list, total = AppAdModel.get_app_ads_by_page(page_num=page_num,  content=content, url=url, type=type, begin_date=begin_date, end_date=end_date)
        return ad_list, total

    @staticmethod
    def get_ad_list_by_type(type=None):
        if not type:
            return None
        return AppAdModel.get_app_ads_by_type(type)

    @staticmethod
    def del_ad_by_id(uuid):
        if not uuid:
            return None
        return AppAdModel.del_ad(uuid)

    @staticmethod
    def save_ad(type, content, url):
        if not type:
            raise AdTpyeIsNull()
        if not content:
            raise AdContentIsNull()
        if not url:
            raise AdUrlIsNull()
        ad_model = AppAdModel()
        ad_model.type = type
        ad_model.content = content
        ad_model.url = url
        return AppAdModel.save(ad_model)

