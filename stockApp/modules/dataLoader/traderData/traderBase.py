# coding:utf8

import abc
import time
from datetime import datetime
from threading import Thread
import requests
import requests.exceptions
from typing import List
from modules.common.session import session
from stockApp.modules.datas.traderData.models import Position, Balance, Deal, Entrust


class NotLoginError(Exception):
    def __init__(self, result=None):
        super(NotLoginError, self).__init__()
        self.result = result

class TradeError(IOError):
    pass

class TraderBase(metaclass=abc.ABCMeta):

    user = ''
    password = ''

    def __init__(self, debug=True):
        self.__read_config()
        self.account_config = None
        self.time = datetime.now()
        self.heart_active = True
        self.heart_thread = Thread(target=self.send_heartbeat)
        self._session = session

    def __read_config(self):
        pass

    def send_heartbeat(self):
        """每隔10秒查询指定接口保持 token 的有效性"""
        while True:
            if self.heart_active:
                self.check_login()
            else:
                time.sleep(1)

    def check_login(self, sleepy=30):
        try:
            response = self.heartbeat()
            self.check_account_live(response)
        except requests.exceptions.ConnectionError:
            pass
        except requests.exceptions.RequestException as e:
            print("心跳线程发现账户出现错误: %s %s, 尝试重新登陆", e.__class__, e)
            self.auto_login()
        finally:
            pass
        time.sleep(sleepy)

    def auto_login(self, limit=10):
        """实现自动登录
        :param limit: 登录次数限制
        """
        for _ in range(limit):
            if self.login():
                break
        else:
            raise NotLoginError("登录失败次数过多, 请检查密码是否正确 / 券商服务器是否处于维护中 / 网络连接是否正常")
        self.keepalive()

    def login(self):
        pass

    def check_account_live(self, response):
        pass

    def heartbeat(self):
        return self.balance

    def keepalive(self):
        """启动保持在线的进程 """
        if self.heart_thread.is_alive():
            self.heart_active = True
        else:
            self.heart_thread.start()

    def prepare(self, **kwargs):
        """登录的统一接口
        :param config_file 登录数据文件，若无则选择参数登录模式
        :param user: 各家券商的账号
        :param password: 密码, 券商为加密后的密码
        :param cookies: [雪球登录需要]雪球登录需要设置对应的 cookies
        :param portfolio_code: [雪球登录需要]组合代码
        :param portfolio_market: [雪球登录需要]交易市场，
            可选['cn', 'us', 'hk'] 默认 'cn'
        """
        self._prepare_account(**kwargs)

        self.auto_login()

    def _prepare_account(self, **kwargs):
        """
        转换参数到登录所需的字典格式
        :param cookies: 雪球登陆需要设置 cookies， 具体见
            https://smalltool.github.io/2016/08/02/cookie/
        :param portfolio_code: 组合代码
        :param portfolio_market: 交易市场， 可选['cn', 'us', 'hk'] 默认 'cn'
        :return:
        """
        self.account_config = {
            "user": self.user,
            "password": self.password,
        }

    @property
    def position(self) -> List[Position]:
        return self.get_position()

    def get_position(self) -> List[Position]:
        """获取持仓"""
        return self.do(self.config["position"])

    @property
    def balance(self) -> List[Balance]:
        return self.get_balance()

    def get_balance(self) -> List[Balance]:
        """获取账户资金状况"""
        return self.do(self.config["balance"])

    @property
    def current_deal(self) -> List[Deal]:
        """获取当日成交列表"""
        return self.get_current_deal()

    def get_current_deal(self) -> List[Deal]:
        """获取当日成交列表"""
        # return self.do(self.config['current_deal'])
        print("目前仅在 佣金宝/银河子类 中实现, 其余券商需要补充")

    @property
    def entrust(self) -> List[Entrust]:
        """获取当日委托列表"""
        return self.get_entrust()

    def get_entrust(self) -> List[Entrust]:
        """获取当日委托列表"""
        return self.do(self.config["entrust"])

    def do(self, params):
        response_data = (params)
        try:
            format_json_data = self.format_response_data(response_data)
        # pylint: disable=broad-except
        except Exception:
            # Caused by server force logged out
            return None
        try:
            self.check_login_status(format_json_data)
        except NotLoginError:
            self.auto_login()
        return format_json_data

    def check_login_status(self, return_data):
        pass

    def buy(self, security, price=0, amount=0, volume=0, entrust_prop=0):
        """买入卖出股票
        :param security: 股票代码
        :param price: 买入价格
        :param amount: 买入股数
        :param volume: 买入总金额 由 volume / price 取整， 若指定 price 则此参数无效
        :param entrust_prop:
        """
        pass

    def sell(self, security, price=0, amount=0, volume=0, entrust_prop=0):
        """卖出股票
        :param security: 股票代码
        :param price: 卖出价格
        :param amount: 卖出股数
        :param volume: 卖出总金额 由 volume / price 取整， 若指定 price 则此参数无效
        :param entrust_prop:
        """
        pass