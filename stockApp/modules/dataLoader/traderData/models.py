from dataclasses import dataclass


@dataclass
class Balance:
    """
    资产
    """

    # 总资产
    asset_balance: float

    current_balance: float

    # 可用
    enable_balance: float

    frozen_balance: float

    # 市值
    market_value: float

    # 币种
    money_type: str

    pre_interest: float = 0

    def update(self, market_value, current_balance):
        self.market_value = market_value
        self.current_balance = current_balance
        self.asset_balance = self.current_balance + self.market_value

    def update_total(self):
        self.asset_balance = self.current_balance + self.market_value

@dataclass
class Position:
    """
    持仓
    """
    current_amount: int
    enable_amount: int
    income_balance: int
    cost_price: float
    last_price: float
    market_value: float
    position_str: str
    stock_code: str
    stock_name: str

    def update(self, last_price: float):
        self.last_price = last_price
        self.market_value = self.current_amount * last_price


@dataclass
class Deal:
    """
    当日成交
    """
    deal_no: str
    entrust_no: str
    # 买卖类别
    bs_type: str
    entrust_amount: int
    deal_amount: int
    deal_price: float
    entrust_price: float
    # HHmmss
    deal_time: str
    stock_code: str
    stock_name: str


@dataclass
class Entrust:
    """
    历史委托
    """
    entrust_no: str
    # 买卖类别
    bs_type: str
    entrust_amount: int
    entrust_price: float
    report_time: str
    entrust_status: str
    stock_code: str
    stock_name: str
    # 费用
    cost: float
