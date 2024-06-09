# coding:utf8
import abc
from ..config.stockDataConst import Constants, EastConfig
from ...common.session import session


class StockDataBase(metaclass=abc.ABCMeta):

    def __init__(self):
        self._session = session
        self._headers = EastConfig.request_header.value
        self._code_id_dict = EastConfig.code_id_dict.value

    def get_code_id(self, code):
        if code in self._code_id_dict.keys():
            return self._code_id_dict[code]
        url = Constants.EAST_CODE_ID_URL.value
        params = (
            ('input', f'{code}'),
            ('type', '14'),
            ('token', 'D43BF722C8E33BDC906FB84D85E326E8'),
        )
        response = self._session.get(url, params=params).json()
        code_dict = response['QuotationCodeTable']['Data']
        if code_dict:
            return code_dict[0]['QuoteID']
        else:
            return None