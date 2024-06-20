# coding: utf-8
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
    DATABASE = "stock"
    DB_URI = "{}+{}://{}:{}@{}:{}/{}".format(DIALCT, DRIVER, USERNAME, PASSWORD, HOST, PORT, DATABASE)
    SQLALCHEMY_DATABASE_URI = DB_URI
    # 连接池个数
    SQLALCHEMY_POOL_SIZE = 5
    # 超时时间，秒
    SQLALCHEMY_POOL_TIMEOUT = 30
    # 空连接回收时间，秒
    SQLALCHEMY_POOL_RECYCLE = 3600
    SQLALCHEMY_MAX_OVERFLOW = 5
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    '''
    Flask-SQLAlchemy有自己的事件通知系统，该系统在SQLAlchemy之上分层。为此，它跟踪对SQLAlchemy会话的修改。
    这会占用额外的资源，因此该选项SQLALCHEMY_TRACK_MODIFICATIONS允许你禁用修改跟踪系统。
    当前，该选项默认为True，但将来该默认值将更改为False，从而禁用事件系统。
    '''

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

    '''
    redis
    '''
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    REDIS_PASSWORD = ''
    REDIS_DB = 0
    REDIS_DEFAULT_TIMEOUT = 300
    REDIS_KEY_PREFIX = ''

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
