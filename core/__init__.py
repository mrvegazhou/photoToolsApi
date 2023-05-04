# -*- coding: utf-8 -*-
import os, sys, socket
import atexit, fcntl
from flask_cors import CORS  # 添加CORS组件 允许跨域访问
from flask import Flask, request, make_response, send_from_directory, current_app, g, jsonify, Blueprint
from .config.sys_config import config
from flask.helpers import get_debug_flag
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import load_only
from sqlalchemy.sql import func
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .log.logger import Logger
from .utils import common, date_utils, auth_token, image_utils
from .http.response import send, sendWithHeader, CODE
from .http import reqparse
from .exception.api_exception import APIException
from .config import constant

from .extensions.redprint import Redprint, RedprintAssigner
from .extensions.api_docs.redprint import RedprintWithDoc
from .extensions.schedules import scheduler


ENV = config['env']
WEB_IP = config[ENV].WEB_IP
WEB_PORT = config[ENV].WEB_PORT
app = Flask(__name__)
# 初始化session 会话  需要配置key
app.secret_key = '\xc3\xc0\xc0\xf6\xc8\xcb\xc9\xfa'
# 实例化 cors
CORS(app, resources={r"/*": {"origins": "*"}})

app.config.from_object(config[ENV])

# 日志
core_logger = Logger(app, log_name="photo_app_core")

# os.environ["FLASK_DEBUG"] = app.config.get('DEBUG', '0')

if app.config.get('USE_REDISLOCK_SCHEDULE', False):
    scheduler.start()  # 启动任务列表
    atexit.register(lambda: scheduler.shutdown())
else:
    f = open("scheduler.lock", "wb")
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except Exception as e:
        print('已启动一个任务计划进程...', str(e))
        app.logger.info("已启动一个任务计划进程！")
    else:
        # 初始化定时器
        # scheduler.init_app(app)
        # 启动定时器，默认后台启动了
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())

        def unlock(f):
            print('解锁....')
            fcntl.flock(f, fcntl.LOCK_UN)
            f.close()
            try:
                os.unlink("scheduler.lock")
            except Exception as e:
                print('unlock:', str(e))
        atexit.register(unlock, f)

# 限速
limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri="memory://",
)
# 数据库
db = SQLAlchemy(app)

utils = {
    "common": common,
    "date": date_utils,
    "auth": auth_token,
    "image": image_utils
}

# 其他组件注册
request = request
make_response = make_response
send_from_directory = send_from_directory
g = g
Blueprint = Blueprint
RedprintAssigner = RedprintAssigner
Redprint = Redprint
RedprintWithDoc = RedprintWithDoc

# 当前目录
CORE_DIR = os.path.split(os.path.abspath(__file__))[0]  # 当前目录


