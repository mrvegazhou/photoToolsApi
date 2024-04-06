# -*- coding: utf-8 -*-
from __init__ import app, WEB_IP, WEB_PORT
from controller.stock import finance

if __name__ == "__main__":

    app.register_blueprint(finance, url_prefix='/finance')

    if WEB_IP == 'localhost':
        # 本地调试
        app.run(host='0.0.0.0', port=WEB_PORT, debug=False, threaded=True)
        # app.run()
        # ssl_context = (
        #    './server.crt',
        #    './server_nopwd.key')
    else:
        from werkzeug.contrib.fixers import ProxyFix

        # 线上服务部署  对接gunicorn
        app.wsgi_app = ProxyFix(app.wsgi_app)
