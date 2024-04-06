# -*- coding: utf-8 -*-
import subprocess
from flask_cors import CORS  # 添加CORS组件 允许跨域访问
from flask import Flask, request, make_response, send_from_directory, current_app, g, jsonify, Blueprint
from .config.sys_config import config

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

from flask_apscheduler import APScheduler
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .log.logger import Logger
from .utils import common, date_utils, auth_token
from .http.response import send, CODE
from .http import reqparse
from .exception.api_exception import APIException
from .config import constant

ENV = config['env']
WEB_IP = config[ENV].WEB_IP
WEB_PORT = config[ENV].WEB_PORT
app = Flask(__name__)
# 初始化session 会话  需要配置key
app.secret_key = '\xc3\xc0\xc0\xf6\xc8\xcb\xc9\xfa'
# 实例化 cors
CORS(app, resources={r"/*": {"origins": "*"}})

app.config.from_object(config[ENV])
# 定时任务
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
# 限速
limiter = Limiter(
    app,
    # key_func=get_remote_address
)
# 数据库
db = SQLAlchemy(app)
# 日志
logger = Logger()
logger.init_app(app)

utils = {
    "common": common,
    "date": date_utils,
    "auth": auth_token
}

# 其他组件注册
request = request
make_response = make_response
send_from_directory = send_from_directory
g = g

from .cache import RedisCache as Cache
cache = Cache()

# admin = Blueprint('admin', 'admin')
# finance = Blueprint('finance', 'finance')

