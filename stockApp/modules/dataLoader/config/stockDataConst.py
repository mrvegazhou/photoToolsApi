# _*_ coding: utf-8 _*_
from enum import Enum, unique
from typing import Dict

@unique
class Constants(Enum):
    # 东财获取它系统自己的code id
    EAST_CODE_ID_URL = 'https://searchapi.eastmoney.com/api/suggest/get'

    # 股票实时
    REAL_TIME_SINA_URL = "http://hq.sinajs.cn/rn={}&list="
    REAL_TIME_EAST_MONEY_URL = "https://push2.eastmoney.com/api/qt/ulist.np/get"
    FULL_REAL_TIME_EAST_MONEY_URL = 'http://push2.eastmoney.com/api/qt/stock/get'
    REAL_TIME_NET_EASE_URL = 'http://api.money.126.net/data/feed/{},money.api'
    REAL_TIME_NET_TENCENT_URL = 'http://qt.gtimg.cn/q={}'

    # 新股或者ST列表
    NEW_OR_ST_STOCKS_URL = 'http://40.push2.eastmoney.com/api/qt/clist/get'

    # 次新股
    NEWLY_ISSUED_URL = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.'

    # 停牌
    SUSPENDED_URL = 'https://datacenter-web.eastmoney.com/api/data/v1/get'

    # 组合市场行情
    MARKET_REAL_TIME_URL = 'http://push2.eastmoney.com/api/qt/clist/get'
    # 日内K线
    INTRADY_DATA_URL = 'http://push2his.eastmoney.com/api/qt/stock/kline/get'
    # 龙虎榜
    DAILY_BILL_BOARD_URL = 'http://datacenter-web.eastmoney.com/api/data/v1/get'
    # 最新一个交易日单子流入数据(分钟级)
    TODAY_BILL_URL = 'http://push2.eastmoney.com/api/qt/stock/fflow/kline/get'
    # 股票历史单子流入数据(日级)
    HISTORY_BILL_URL = 'http://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get'

    # 业绩快报
    EARNINGS_RELEASE_URL = 'http://datacenter.eastmoney.com/api/data/get?v=1'
    # 业绩预告
    EARNINGS_FORECAST_URL = 'http://datacenter.eastmoney.com/securities/api/data/v1/get'
    # 资产负债表
    BALANCE_SHEET_URL = 'http://datacenter-web.eastmoney.com/api/data/v1/get?v=1'
    # 利润表
    INCOME_STATEMENT_URL = 'http://datacenter-web.eastmoney.com/api/data/v1/get?v=2'
    # 现金流量表
    CASH_FLOW_STATEMENT_URL = 'http://datacenter-web.eastmoney.com/api/data/v1/get?v=3'
    # 年报季报财务指标
    Q_A_REPORT_URL = 'http://datacenter.eastmoney.com/api/data/get'
    # 沪深市场全部股票报告期信息
    ALL_STOCK_REPORT_URL = 'http://datacenter.eastmoney.com/securities/api/data/get'

    # 个股详细财务指标
    STOCK_FINANCIAL_INDICATORS_URL = 'http://money.finance.sina.com.cn/corp/go.php/vFD_FinancialGuideLine/stockid/{}/ctrl/{}/displaytype/4.phtml'

    # 股票交易日
    SZSE_DATE_URL = 'http://www.szse.cn/api/report/exchange/onepersistenthour/monthList?month={}'
    SINA_DATE_LIST_URL = 'https://finance.sina.com.cn/realstock/company/klc_td_sh.txt'

@unique
class EastConfig(Enum):

    # 东方财富网网页请求头
    request_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2'}

    code_id_dict = {
        '上证综指': '1.000001', 'sh': '1.000001', '上证指数': '1.000001', '1.000001': '1.000001',
        '深证综指': '0.399106', 'sz': '0.399106', '深证指数': '0.399106', '深证成指': '0.399106',
        '创业板指': '0.399006', 'cyb': '0.399006', '创业板': '0.399006', '创业板指数': '0.399006',
        '沪深300': '1.000300', 'hs300': '1.000300',
        '上证50': '1.000016', 'sz50': '1.000016',
        '上证180': '1.000010', 'sz180': '1.000010',
        '科创50': '1.000688', 'kc50': '1.000688',
        '中小100': '0.399005', 'zxb': '0.399005', '中小板': '0.399005', '中小板指数': '0.399005', '深圳100': '0.399005',
        '标普500': '100.SPX', 'SPX': '100.SPX', 'spx': '100.SPX', '标普指数': '100.SPX',
        '纳斯达克': '100.NDX', '纳斯达克指数': '100.NDX', 'NSDQ': '100.NDX', 'nsdq': '100.NDX',
        '道琼斯': '100.DJIA', 'DJIA': '100.DJIA', 'dqs': '100.DJIA', '道琼斯指数': '100.DJIA',
        '韩国KOSPI': '100.KS11', '韩国综合': '100.KS11', '韩国综合指数': '100.KS11', '韩国指数': '100.KS11',
        '加拿大S&P/TSX': '100.TSX', '加拿大指数': '100.TSX',
        '巴西BOVESPA': '100.BVSP', '巴西指数': '100.BVSP',
        '墨西哥BOLSA': '100.MXX', '墨西哥指数': '100.MXX',
        '俄罗斯RTS': '100.RTS', '俄罗斯指数': '100.RTS',
    }

    market_dict = {
        'all_stocks': 'm:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23',
        'sh_sz_A': 'm:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23',
        'sh_A': 'm:1 t:2,m:1 t:23', # 上证A
        'sz_A': 'm:0 t:6,m:0 t:80', # 深证A
        'bj_A': 'm:0 t:81 s:2048',  # 北证A
        'chi_next_A': 'm:0 t:80',   # 创业板
        'star_A': 'm:1 t:23',   # 科创板
        'sh_sz_bj_A': 'm:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23,m:0 t:81 s:2048',  # 沪深京A
        'sh_north_bound_A': 'b:BK0707', # 沪股通
        'sz_north_bound_A': 'b:BK0804', # 深股通
        'risk_warning_board': 'm:0 f:4,m:1 f:4',    # 风险警示板
        'delisting': 'm:0 s:3', # 两网及退市
        'new_stocks': 'm:0 f:8,m:1 f:8',    # 新股
        'american_stocks': 'm:105,m:106,m:107', # 美股
        'hk_stocks': 'm:128 t:3,m:128 t:4,m:128 t:1,m:128 t:2', # 港股
        'china_concept_stocks': 'b:MK0201', # 中概股
        'regional_sector': 'm:90 t:1 f:!50',    # 地域板块
        'industry_sector': 'm:90 t:2 f:!50',    # 行业板块
        'conceptual_sector': 'm:90 t:3 f:!50',  # 概念板块
        'sh_index': 'm:1 s:2',  # 上证指数
        'sz_index': 'm:0 t:5',  # 深证指数
        'sh_sz_index': 'm:1 s:2,m:0 t:5',   # 沪深指数
        'bond': 'b:MK0354', # 可转债
        'future': 'm:113,m:114,m:115,m:8,m:142',    # 期货
        'ETF': 'b:MK0021,b:MK0022,b:MK0023,b:MK0024',
        'LOF': 'b:MK0404,b:MK0405,b:MK0406,b:MK0407',
    }

    stock_intraday_data_dict = {
        'date': 'f51',   # 日期,
        'open': 'f52',   # 开盘,
        'close': 'f53',   # 收盘,
        'high_price': 'f54',   # 最高,
        'low_price': 'f55',   # 最低,
        'volume': 'f56',   # 成交量,
        'turnover': 'f57',   # 成交额,
        'amplitude': 'f58',   # 振幅,
        'percent': 'f59',   # 涨跌幅,
        'price_change': 'f60',   # 涨跌额,
        'turnover_rate': 'f61',   # 换手率,
    }

    stock_real_time_dict = {
        'code': 'f12',
        'name': 'f14',
        'amplitude': 'f3',  # 振幅(%)
        'now_price': 'f2',
        'high_price': 'f15',
        'low_price': 'f16',
        'open': 'f17',
        'turnover_rate': 'f8',  # 换手率
        'volume_ratio': 'f10', # 量比
        'p_e_ratio': 'f9', # 市盈率
        'volume': 'f5', # 成交量
        'turnover': 'f6', # 成交额
        'yesterday_close': 'f18',
        'total_market_value': 'f20',  # 总市值
        'floating_market_value': 'f21',  # 流通市值
        'date': 'f124',
    }

    full_stock_real_time_dict = {
        'name': 'f58',
        'code': 'f57',
        'open': 'f46',

        'yesterday_close': 'f60',
        'now_price': 'f43',

        'high_price': 'f44',
        'low_price': 'f45',

        'volume': 'f47', # 今日成交量
        'turnover': 'f48', # 今日成交金额

        'buy_volume': 'f49', # 买入数量
        'percent': 'f50', # 涨跌幅
        # 'updown': 'f4', # 涨跌金额
        'sell_volume': 'f59', # 卖出数量
        'p_e_ratio': 'f52', # 市盈率
        'turnover_rate': 'f55', # 换手率
        'amplitude': 'f62', # "振幅(%)":'f62',
        'volume_ratio': 'f92', # 量比
        'total_market_value': 'f84', # 总市值
        'floating_market_value': 'f85', # 流通市值
        'net_inflow': 'f103', # 净流入
        'inner_disk': 'f104', # 内盘
        'outer_disk': 'f105', # 外盘
        'bid_volume': 'f107', # 委买量
        'ask_volume': 'f108', # 委卖量
        'commitment_ratio': 'f109', # 委比
        'bid_amount': 'f110', # 委买金额
        'ask_amount': 'f111', # 委卖金额
        'commitment_ratio_value': 'f112', # 委比值

        'five_trades': 'f113', # 五档成交
        'five_bid': 'f114', # 五档委买
        'five_ask': 'f115', # 五档委卖
        'capital_inflow': 'f116', # 资金流入
        'capital_outflow': 'f117', # 资金流出

        'bid_vol_1': 'f16',
        'bid_price_1': 'f15',

        'bid_vol_2': 'f20',
        'bid_price_2': 'f19',

        'bid_vol_3': 'f40',
        'bid_price_3': 'f39',

        'bid_vol_4': 'f36',
        'bid_price_4': 'f35',

        'bid_vol_5': 'f32',
        'bid_price_5': 'f31',

        'ask_vol_1': 'f14',
        'ask_price_1': 'f13',

        'ask_vol_2': 'f18',
        'ask_price_2': 'f17',

        'ask_vol_3': 'f36',
        'ask_price_3': 'f35',

        'ask_vol_4': 'f38',
        'ask_price_4': 'f37',

        'ask_vol_5': 'f34',
        'ask_price_5': 'f33',

        'date': 'f86',
        'trading_time_periods': 'f80', #交易时间段
        'time': 'f86',
    }

    daily_bill_board_dict = {
        'code':  'SECURITY_CODE', #股票代码
        'name': 'SECURITY_NAME_ABBR', #股票名称
        'date': 'TRADE_DATE', #上榜日期
        'explain': 'EXPLAIN', #解读
        'close': 'CLOSE_PRICE', #收盘价
        'percent': 'CHANGE_RATE', #涨跌幅
        'turnover_rate': 'TURNOVERRATE', #换手率
        'billboard_net_amt': 'BILLBOARD_NET_AMT', #龙虎榜净买额
        'billboard_buy_amt': 'BILLBOARD_BUY_AMT', #龙虎榜买入额
        'billboard_sell_amt': 'BILLBOARD_SELL_AMT', #龙虎榜卖出额
        'billboard_deal_amt': 'BILLBOARD_DEAL_AMT', #龙虎榜成交额
        'accum_amount': 'ACCUM_AMOUNT', #市场总成交额
        'deal_net_ratio': 'DEAL_NET_RATIO', #净买额占总成交比
        'deal_amount_ratio': 'DEAL_AMOUNT_RATIO', #成交额占总成交比
        'free_market_cap': 'FREE_MARKET_CAP', #流通市值
        'explanation': 'EXPLANATION', #上榜原因
    }

    today_bill_dict = {
        'date': 0,
        'main_force_net_inflow': 1, # 主力净流入
        'small_order_net_inflow': 2, # 小单净流入
        'medium_order_net_inflow': 3, # 中单净流入
        'large_order_net_inflow': 4, # 大单净流入
        'extra_large_order_net_inflow': 5, # 超大单净流入
    }

    history_bill_dict = {
        'date': 'f51', # 日期',
        'main_force_net_inflow': 'f52', # 主力净流入',
        'small_order_net_inflow': 'f53', # 小单净流入',
        'medium_order_net_inflow': 'f54', # 中单净流入',
        'large_order_net_inflow': 'f55', # 大单净流入',
        'extra_large_order_net_inflow': 'f56', # 超大单净流入',
        'main_force_net_inflow_ratio': 'f57', # 主力净流入占比',
        'small_order_net_inflow_ratio': 'f58', # 小单流入净占比',
        'medium_order_net_inflow_ratio': 'f59', # 中单流入净占比',
        'large_order_net_inflow_ratio': 'f60', # 大单流入净占比',
        'extra_large_order_net_inflow_ratio': 'f61', # 超大单流入净占比',
        'close': 'f62', # 收盘价',
        'percent': 'f63', # 涨跌幅',
    }

    # 财务 业绩快报
    earnings_release_dict = [
        'id', # 序号
        'code', # 代码
        'name', # 简称
        'sector', # 板块
        '_',
        'type', # 类型
        '_',
        'announcement_date', # 公告日
        '_',
        'EPS', # earnings_per_share 每股收益
        'operating_revenue', # 营业收入
        'YoY_operating_revenue', # 营业收入去年同期
        'net_profit',  # 净利润
        'YoY_net_profit', # 净利润去年同期
        'BVPS', # book_value_per_share 每股净资产
        'ROE', # return_on_equity 净资产收益率
        'revenue_growth_YoY', # 营业收入同比
        'net_profit_growth_YoY', # 净利润同比
        'revenue_growth_QoQ', # 营业收入季度环比
        'net_profit_growth_QoQ', # 净利润季度环比
        'industry', # 行业
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
    ]

    # 业绩预告
    earning_forcast_dict = {
        'code': 'SECURITY_CODE',
        'name': 'SECURITY_NAME_ABBR',
        'forecasting_indicator': 'NOTICE_DATE', # 预测指标
        'earnings_variation': 'REPORT_DATE', # 业绩变动
        'predictive_value': 'PREDICT_FINANCE', # 预测数值
        'variation_range': 'PREDICT_CONTENT', # 变动幅度
        'change_reason_explain': 'CHANGE_REASON_EXPLAIN', # 变动原因
        'predict_type': 'PREDICT_TYPE', # 预告类型
        'YoY': 'PREYEAR_SAME_PERIOD', # 上年同期
        'announcement_date': 'INCREASE_JZ', # 公告日
        '': 'FORECAST_JZ'
    }

    detail_info_dict = {
        'code': "f57", # 股票代码
        'name': "f58", # 股票简称
        'total_share_capital': "f84", # 总股本
        'floating_shares': "f85", # 流通股
        'industry': "f127", # 行业
        'total_market_value': "f116", # 总市值
        'floating_market_value': "f117", # 流通市值
        'IPO_date': "f189", # 上市时间
    }

    suspended_info_dict = {
        'index': '序号',
        'code': "代码",
        'name': "名称",
        'suspended_date': "停牌时间",
        'suspended_deadline': "停牌截止时间",
        'suspended_period': "停牌期限",
        'suspended_reason': "停牌原因",
        'market': "所属市场",
        'suspended_beigin_date': "停牌开始日期",
        'suspended_end_date': "预计复牌时间"
    }

    new_st_stock_info_dict: Dict[str, str] = {
        'code': '代码',
        'name': '名称',
        'close': '收盘价',
        'percent': '涨跌幅',
        'price_change': '涨跌额',
        'volume': '成交量',
        'turnover': '成交额',
        'amplitude': '振幅',
        'high_price': '最高',
        'low_price': '最低',
        'open': '开盘价',
        'yesterday_close': '昨日收盘价',
        'volume_ratio': '量比',
        'turnover_rate': '换手率',
        'forward_pe': '动态市盈率',
        'pb_ratio': '市净率'
    }



@unique
class SinaConfig(Enum):
    hk_js_decode = """
    function d(t) {
                var e, i, n, r, a, o, s, l = (arguments,
                864e5), u = 7657, c = [], d = [], h = ~(3 << 30), f = 1 << 30, m = [0, 3, 5, 6, 9, 10, 12, 15, 17, 18, 20, 23, 24, 27, 29, 30], p = Math, g = function() {
                    var l, u;
                    for (l = 0; 64 > l; l++)
                        d[l] = p.pow(2, l),
                        26 > l && (c[l] = v(l + 65),
                        c[l + 26] = v(l + 97),
                        10 > l && (c[l + 52] = v(l + 48)));
                    for (c.push("+", "/"),
                    c = c.join(""),
                    i = t.split(""),
                    n = i.length,
                    l = 0; n > l; l++)
                        i[l] = c.indexOf(i[l]);
                    return r = {},
                    e = o = 0,
                    a = {},
                    u = w([12, 6]),
                    s = 63 ^ u[1],
                    {
                        _1479: D,
                        _136: _,
                        _200: C,
                        _139: R,
                        _197: A,
                        _3466: O
                    }["_" + u[0]] || function() {
                        return []
                    }
                }, v = String.fromCharCode, b = function(t) {
                    return t === {}._
                }, N = function() {
                    var t, e;
                    for (t = y(),
                    e = 1; ; ) {
                        if (!y())
                            return e * (2 * t - 1);
                        e++
                    }
                }, y = function() {
                    var t;
                    return e >= n ? 0 : (t = i[e] & 1 << o,
                    o++,
                    o >= 6 && (o -= 6,
                    e++),
                    !!t)
                }, w = function(t, r, a) {
                    var s, l, u, c, h;
                    for (l = [],
                    u = 0,
                    r || (r = []),
                    a || (a = []),
                    s = 0; s < t.length; s++)
                        if (c = t[s],
                        u = 0,
                        c) {
                            if (e >= n)
                                return l;
                            if (t[s] <= 0)
                                u = 0;
                            else if (t[s] <= 30) {
                                for (; h = 6 - o,
                                h = c > h ? h : c,
                                u |= (i[e] >> o & (1 << h) - 1) << t[s] - c,
                                o += h,
                                o >= 6 && (o -= 6,
                                e++),
                                c -= h,
                                !(0 >= c); )
                                    ;
                                r[s] && u >= d[t[s] - 1] && (u -= d[t[s]])
                            } else
                                u = w([30, t[s] - 30], [0, r[s]]),
                                a[s] || (u = u[0] + u[1] * d[30]);
                            l[s] = u
                        } else
                            l[s] = 0;
                    return l
                }, x = function() {
                    var t;
                    return t = w([3])[0],
                    1 == t ? (r.d = w([18], [1])[0],
                    t = 0) : t || (t = w([6])[0]),
                    t
                }, S = function(t) {
                    var e, i, n;
                    for (t > 1 && (e = 0),
                    e = 0; t > e; e++)
                        r.d++,
                        n = r.d % 7,
                        (3 == n || 4 == n) && (r.d += 5 - n);
                    return i = new Date,
                    i.setTime((u + r.d) * l),
                    i
                }, k = function(t) {
                    var e, i, n;
                    for (n = r.wd || 62,
                    e = 0; t > e; e++)
                        do
                            r.d++;
                        while (!(n & 1 << (r.d % 7 + 10) % 7));
                    return i = new Date,
                    i.setTime((u + r.d) * l),
                    i
                }, T = function(t) {
                    var e, i, n;
                    return t ? 0 > t ? (e = T(-t),
                    [-e[0], -e[1]]) : (e = t % 3,
                    i = (t - e) / 3,
                    n = [i, i],
                    e && n[e - 1]++,
                    n) : [0, 0]
                }, P = function(t, e, i) {
                    var n, r, a;
                    for (r = "number" == typeof e ? T(e) : e,
                    a = T(i),
                    n = [a[0] - r[0], a[1] - r[1]],
                    r = 1; n[0] < n[1]; )
                        r *= 5,
                        n[1]--;
                    for (; n[1] < n[0]; )
                        r *= 2,
                        n[0]--;
                    if (r > 1 && (t *= r),
                    n = n[0],
                    t = E(t),
                    0 > n) {
                        for (; t.length + n <= 0; )
                            t = "0" + t;
                        return n += t.length,
                        r = t.substr(0, n) - 0,
                        void 0 === i ? r + "." + t.substr(n) - 0 : (a = t.charAt(n) - 0,
                        a > 5 ? r++ : 5 == a && (t.substr(n + 1) - 0 > 0 ? r++ : r += 1 & r),
                        r)
                    }
                    for (; n > 0; n--)
                        t += "0";
                    return t - 0
                }, C = function() {
                    var t, i, a, o, l;
                    if (s >= 1)
                        return [];
                    for (r.d = w([18], [1])[0] - 1,
                    a = w([3, 3, 30, 6]),
                    r.p = a[0],
                    r.ld = a[1],
                    r.cd = a[2],
                    r.c = a[3],
                    r.m = p.pow(10, r.p),
                    r.pc = r.cd / r.m,
                    i = [],
                    t = 0; o = {
                        d: 1
                    },
                    y() && (a = w([3])[0],
                    0 == a ? o.d = w([6])[0] : 1 == a ? (r.d = w([18])[0],
                    o.d = 0) : o.d = a),
                    l = {
                        date: S(o.d)
                    },
                    y() && (r.ld += N()),
                    a = w([3 * r.ld], [1]),
                    r.cd += a[0],
                    l.close = r.cd / r.m,
                    i.push(l),
                    !(e >= n) && (e != n - 1 || 63 & (r.c ^ t + 1)); t++)
                        ;
                    return i[0].prevclose = r.pc,
                    i
                }, _ = function() {
                    var t, i, a, o, l, u, c, d, h, f, m;
                    if (s > 2)
                        return [];
                    for (c = [],
                    h = {
                        v: "volume",
                        p: "price",
                        a: "avg_price"
                    },
                    r.d = w([18], [1])[0] - 1,
                    d = {
                        date: S(1)
                    },
                    a = w(1 > s ? [3, 3, 4, 1, 1, 1, 5] : [4, 4, 4, 1, 1, 1, 3]),
                    t = 0; 7 > t; t++)
                        r[["la", "lp", "lv", "tv", "rv", "zv", "pp"][t]] = a[t];
                    for (r.m = p.pow(10, r.pp),
                    s >= 1 ? (a = w([3, 3]),
                    r.c = a[0],
                    a = a[1]) : (a = 5,
                    r.c = 2),
                    r.pc = w([6 * a])[0],
                    d.pc = r.pc / r.m,
                    r.cp = r.pc,
                    r.da = 0,
                    r.sa = r.sv = 0,
                    t = 0; !(e >= n) && (e != n - 1 || 7 & (r.c ^ t)); t++) {
                        for (l = {},
                        o = {},
                        f = r.tv ? y() : 1,
                        i = 0; 3 > i; i++)
                            if (m = ["v", "p", "a"][i],
                            (f ? y() : 0) && (a = N(),
                            r["l" + m] += a),
                            u = "v" == m && r.rv ? y() : 1,
                            a = w([3 * r["l" + m] + ("v" == m ? 7 * u : 0)], [!!i])[0] * (u ? 1 : 100),
                            o[m] = a,
                            "v" == m) {
                                if (!(l[h[m]] = a) && (s > 1 || 241 > t) && (r.zv ? !y() : 1)) {
                                    o.p = 0;
                                    break
                                }
                            } else
                                "a" == m && (r.da = (1 > s ? 0 : r.da) + o.a);
                        r.sv += o.v,
                        l[h.p] = (r.cp += o.p) / r.m,
                        r.sa += o.v * r.cp,
                        l[h.a] = b(o.a) ? t ? c[t - 1][h.a] : l[h.p] : r.sv ? ((p.floor((r.sa * (2e3 / r.m) + r.sv) / r.sv) >> 1) + r.da) / 1e3 : l[h.p] + r.da / 1e3,
                        c.push(l)
                    }
                    return c[0].date = d.date,
                    c[0].prevclose = d.pc,
                    c
                }, D = function() {
                    var t, e, i, n, a, o, l;
                    if (s >= 1)
                        return [];
                    for (r.lv = 0,
                    r.ld = 0,
                    r.cd = 0,
                    r.cv = [0, 0],
                    r.p = w([6])[0],
                    r.d = w([18], [1])[0] - 1,
                    r.m = p.pow(10, r.p),
                    a = w([3, 3]),
                    r.md = a[0],
                    r.mv = a[1],
                    t = []; a = w([6]),
                    a.length; ) {
                        if (i = {
                            c: a[0]
                        },
                        n = {},
                        i.d = 1,
                        32 & i.c)
                            for (; ; ) {
                                if (a = w([6])[0],
                                63 == (16 | a)) {
                                    l = 16 & a ? "x" : "u",
                                    a = w([3, 3]),
                                    i[l + "_d"] = a[0] + r.md,
                                    i[l + "_v"] = a[1] + r.mv;
                                    break
                                }
                                if (32 & a) {
                                    o = 8 & a ? "d" : "v",
                                    l = 16 & a ? "x" : "u",
                                    i[l + "_" + o] = (7 & a) + r["m" + o];
                                    break
                                }
                                if (o = 15 & a,
                                0 == o ? i.d = w([6])[0] : 1 == o ? (r.d = o = w([18])[0],
                                i.d = 0) : i.d = o,
                                !(16 & a))
                                    break
                            }
                        n.date = S(i.d);
                        for (o in {
                            v: 0,
                            d: 0
                        })
                            b(i["x_" + o]) || (r["l" + o] = i["x_" + o]),
                            b(i["u_" + o]) && (i["u_" + o] = r["l" + o]);
                        for (i.l_l = [i.u_d, i.u_d, i.u_d, i.u_d, i.u_v],
                        l = m[15 & i.c],
                        1 & i.u_v && (l = 31 - l),
                        16 & i.c && (i.l_l[4] += 2),
                        e = 0; 5 > e; e++)
                            l & 1 << 4 - e && i.l_l[e]++,
                            i.l_l[e] *= 3;
                        i.d_v = w(i.l_l, [1, 0, 0, 1, 1], [0, 0, 0, 0, 1]),
                        o = r.cd + i.d_v[0],
                        n.open = o / r.m,
                        n.high = (o + i.d_v[1]) / r.m,
                        n.low = (o - i.d_v[2]) / r.m,
                        n.close = (o + i.d_v[3]) / r.m,
                        a = i.d_v[4],
                        "number" == typeof a && (a = [a, a >= 0 ? 0 : -1]),
                        r.cd = o + i.d_v[3],
                        l = r.cv[0] + a[0],
                        r.cv = [l & h, r.cv[1] + a[1] + !!((r.cv[0] & h) + (a[0] & h) & f)],
                        n.volume = (r.cv[0] & f - 1) + r.cv[1] * f,
                        t.push(n)
                    }
                    return t
                }, R = function() {
                    var t, e, i, n;
                    if (s > 1)
                        return [];
                    for (r.l = 0,
                    n = -1,
                    r.d = w([18])[0] - 1,
                    i = w([18])[0]; r.d < i; )
                        e = S(1),
                        0 >= n ? (y() && (r.l += N()),
                        n = w([3 * r.l], [0])[0] + 1,
                        t || (t = [e],
                        n--)) : t.push(e),
                        n--;
                    return t
                }, A = function() {
                    var t, i, a, o;
                    if (s >= 1)
                        return [];
                    for (r.f = w([6])[0],
                    r.c = w([6])[0],
                    a = [],
                    r.dv = [],
                    r.dl = [],
                    t = 0; t < r.f; t++)
                        r.dv[t] = 0,
                        r.dl[t] = 0;
                    for (t = 0; !(e >= n) && (e != n - 1 || 7 & (r.c ^ t)); t++) {
                        for (o = [],
                        i = 0; i < r.f; i++)
                            y() && (r.dl[i] += N()),
                            r.dv[i] += w([3 * r.dl[i]], [1])[0],
                            o[i] = r.dv[i];
                        a.push(o)
                    }
                    return a
                }, O = function() {
                    if (r = {
                        b_avp: 1,
                        b_ph: 0,
                        b_phx: 0,
                        b_sep: 0,
                        p_p: 6,
                        p_v: 0,
                        p_a: 0,
                        p_e: 0,
                        p_t: 0,
                        l_o: 3,
                        l_h: 3,
                        l_l: 3,
                        l_c: 3,
                        l_v: 5,
                        l_a: 5,
                        l_e: 3,
                        l_t: 0,
                        u_p: 0,
                        u_v: 0,
                        u_a: 0,
                        wd: 62,
                        d: 0
                    },
                    s > 0)
                        return [];
                    var t, i, a, o, l, u, c;
                    for (t = []; ; ) {
                        if (e >= n)
                            return void 0;
                        if (a = {
                            d: 1,
                            c: 0
                        },
                        y())
                            if (y()) {
                                if (y()) {
                                    for (a.c++,
                                    a.a = r.b_avp,
                                    y() && (r.b_avp ^= y(),
                                    r.b_ph ^= y(),
                                    r.b_phx ^= y(),
                                    a.s = r.b_sep,
                                    r.b_sep ^= y(),
                                    y() && (r.wd = w([7])[0]),
                                    a.s ^ r.b_sep && (a.s ? r.u_p = r.u_c : r.u_o = r.u_h = r.u_l = r.u_c = r.u_p)),
                                    u = 0; u < 3 + 2 * r.b_ph; u++)
                                        if (y() && (l = "pvaet".charAt(u),
                                        o = r["p_" + l],
                                        r["p_" + l] += N(),
                                        r["u_" + l] = P(r["u_" + l], o, r["p_" + l]) - 0,
                                        r.b_sep && !u))
                                            for (c = 0; 4 > c; c++)
                                                l = "ohlc".charAt(c),
                                                r["u_" + l] = P(r["u_" + l], o, r.p_p) - 0;
                                    !r.b_avp && a.a && (r.u_a = P(i && i.amount || 0, 0, r.p_a))
                                }
                                if (y())
                                    for (a.c++,
                                    u = 0; u < 7 + r.b_ph + r.b_phx; u++)
                                        y() && (6 == u ? a.d = x() : r["l_" + "ohlcva*et".charAt(u)] += N());
                                if (y() && (a.c++,
                                l = r.l_o + (y() && N()),
                                o = w([3 * l], [1])[0],
                                a.p = r.b_sep ? r.u_c + o : r.u_p += o),
                                !a.c)
                                    break
                            } else
                                y() ? y() ? y() ? a.d = x() : r.l_v += N() : r.b_ph && y() ? r["l_" + "et".charAt(r.b_phx && y())] += N() : r.l_a += N() : r["l_" + "ohlc".charAt(w([2])[0])] += N();
                        for (u = 0; u < 6 + r.b_ph + r.b_phx; u++)
                            c = "ohlcvaet".charAt(u),
                            o = (r.b_sep ? 191 : 185) >> u & 1,
                            a["v_" + c] = w([3 * r["l_" + c]], [o])[0];
                        i = {
                            date: k(a.d)
                        },
                        a.p && (i.prevclose = P(a.p, r.p_p)),
                        r.b_sep ? (i.open = P(r.u_o += a.v_o, r.p_p),
                        i.high = P(r.u_h += a.v_h, r.p_p),
                        i.low = P(r.u_l += a.v_l, r.p_p),
                        i.close = P(r.u_c += a.v_c, r.p_p)) : (a.o = r.u_p + a.v_o,
                        i.open = P(a.o, r.p_p),
                        i.high = P(a.o + a.v_h, r.p_p),
                        i.low = P(a.o - a.v_l, r.p_p),
                        i.close = P(r.u_p = a.o + a.v_c, r.p_p)),
                        i.volume = P(r.u_v += a.v_v, r.p_v),
                        r.b_avp ? (o = T(r.p_p),
                        l = T(r.p_v),
                        i.amount = P(P(Math.floor((r.b_sep ? (r.u_o + r.u_h + r.u_l + r.u_c) / 4 : a.o + (a.v_h - a.v_l + a.v_c) / 4) * r.u_v + .5), [o[0] + l[0], o[1] + l[1]], r.p_a) + a.v_a, r.p_a)) : (r.u_a += a.v_a,
                        i.amount = P(r.u_a, r.p_a)),
                        r.b_ph && (i.postVol = P(a.v_e, r.p_e),
                        i.postAmt = P(Math.floor(i.postVol * i.close + (r.b_phx ? P(a.v_t, r.p_t) : 0) + .5), 0)),
                        t.push(i)
                    }
                    return t
                }, E = function(t) {
                    var e, i, n;
                    if (t = (t || 0).toString(),
                    n = [],
                    i = t.toLowerCase().indexOf("e"),
                    i > 0) {
                        for (e = t.substr(i + 1) - 0; e >= 0; e--)
                            n.push(Math.floor(e * Math.pow(10, -e) + .5) - 0);
                        return n.join("")
                    }
                    return t
                };
                return g()()
            }
            ;
    """

    header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "Connection": "keep-alive",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"}

    stock_real_time_dict = {
        'name': 0,
        'open': 1,

        'yesterday_close': 2,
        'now_price': 3,

        'high_price': 4,
        'low_price': 5,

        # '竞买价': 6,
        # '竞卖价': 7,

        'volume': 8,
        'turnover': 9,

        # 'percent': '涨跌幅',
        # 'updown': '涨跌金额',

        'bid_vol_1': 10,
        'bid_price_1': 11,

        'bid_vol_2': 12,
        'bid_price_2': 13,

        'bid_vol_3': 14,
        'bid_price_3': 15,

        'bid_vol_4': 16,
        'bid_price_4': 17,

        'bid_vol_5': 18,
        'bid_price_5': 19,

        'ask_vol_1': 20,
        'ask_price_1': 21,

        'ask_vol_2': 22,
        'ask_price_2': 23,

        'ask_vol_3': 24,
        'ask_price_3': 25,

        'ask_vol_4': 26,
        'ask_price_4': 27,

        'ask_vol_5': 28,
        'ask_price_5': 29,

        'date': 30,
        'time': 31,
    }

    financial_indicators_dict = {
        'date': '日期',
        'EPS': '每股收益',
        'ANAPS': '调整每股净资产', # adjusted_net_assets_per_share
        'CFPS': '每股现金流', # cash_flow_per_share
        'APS': '每股公积金', # accumulated per share
        'UDPS': '每股未分配利润', # undistributed profit per share
        'TA': '总资产', # Total Assets
        'NP_after_NDR': '扣非净利润',
        'MBPR': '主营利润率',
        'ROA': '总资产净利率',
        'net_sales_margin': '销售净利率',
        'ROE2': '净资产报酬率',
        'ROA2': '资产报酬率',
        'ROE': '净资产收益率',
        'WAROE': '加权净资产收益率',
        'RPC': '成本费用利润率',
        'MCR': '主营业务成本率',
        'ART': '应收账款周转率',
        'ITR': '存货周转率',
        'FAT': '固定资产周转率',
        'TAT': '总资产周转率',
        'CATO': '流动资产周转率',
        'CR': '流动比率',
        'QR': '速动比率',
        'cash_ratio': '现金比率',
        'ER': '产权比率',
        'DAR': '资产负债率',
        'CFR': '现金流销售比',
        'CNPR': '现金流净利润比',
        'CFLR': '现金流负债比',
        'MRGR': '主营收入增长率',
        'NPGR': '净利润增长率',
        'NAGR': '净资产增长率',
        'TAGR': '总资产增长率'
    }

    new_stock_info_dict = {
        'symbol': "symbol",
        'code': "code",
        'name': "name",
        'open': "open",
        'high_price': "high",
        'low_price': "low",
        'volume': "volume",
        'turnover': "amount",
        'total_market_value': "mktcap",
        'turnover_rate': "turnoverratio",
    }

@unique
class NetEaseConfig(Enum):
    stock_real_time_dict = {
        'name': 'name',
        'open': 'open',

        'yesterday_close': 'yestclose',
        'now_price': 'price',
        'high_price': 'high',
        'low_price': 'low',
        'volume': 'volume', # 成交量
        'turnover': 'turnover', # 成交额

        'percent': 'percent',
        'updown': 'updown',

        'bid_vol_1': 'bidvol1',
        'bid_price_1': 'bid1',

        'bid_vol_2': 'bidvol2',
        'bid_price_2': 'bid2',

        'bid_vol_3': 'bidvol3',
        'bid_price_3': 'bid3',

        'bid_vol_4': 'bidvol4',
        'bid_price_4': 'bid4',

        'bid_vol_5': 'bidvol5',
        'bid_price_5': 'bid5',

        'ask_vol_1': 'askvol1',
        'ask_price_1': 'ask1',

        'ask_vol_2': 'askvol2',
        'ask_price_2': 'ask2',

        'ask_vol_3': 'askvol3',
        'ask_price_3': 'ask3',

        'ask_vol_4': 'askvol4',
        'ask_price_4': 'ask4',

        'ask_vol_5': 'askvol5',
        'ask_price_5': 'ask5',

        'date': 'time',
        'time': 'time'
    }

@unique
class TencentConfig(Enum):
    stock_real_time_dict = {
        'name': 1,
        'open': 5,
        'yesterday_close': 4,
        'now_price': 3,
        'high_price': 33,
        'low_price': 34,
        'volume': 36,  # 成交量
        'turnover': 37,  # 成交额
        'turnover_rate': 38,
        'percent': 32,
        'updown': 31,
        'out_trade': 7,
        'in_trade': 8,
        'p_e_ratio': 39,
        'limit_up_price': 47,
        'limit_down_price': 48,

        'bid_vol_1': 10,
        'bid_price_1': 9,

        'bid_vol_2': 12,
        'bid_price_2': 11,

        'bid_vol_3': 14,
        'bid_price_3': 13,

        'bid_vol_4': 16,
        'bid_price_4': 15,

        'bid_vol_5': 18,
        'bid_price_5': 17,

        'ask_vol_1': 20,
        'ask_price_1': 19,

        'ask_vol_2': 22,
        'ask_price_2': 21,

        'ask_vol_3': 24,
        'ask_price_3': 23,

        'ask_vol_4': 26,
        'ask_price_4': 25,

        'ask_vol_5': 28,
        'ask_price_5': 27,

        'date': 30
    }