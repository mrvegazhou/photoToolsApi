# -*- coding: utf-8 -*-

from stock_app.__init__ import app, send, reqparse, ak, limiter, finance

parser = reqparse.RequestParser()


@finance.route('/negative_include_positive', methods=['GET'])
def negative_include_positive():
    parser.add_argument('code')
