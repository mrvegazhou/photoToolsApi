# -*- coding: utf-8 -*-
from stock_app.__init__ import db, utils
import typing

class Base(db.Model):
    # Flask-SQLAlchemy创建table时,如何声明基类（这个类不会创建表,可以被继承）
    # 方法就是把__abstract__这个属性设置为True,这个类为基类，不会被创建为表！
    __abstract__ = True

    """根据 code 确定唯一 hash 值（确定分表）"""
    @classmethod
    def get_hash_table_id(cls, code, max_num):
        hash_str = utils['common'].md5(code)
        num = int(hash_str[:2] + hash_str[-2:], 16)  # 16进制 --> 10进制
        hash_id = num % max_num
        return hash_id

    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)

    def __repr__(self) -> str:
        return self._repr(id=self.id)

    def _repr(self, **fields: typing.Dict[str, typing.Any]) -> str:
        '''
        Helper for __repr__
        '''
        field_strings = []
        at_least_one_attached_attribute = False
        for key, field in fields.items():
            try:
                field_strings.append(f'{key}={field!r}')
            except Exception:
                field_strings.append(f'{key}=DetachedInstanceError')
            else:
                at_least_one_attached_attribute = True
        if at_least_one_attached_attribute:
            return f"<{self.__class__.__name__}({','.join(field_strings)})>"
        return f"<{self.__class__.__name__} {id(self)}>"