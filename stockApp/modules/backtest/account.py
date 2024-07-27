# coding:utf8



"""
rtn & earning in the Account
    rtn:
        from order's view
        1.change if any order is executed, sell order or buy order
        2.change at the end of today,   (today_close - stock_price) * amount
    earning
        from value of current position
        earning will be updated at the end of trade date
        earning = today_value - pre_value
    **is consider cost**
        while earning is the difference of two position value, so it considers cost, it is the true return rate
        in the specific accomplishment for rtn, it does not consider cost, in other words, rtn - cost = earning

"""


class AccumulatedInfo:
    """
    accumulated trading info, including accumulated return/cost/turnover
    AccumulatedInfo should be shared across different levels
    """

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.rtn: float = 0.0  # accumulated return, do not consider cost
        self.cost: float = 0.0  # accumulated cost
        self.to: float = 0.0  # accumulated turnover

    def add_return_value(self, value: float) -> None:
        self.rtn += value

    def add_cost(self, value: float) -> None:
        self.cost += value

    def add_turnover(self, value: float) -> None:
        self.to += value

    @property
    def get_return(self) -> float:
        return self.rtn

    @property
    def get_cost(self) -> float:
        return self.cost

    @property
    def get_turnover(self) -> float:
        return self.to


class Account:
    """
    The correctness of the metrics of Account in nested execution depends on the shallow copy of `trade_account` in
    qlib/backtest/executor.py:NestedExecutor
    Different level of executor has different Account object when calculating metrics. But the position object is
    shared cross all the Account object.
    """

    