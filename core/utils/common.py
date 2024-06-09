# coding: utf-8
"""
系统工具方法集
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from subprocess import call
import os
import sys
import json
import re
import decimal
import string
import hmac
import base64
import hashlib
import uuid
import time
import traceback
import random
import math
from datetime import date, datetime, time as d_time
from dateutil.relativedelta import relativedelta
from hashlib import sha512
from random import choice
from sqlalchemy.ext.declarative import DeclarativeMeta
import unicodedata

from flask import request


def is_blank(var):
    return not (var and var.strip())


def is_email(var):
    if var is None:
        return False
    regexp = r"^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"
    return re.search(regexp, str(var))


def is_url(var):
    if var is None:
        return False
    regexp = r"^((ht|f)tps?):\/\/[\w\-]+(\.[\w\-]+)+([\w\-\.,@?^=%&:\/~\+#]*[\w\-\@?^=%&\/~\+#])?$"
    return re.search(regexp, str(var))


def is_phone(var):
    if var is None:
        return False
    regexp = r"^(0[0-9]{2,3}\-?)?([2-9][0-9]{6,7})+(\-[0-9]{1,4})?$"
    return re.search(regexp, str(var))


def is_mobile(var):
    if var is None:
        return False
    return is_mobile_cn(var) or is_mobile_hk(var) or is_mobile_mo(var) or is_mobile_tw(var)


def is_mobile_cn(var):
    if var is None:
        return False
    regexp = r"^1\d{10}$"
    return re.search(regexp, str(var))


def is_mobile_hk(var):
    if var is None:
        return False
    regexp = r"^(6|9)\d{7}$"
    return re.search(regexp, str(var))


def is_mobile_mo(var):
    if var is None:
        return False
    regexp = r"^6\d{6}$"
    return re.search(regexp, str(var))


def is_mobile_tw(var):
    if var is None:
        return False
    regexp = r"^9\d{8}$"
    return re.search(regexp, str(var))


def is_date(var):
    if var is None:
        return False
    regexp = r"^(1\d{3}|2\d{3})[-/.]{1}(0?\d|1[0-2]{1})[-/.]{1}(0?\d|[12]{1}\d|3[01]{1})$"
    if re.search(regexp, str(var)):
        try:
            return datetime.strptime(re.sub(r'[/.]', '-', str(var)), '%Y-%m-%d')
        except ValueError:    # 防止出现2018.06.31这种错误
            return False
    else:
        return False


def is_time(var):
    if var is None:
        return False
    regexp = r"^(0?\d|1\d|2[0-3]{1})[:-]{1}(0?\d|[1-5]{1}\d)[:-]{1}(0?\d|[1-5]{1}\d)$"
    return re.search(regexp, str(var))


def is_datetime(var):
    if var is None:
        return False
    try:
        d, t = var.split(" ")
    except ValueError:
        return False
    return is_date(d) and is_time(t)


def is_password(var):
    if var is None:
        return False
    regexp = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*?[^A-Za-z0-9])(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,18}$'
    return re.search(regexp, str(var))

def thousands_separator(num):
    return num.replace(r'/\B(?=(?:\d{3})+(?!\d))/g', ",")

def is_sms_code(var):
    if var is None:
        return False
    regexp = r"^[a-zA-Z0-9]{6}$"
    return re.search(regexp, str(var))

def get_error_info():
    """输出最近一个错误栈的file, line, func, code"""
    error_info = traceback.format_exception(*sys.exc_info(), -1)[1]
    error_reg = re.compile(r'File\s*"([^"].*)",\s*line\s*([^,].*),\s*in\s*([^\n].*)\s*\n\s*([^\n].*)\s*\n', re.S | re.M)
    error_field = error_reg.findall(error_info)
    return error_field[0] if error_field else ("", "", "", "")


def get_datetime(now=None, year=0, month=0, week=0, day=0, hour=0, minute=0, second=0):
    if now is None:
        now = datetime.now()
    res = now + relativedelta(years=int(year), months=int(month), weeks=int(week), days=int(day), hours=int(hour), minutes=int(minute), seconds=int(second))
    return res


def get_timestamp(now=None, year=0, month=0, week=0, day=0, hour=0, minute=0, second=0):
    dt = get_datetime(now, year, month, week, day, hour, minute, second)
    return int(time.mktime(dt.timetuple()))


def get_param_sign(**kwargs):
    """根据传入的参数，排序后生成md5值"""
    s = '&'.join(['{0}={1}'.format(k, v) for k, v in sorted(kwargs.items(), key=lambda x: x[0])])
    return md5(s)


def get_remote_addr():
    """获取客户端IP地址"""
    address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if address is not None:
        address = address.encode('utf-8').split(b',')[0].strip()
    return address.decode()


def get_client_ident(var=None):
    """获取客户端标识"""
    user_agent = request.headers.get('User-Agent')
    if user_agent is not None:
        user_agent = user_agent.encode('utf-8')
    if var is None or var == "":
        base = str(user_agent)
    else:
        base = '{0}|{1}'.format(var, user_agent)
    h = sha512()
    h.update(base.encode('utf8'))
    return h.hexdigest()


def get_age(born, today=None):
    """计算年龄"""
    if isinstance(born, datetime):
        born = born.date()
    elif isinstance(born, date):
        pass
    else:
        return 0

    if isinstance(today, datetime):
        today = today.date()
    elif isinstance(today, date):
        pass
    else:
        today = date.today()

    try:
        birthday = born.replace(year=today.year)
    except ValueError:      # 防止非闰年的2月29
        birthday = born.replace(year=today.year, day=born.day-1)
    if birthday > today:
        return today.year - born.year - 1
    else:
        return today.year - born.year


def get_max_hr(sex, age):
    """计算最大心率"""
    if not sex or re.search(r"^\d$", str(sex)) is None:
        sex = 1
    if not age or re.search(r"^\d+$", str(age)) is None:
        age = 25
    if int(sex) == 1:
        max_hr = 220
    else:
        max_hr = 224
    return max_hr - int(age)


def create_uuid_str():
    """生成UUID字符串"""
    return str(uuid.uuid1()).replace('-', '')


def create_random_str(length=6, chars=string.ascii_letters + string.digits):
    """生成随机字符"""
    return ''.join([choice(chars) for _ in range(length)])


def create_random_num(length=6):
    """生成随机数字"""
    return create_random_str(length, chars=string.digits)


def hmacb64(obj_str, secret, alg='sha1'):
    """对字符串进行hmac"""
    if alg == 'sha1':
        alg = hashlib.sha1
    h = hmac.new(secret.encode(), obj_str.encode(), alg)
    return base64.b64encode(h.digest()).decode()


def md5(obj_str):
    """对字符串进行md5"""
    s = obj_str.encode("utf-8")
    m = hashlib.md5(s)
    # m.update(obj_str.encode())
    return m.hexdigest()


def datediff(var1, var2):
    """比较两个日期差, 日期格式必须是%Y-%m-%d格式的date字符串"""
    # noinspection PyBroadException
    try:
        date1 = datetime.strptime(var1, "%Y-%m-%d")
        date2 = datetime.strptime(var2, "%Y-%m-%d")
    except Exception:
        return 0
    return (date1-date2).days


def datetimediff(var1, var2):
    """比较两个时间差, 日期格式必须是%Y-%m-%d %H:%M:%S格式的datetime字符串"""
    # noinspection PyBroadException
    try:
        datetime1 = datetime.strptime(var1, "%Y-%m-%d %H:%M:%S")
        datetime2 = datetime.strptime(var2, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return 0
    return int((datetime1-datetime2).total_seconds())


def db_to_dict(inst, cls):
    """数据库对象转换为字典"""
    d = dict()
    for c in cls.__table__.columns:
        name = c.name
        v = getattr(inst, name)
        if v is None:
            d[name] = str()
        else:
            if isinstance(v, datetime):
                d[name] = v.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(v, date):
                d[name] = v.strftime('%Y-%m-%d')
            elif isinstance(v, decimal.Decimal):
                d[name] = float(v)
            else:
                d[name] = v
    return d


# 生成随机字符串
def gen_random_str(num):
    return ''.join(str(i) for i in random.sample('zyxwvutsrqponmlkjihgfedcba1234567890', num))


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, d_time):
            return obj.strftime('%H:%M:%S')
        elif isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            try:
                return obj.get_keys()
            except TypeError:
                return None
        else:
            return json.JSONEncoder.default(self, obj)


def pagination(current_page, page_size, total):
    '''
    :param current_page: 当前页码
    :param page_size: 页大小
    :param total: 查询总数
    :return: start起始位置 end终止位置
    '''
    try:
        current_page = int(current_page)
    except Exception as e:
        current_page = 1

    if not current_page:
        current_page = 1
    if not page_size:
        page_size = total

    current_page = int(current_page)
    page_size = int(page_size)
    total = int(total)

    if total == 0:
        return 0, 0, 0

    max_page_num = math.ceil(total / page_size)

    if current_page >= max_page_num:
        current_page = max_page_num

    start = (current_page - 1) * page_size
    end = page_size * current_page

    if current_page == max_page_num:
        end = total

    return start, end, max_page_num


# 判断是否为数字
def is_num(value):
    try:
        x = int(value)
    except TypeError:
        return False
    except ValueError:
        return False
    except Exception:
        return False
    else:
        return True

# 判断是否为中文
def is_chinese(s):
    for char in s:
        if not '\u4e00' <= char <= '\u9fff':
            return False
    return True

_windows_device_files = (
    "CON",
    "AUX",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "LPT1",
    "LPT2",
    "LPT3",
    "PRN",
    "NUL",
)
def secure_filename(filename: str) -> str:
    r"""Pass it a filename and it will return a secure version of it.  This
    filename can then safely be stored on a regular file system and passed
    to :func:`os.path.join`.  The filename returned is an ASCII only string
    for maximum portability.

    On windows systems the function also makes sure that the file is not
    named after one of the special device files.

    >>> secure_filename("My cool movie.mov")
    'My_cool_movie.mov'
    >>> secure_filename("../../../etc/passwd")
    'etc_passwd'
    >>> secure_filename('i contain cool \xfcml\xe4uts.txt')
    'i_contain_cool_umlauts.txt'

    The function might return an empty filename.  It's your responsibility
    to ensure that the filename is unique and that you abort or
    generate a random filename if the function returned an empty one.

    .. versionadded:: 0.5

    :param filename: the filename to secure
    """
    filename = unicodedata.normalize("NFKD", filename)
    filename = filename.encode("utf8", "ignore").decode("utf8")  # 编码格式改变

    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")
    _filename_ascii_add_strip_re = re.compile(r'[^A-Za-z0-9_\u4E00-\u9FBF\u3040-\u30FF\u31F0-\u31FF.-]')
    filename = str(_filename_ascii_add_strip_re.sub('', '_'.join(filename.split()))).strip('._')  # 添加新规则

    # on nt a couple of special files are present in each folder.  We
    # have to ensure that the target file is not such a filename.  In
    # this case we prepend an underline
    if (
            os.name == "nt"
            and filename
            and filename.split(".")[0].upper() in _windows_device_files
    ):
        filename = f"_{filename}"

    return filename


# 字节转文件大小单位
def convertFileSize(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])


def run_cmd(command):
    try:
        return call(command, shell=True)
    except KeyboardInterrupt:
            raise Exception("Process interrupted")


# 检查目录剩余存储空间
def get_free_space_mb(folder):
    st = os.statvfs(folder)
    return st.f_bavail * st.f_frsize / 1024 // 1024
