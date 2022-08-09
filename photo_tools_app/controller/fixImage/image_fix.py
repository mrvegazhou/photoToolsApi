# -*- coding: utf-8 -*-

import os, math
from werkzeug.datastructures import FileStorage

from photo_tools_app.__init__ import send, reqparse, Redprint, CODE, utils, app, logger
from photo_tools_app.utils.common_util import allowedFile
from photo_tools_app.utils.jwt_required import jwt_required
from photo_tools_app.service.image_upload import UploadImg
from photo_tools_app.service.image_fix import FixImg



import time
import traceback
from functools import wraps

exception_dict = {
    "AssertionError": "断言语句（assert）失败",
    "AttributeError": "尝试访问未知的对象属性",
    "EOFError": "用户输入文件末尾标志EOF（Ctrl+d）",
    "FloatingPointError": "浮点计算错误",
    "GeneratorExit": "generator.close()方法被调用的时候",
    "ImportError": "导入模块失败的时候",
    "IndexError": "索引超出序列的范围",
    "KeyError": "字典中查找一个不存在的关键字",
    "KeyboardInterrupt": "用户输入中断键（Ctrl+c",
    "MemoryError": "内存溢出（可通过删除对象释放内存）",
    "NameError": "尝试访问一个不存在的变量",
    "NotImplementedError": "尚未实现的方法",
    "OSError": "操作系统产生的异常（例如打开一个不存在的文件）",
    "OverflowError": "数值运算超出最大限制",
    "ReferenceError": "弱引用（weak reference）试图访问一个已经被垃圾回收机制回收了的对象",
    "RuntimeError": "一般的运行时错误",
    "StopIteration": "迭代器没有更多的值",
    "SyntaxError": "Python的语法错误",
    "IndentationError": "缩进错误",
    "TabError": "Tab和空格混合使用",
    "SystemError": "Python编译器系统错误",
    "SystemExit": "Python编译器进程被关闭",
    "TypeError": "不同类型间的无效操作",
    "UnboundLocalError": "访问一个未初始化的本地变量（NameError的子类）",
    "UnicodeError": "Unicode相关的错误（ValueError的子类）",
    "UnicodeEncodeError": "Unicode编码时的错误（UnicodeError的子类）",
    "UnicodeDecodeError": "Unicode解码时的错误（UnicodeError的子类）",
    "UnicodeTranslateError": "Unicode转换时的错误（UnicodeError的子类）",
    "ValueError": "传入无效的参数",
    "ZeroDivisionError": "除数为零",
}
def check_exception_time(f):
    @wraps(f)
    def check(*args, **kwargs):
        try:
            # return f(*args, **kwargs)
            timestamp_start = float(time.time())
            res = f(*args, **kwargs)
            timestamp_end = float(time.time())
            cost_timestamp = timestamp_end - timestamp_start
            # cost_time = get_duration(cost_timestamp)
            logger.info("[%s]运行时间:[%s]秒" % (f.__name__, round(cost_timestamp, 2)))
            return res
        except Exception as e:
            # 以下是异常简要
            logger.info("未知异常简要：" + str(e))
            # 此处需要用到traceback模块捕获具体异常，以便展示具体的错误位置。以下是格式化后的具体异常
            exception_desc = "未知异常"
            for i in exception_dict:
                # print(i, exception_dict[i])
                if i in str(traceback.format_exc()):
                    exception_desc = "参考异常：" + exception_dict[i]
            logger.info("未知异常具体：" + str(traceback.format_exc()))
            # 以下字典格式不能http返回，所以需要转换成str,提前将traceback.format_exc()也转换成str，否则返回字符串没有引号
            res_data = {
                "code": 400,
                "message": exception_desc,
                "data": str(traceback.format_exc()),
            }
            print("未知异常具体：" + str(traceback.format_exc()), '======')
            return send(400, str(res_data))

    return check

api = Redprint(name='fix')


@api.route('/restore', methods=["POST"])
@jwt_required
@check_exception_time
def ImageFix():
    parser = reqparse.RequestParser()
    parser.add_argument('imgFile', required=True, type=FileStorage, location='files', help="图片错误")
    entry = parser.parse_args(http_error_code=50003)

    img_file = entry.get('imgFile')
    ios = img_file.stream.read()

    file_size = len(ios)
    convertFileSize = utils['common'].convertFileSize

    if file_size>=app.config['MAX_UPLOAD_IMG_SIZE']:
        return send(80012, data=CODE[80012]+", 请上传小于"+convertFileSize(app.config['MAX_UPLOAD_IMG_SIZE']))
    try:
        # 上传文件
        new_file_name, file_dir = UploadImg.createUploadPathAndFileName()
        sep = os.path.sep

        if img_file and allowedFile(img_file.filename):
            fname = utils['common'].secure_filename(img_file.filename)
            ext = fname.rsplit('.', 1)[1]
            new_filename = new_file_name + '.' + ext
            # 文件输入地址
            file_input_file_path = "{}{}{}{}input{}".format(file_dir, sep, new_file_name, sep, sep)
            if not os.path.exists(file_input_file_path):
                os.makedirs(file_input_file_path)
            try:
                with open(file_input_file_path+new_filename, 'wb') as f:
                    f.write(ios)
            except Exception:
                return send(80005, data=CODE[80005])
            #文件输出地址
            file_output_dir_path = "{}{}{}{}output{}".format(file_dir, sep, new_file_name, sep, sep)
            if not os.path.exists(file_output_dir_path):
                os.makedirs(file_output_dir_path)
            #修复图片
            try:
                flag = FixImg.restoreOldPhotoByMicrosoft(new_file_name, ext, file_dir, file_input_file_path, file_output_dir_path)
                if not flag:
                    return send(80011, data=CODE[80011])
            except Exception:
                return send(80011, data=CODE[80011])

            return send(200, data={})

        else:
            return send(80005, data=CODE[80005])
    except KeyboardInterrupt:
        print('---------------b-------------')
        raise
    finally:
        print('sss---------------b-------------s')