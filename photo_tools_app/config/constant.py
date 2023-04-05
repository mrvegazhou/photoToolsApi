# _*_ coding: utf-8 _*_

from enum import Enum, unique

@unique
class Constant(Enum):
    # 微信·小程序
    APP_ID = 'wx69d35100ccbd246e'
    APP_SECRET = 'df6525f0b0ee9d2725f4f8295a1bc7d1'
    WX_LOGIN = 'https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code'

    JWT_SALT = 'iv%i6xo7l8_t9bf_u!8#g#m*)*+ej@bek6)(@u3kh*42+unjv='

    # 百度aip账号
    # BAIDU_APP_ID = '26564867'
    # BAIDU_API_KEY = 'ZAh9Ew3qAjipe2qiYemUxkAs'
    # BAIDU_SECRET_KEY = 'st02M1wsUk9GvsM1tsrEWzrcZPYpUb1R'
    BAIDU_APP_ID = '25673679'
    BAIDU_API_KEY = 'lTKy64EI8jDwPzyXlPmZttTZ'
    BAIDU_SECRET_KEY = '4soBMzSFClAQG5LwYxTH56TDhiPzIEwf'

    PAGE_SIZE = 10


