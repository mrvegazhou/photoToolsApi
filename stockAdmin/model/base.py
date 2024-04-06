# -*- coding: utf-8 -*-
import typing
import json
from stock_admin.__init__ import db, utils

class Base(db.Model):
    __abstract__ = True
    __table_args__ = {'extend_existing': True, 'schema': 'stock'}

    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key) and key != 'uuid':
                setattr(self, key, value)

    def get_keys(self):
        return None

    def __repr__(self) -> str:
        obj = self.get_keys()
        if not obj:
            return ''
        return json.dumps(obj, cls=utils["common"].ComplexEncoder)

    def __iter__(self):
        obj = self.get_keys()
        for key in obj:
            yield (key, obj[key])

    def __getitem__(self, key):
        return self.__dict__.get(key)

