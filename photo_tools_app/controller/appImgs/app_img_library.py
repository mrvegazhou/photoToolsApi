# -*- coding: utf-8 -*-
import sys
from concurrent.futures import ThreadPoolExecutor
from photo_tools_app.__init__ import send, reqparse, Redprint, CODE, utils, app
from photo_tools_app.utils.jwt_required import jwt_required
from core.extensions.text_handle.words_search.words_search import WordsSearch
from photo_tools_app.service.app_img_library import AppImgLibraryService


api = Redprint(name='search')
executor = ThreadPoolExecutor()

@api.route('/list', methods=["POST", "GET"])
# @jwt_required
def AppImgLibrary():
    parser = reqparse.RequestParser()
    parser.add_argument('tags', type=str, help="搜索内容", location='json')
    parser.add_argument('load_time', type=str, help="搜索时间戳", location='json')
    parser.add_argument('page', type=int, help="页码", default=1, location='json')
    entry = parser.parse_args(http_error_code=50003)

    tags = entry.get('tags')
    page = entry.get('page')
    load_time = entry.get('load_time')

    # 异步存入搜索日志表
    args = {
        'tags': tags,
        'user_id': g.uid or 0,
    }
    executor.submit(AppImgLibraryService.save_search_log, args)

    # 检查搜索词是否合法
    search = WordsSearch()
    search.set_keywords()
    for tag in tags.split():
        flag = search.contains_any(tag)
        if not flag:
            return send(30009, data=CODE[30009])

    list = AppImgLibraryService.get_app_imgs_list(page=page, tags=tags, load_time=load_time)
    return send(200, data={"list": list})