# -*- coding: utf-8 -*-

from stock_app.__init__ import app, send, reqparse, ak, limiter, finance
# from stock_app.service import stock

parser = reqparse.RequestParser()


@finance.route('/check_stock', methods=['GET'])
def check_stock():
    parser.add_argument('rate', type=int, help='Rate cannot be converted')
    parser.add_argument('name')
    args = parser.parse_args(http_error_code=50003)
    return send(10000, data="sss")


@finance.route('/stock/<string:code>/<string:start_date>/<string:ending_date>', methods=['GET'])
@limiter.limit("1/second", override_defaults=False)
def get_stock_info(code, start_date, ending_date):
    result = {}
    stocks = []
    result['stockId'] = code
    # 后复权历史行情数据
    try:
        df = ak.stock_zh_a_daily(symbol=code, start_date=start_date, end_date=ending_date, adjust="hfq")
    except Exception:
        df = ak.stock_zh_a_daily(symbol=code, start_date=start_date, end_date=ending_date)
    print(df)
    # stocks.sort(key=lambda x: x['time'])
    result['trendData'] = stocks

    return send(10000, data='')


@finance.route('/update_stock', methods=['GET'])
def update_stock():
    # stock.addAllStockCodes()
    return send(10000, data='')
