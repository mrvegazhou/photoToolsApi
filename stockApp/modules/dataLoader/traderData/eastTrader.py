# coding:utf8
import sys
import os
# 获取项目根目录的路径（假设当前脚本在module1文件夹内）
project_root = os.path.abspath(os.path.join(__file__, *(['..'] * 5)))
# # 将项目根目录添加到sys.path中
sys.path.append(project_root)

import pickle
import os
import json
import time
import random
import ddddocr
from typing import List
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5

from traderBase import TraderBase, TradeError
from models import Position, Balance, Entrust, Deal
from ..config.tradeDataConst import EastConfig
from modules.common.session import session

def encrypt_data(pwd):
    rsakey = RSA.importKey(EastConfig.public_key.value)
    cipher = Cipher_pkcs1_v1_5.new(rsakey)
    cipher_text = base64.b64encode(cipher.encrypt(pwd.encode(encoding="utf-8")))
    value = cipher_text.decode('utf8')
    return value

class EastTraderData(TraderBase):

    validate_key = None


    random_number = '0.9033461201665647898'
    session_file = 'eastmoney_trader.session'

    def __init__(self, **kwargs):
        super(EastTraderData, self).__init__()
        self._HEADERS = EastConfig.headers.value
        if not self._reload_session():
            self.s = session
            self.s.verify = False
            self.s.headers.update(self._HEADERS)

        self.user = EastConfig.user.value
        self.password = EastConfig.password.value
        self.config = EastConfig.trader_info.value


    def _recognize_verification_code(self):
        ocr = ddddocr.DdddOcr()
        self.random_number = '0.305%d' % random.randint(100000, 900000)
        req = self.s.get("%s%s" % (self.config['yzm'], self.random_number))
        code = ocr.classification(req.content)
        if len(code) == 4:
            return code
        # code length should be 4
        time.sleep(1)
        return self._recognize_verification_code()

    def auto_login(self, **kwargs):
        """重写父类方法"""
        if self.validate_key:
            try:
                self.heartbeat()
                print('already logined in')
                return
            except:
                print('heartbeat failed, login again')

        """
        自动登录
        :return:
        """
        while True:
            password = encrypt_data(self.password)
            identify_code = self._recognize_verification_code()
            # sec_info = self.s.get(f'http://127.0.0.1:18888/api/verifyUserInfo?{identify_code}').json()
            # sec_info = sec_info['userInfo']
            sec_info = ''
            self.s.headers.update({
                "gw_reqtimestamp": str(int(round(time.time() * 1000))),
                "content-type": "application/x-www-form-urlencoded"
            })
            login_res = self.s.post(self.config['authentication'], data={
                'duration': 1800,
                'password': password,
                'identifyCode': identify_code,
                'type': 'Z',
                'userId': self.account_config['user'],
                'randNumber': self.random_number,
                'authCode': '',
                'secInfo': sec_info
            }).json()

            if login_res['Status'] != 0:
                print('auto login error, try again later')
                print(login_res)
                time.sleep(3)
            else:
                break

        self._get_valid_key()

        # 保存session
        self._save_session()

    def _get_valid_key(self):
        content = self.s.get(self.config['authentication_check']).text
        key = "input id=\"em_validatekey\" type=\"hidden\" value=\""
        begin = content.index(key) + len(key)
        end = content.index("\" />", begin)
        self.validate_key = content[begin: end]

    def _save_session(self):
        """
        save session to a cache file
        """
        # always save (to update timeout)
        with open(self.session_file, "wb") as f:
            pickle.dump((self.validate_key, self.s), f)
            print('updated session cache-file %s' % self.session_file)

    def _reload_session(self):
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, "rb") as f:
                    self.validate_key, self.s = pickle.load(f)
                    return True
            except:
                print('load session failed')
        return False

    def get_position(self) -> List[Position]:
        """
        获取持仓
        :return:
        """
        server_positions = self._request_data("get_stock_list")
        if server_positions is None:
            raise TradeError(u"获取持仓失败")

        balance = self.get_balance()[0]
        print(balance)
        position_list = []

        # TODO 验证
        for pos in server_positions:
            position_list.append(
                Position(
                    current_amount=int(pos["Zqsl"]),
                    enable_amount=int(pos["Kysl"]),
                    income_balance=0,
                    cost_price=float(pos["Cbjg"]),
                    last_price=float(pos["Zxjg"]),
                    market_value=float(pos["Zxjg"]) * int(pos["Zqsl"]),
                    position_str="random",
                    stock_code=pos["Zqdm"],
                    stock_name=pos["Zqmc"],
                ))
        return position_list

    def _request_data(self, api_name: str, params=None):
        api = self._get_api_url(api_name)
        result = self.s.get(api, params=params).json()
        if result['Status'] == 0:
            return result['Data']
        # TODO 错误处理
        return None

    def _get_api_url(self, key):
        return self.config[key] % self.validate_key

    @property
    def balance(self) -> List[Balance]:
        return self.get_balance()

    def _get_assets(self):
        return self._request_data("assets")

    def get_balance(self) -> List[Balance]:
        """
        获取账户资金状况
        :return:
        """
        assets = self._get_assets()

        if not assets:
            raise TradeError(u"获取资金失败")

        assets = assets[0]

        # {'Message': None, 'Status': 0, 'Data': [{'Zzc': '1.00', 'Zxsz': '0.00', 'Kyzj': '1.00', 'Kqzj': '1.00',
        # 'Djzj': '0.00', 'Zjye': '1.00', 'Money_type': 'RMB', 'Drckyk': None, 'Ljyk': None, 'F303S': None}]}
        return [
            Balance(
                asset_balance=float(assets['Zzc']),
                current_balance=float(assets['Kqzj']),
                enable_balance=float(assets['Kyzj']),
                frozen_balance=float(assets['Djzj']),
                market_value=float(assets['Zzc']) - float(assets['Kyzj']),
                money_type=u"人民币")
        ]

    def get_entrust(self) -> List[Entrust]:
        """
        获取委托单(目前返回20次调仓的结果)
        操作数量都按1手模拟换算的
        :return:
        """
        xq_entrust_list = self._request_data("get_orders_data")
        entrust_list = []
        for xq_entrusts in xq_entrust_list:
            entrust_list.append(
                Entrust(
                    entrust_no=xq_entrusts["Wtbh"],
                    bs_type=xq_entrusts["Mmlb"],
                    entrust_status=xq_entrusts["Wtzt"],
                    report_time=self._format_time(xq_entrusts["Bpsj"]),
                    stock_code=xq_entrusts["Zqdm"],
                    stock_name=xq_entrusts["Zqmc"],
                    entrust_amount=int(xq_entrusts["Wtsl"]),
                    entrust_price=float(xq_entrusts["Wtjg"]),
                )
            )
        return entrust_list

    def get_current_deal(self) -> List[Deal]:
        """获取当日成交列表"""
        # return self.do(self.config['current_deal'])
        data_list = self._request_data("get_deal_data")
        result = []
        for item in data_list:
            result.append(
                Deal(
                    deal_no=item["Cjbh"],
                    entrust_no=item["Wtbh"],
                    bs_type=item["Mmlb"],
                    stock_code=item["Zqdm"],
                    stock_name=item["Zqmc"],
                    deal_amount=int(item["Cjsl"]),
                    deal_price=float(item["Cjjg"]),
                    entrust_amount=int(item["Wtsl"]),
                    entrust_price=float(item["Wtjg"]),
                    deal_time=self._format_time(item["Cjsj"]),
                )
            )
        return result

    def _format_time(self, time):
        return "%s:%s:%s" % (time[0:2], time[2:4], time[4:])

    def _trade(self, security, price=0, amount=0, volume=0, entrust_bs="B"):
        """
        调仓
        :param security:
        :param price:
        :param amount:
        :param volume:
        :param entrust_bs:
        :return:
        """
        balance = self.get_balance()[0]
        if not volume:
            volume = int(float(price) * amount)  # 可能要取整数
        if balance.enable_balance < volume and entrust_bs == "B":
            raise TradeError(u"没有足够的现金进行操作")
        if amount == 0:
            raise TradeError(u"数量不能为0")

        response = self.s.post(self._get_api_url('submit'), data={
            "stockCode": security,
            "price": price,
            "amount": amount,
            "zqmc": "unknown",
            "tradeType": entrust_bs
        }).json()

        if response['Status'] != 0:
            raise TradeError('下单失败, %s' % json.dumps(response))

        print('下单成功')

    def buy(self, security, price=0, amount=0, volume=0, entrust_prop=0):
        """买入卖出股票
        :param security: 股票代码
        :param price: 买入价格
        :param amount: 买入股数
        :param volume: 买入总金额 由 volume / price 取整， 若指定 price 则此参数无效
        :param entrust_prop:
        """
        return self._trade(security, price, amount, volume, "B")

    def sell(self, security, price=0, amount=0, volume=0, entrust_prop=0):
        """卖出股票
        :param security: 股票代码
        :param price: 卖出价格
        :param amount: 卖出股数
        :param volume: 卖出总金额 由 volume / price 取整， 若指定 price 则此参数无效
        :param entrust_prop:
        """
        return self._trade(security, price, amount, volume, "S")


if __name__ == '__main__':
    trader = EastTraderData()
    trader.prepare()
    print(trader.get_position())
    # trader.buy('002230', price=55, amount=100)