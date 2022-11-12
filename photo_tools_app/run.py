# -*- coding: utf-8 -*-
from werkzeug.routing import BaseConverter
from __init__ import app, WEB_IP, WEB_PORT, RedprintAssigner
from photo_tools_app.utils.jwt_required import jwt_wx_authentication

APP_NAME = 'photo_tools_app'

def load_config():
    app.config.from_object('{}.{}.{}'.format(APP_NAME, 'config', 'setting'))

def register_blueprint():
    app.config.from_object('{}.{}.{}'.format(APP_NAME, 'config', 'swagger'))
    assigner = RedprintAssigner(app=app, rp_api_list=app.config['ALL_RP_API_LIST'], api_path='{}.{}'.format(APP_NAME, 'controller'))

    # 将红图的每个api的tag注入SWAGGER_TAGS中
    # @assigner.handle_rp
    # def handle_swagger_tag(api):
    #     app.config['SWAGGER_TAGS'].append(api.tag)

    bp_list = assigner.create_bp_list()
    for url_prefix, bp in bp_list:
        app.register_blueprint(bp, url_prefix=url_prefix)


app.before_request(jwt_wx_authentication)

# 跨域支持
def after_request(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
app.after_request(after_request)

#限制文件上传大小
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# 正则匹配路由
class staticFileConverter(BaseConverter):
    def __init__(self, url_map):
        super().__init__(url_map)
        self.regex = r'[0-9A-Za-z]{1,32}(_rgba|_c|_fixed|_old|_s)?\.(png|jpe?g|gif|svg)'
app.url_map.converters["staticFile"] = staticFileConverter

if __name__ == "__main__":
    load_config()
    register_blueprint()

    if WEB_IP == 'localhost':
        # 本地调试
        app.run(host='0.0.0.0', port=WEB_PORT, threaded=True, debug=True)
        # app.run()
        # ssl_context = (
        #    './server.crt',
        #    './server_nopwd.key')
    else:
        from werkzeug.middleware.proxy_fix import ProxyFix

        # 线上服务部署  对接gunicorn
        app.wsgi_app = ProxyFix(app.wsgi_app)
