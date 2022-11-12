# coding: utf-8
from sqlalchemy.pool import QueuePool

class Config:
    '''
    database_setting
    '''

    DIALCT = "postgresql"
    DRIVER = "psycopg2"
    USERNAME = "postgres"
    PASSWORD = "root"
    HOST = "127.0.0.1"
    PORT = "5432"
    DATABASE = "app_tool_db"
    DB_URI = "{}+{}://{}:{}@{}:{}/{}".format(DIALCT, DRIVER, USERNAME, PASSWORD, HOST, PORT, DATABASE)
    SQLALCHEMY_DATABASE_URI = DB_URI
    SQLALCHEMY_ENGINE_OPTIONS = {
        'poolclass': QueuePool,
        'max_overflow': 5,   # 超过连接池大小外最多可创建的连接
        'pool_size': 20,  # 连接池大小
        'pool_timeout': 5,  # 池满后，线程的最多等待连接的时间，否则报错
        'pool_recycle': 1200,  # 多久之后对线程池中的线程进行一次连接的回收（重置）—— -1 永不回收
        'pool_pre_ping': True,
    }
    # Flask - SQLAlchemy有自己的事件通知系统，该系统在SQLAlchemy之上分层。为此，它跟踪对SQLAlchemy会话的修改。
    # 这会占用额外的资源，因此该选项SQLALCHEMY_TRACK_MODIFICATIONS允许你禁用修改跟踪系统。
    # 当前，该选项默认为True，但将来该默认值将更改为False，从而禁用事件系统。
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    '''
    WEB SETTINT
    '''
    WEB_IP = 'localhost'
    WEB_PORT = '5000'
    # 字符串编码格式
    STRING_CODE = 'utf-8'
    # 加密方式名
    ENCRYPTION_SHA1 = 'sha1'
    # token过期时间配置(默认一周 604800/测试的时候5分钟)
    TOKEN_EXPIRE = 604800

    '''
    db-select-habit
    '''

    USER_SALT_LENGTH = 4
    PAGE_LIMIT = 10
    DEFAULT_PAGE = 1


class DevConfig(Config):
    ENV = "development"


class ProdConfig(Config):
    ENV = "product"

global_env = 'dev'

config = {
    "env": global_env,
    "dev": DevConfig,
    "prod": ProdConfig
}
