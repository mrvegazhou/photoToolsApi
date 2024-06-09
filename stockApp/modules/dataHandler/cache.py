# coding:utf8
from ..common.config import C
import os
import sys
import stat
import time
import pickle
import traceback
import redis_lock
import contextlib
import abc
from pathlib import Path
import numpy as np
import pandas as pd
from typing import Union, Iterable
from collections import OrderedDict


class MemCacheUnit(abc.ABC):
    """Memory Cache Unit."""

    def __init__(self, *args, **kwargs):
        self.size_limit = kwargs.pop("size_limit", 0)
        self._size = 0
        self.od = OrderedDict()

    def __setitem__(self, key, value):
        # 此方法重载了 [] 操作符
        # TODO: thread safe?__setitem__ failure might cause inconsistent size?

        # precalculate the size after od.__setitem__
        self._adjust_size(key, value)

        self.od.__setitem__(key, value)

        # move the key to end,make it latest
        self.od.move_to_end(key)

        if self.limited:
            # pop the oldest items beyond size limit
            while self._size > self.size_limit:
                self.popitem(last=False)

    def __getitem__(self, key):
        # 此方法重载了 [] 操作符，用于获取缓存中的值。它还会将访问的键移动到 OrderedDict 的末尾。
        v = self.od.__getitem__(key)
        self.od.move_to_end(key)
        return v

    def __contains__(self, key):
        return key in self.od

    def __len__(self):
        return self.od.__len__()

    def __repr__(self):
        return f"{self.__class__.__name__}<size_limit:{self.size_limit if self.limited else 'no limit'} total_size:{self._size}>\n{self.od.__repr__()}"

    def set_limit_size(self, limit):
        self.size_limit = limit

    @property
    def limited(self):
        """whether memory cache is limited"""
        return self.size_limit > 0

    @property
    def total_size(self):
        return self._size

    def clear(self):
        self._size = 0
        self.od.clear()

    def popitem(self, last=True):
        k, v = self.od.popitem(last=last)
        self._size -= self._get_value_size(v)

        return k, v

    def pop(self, key):
        v = self.od.pop(key)
        self._size -= self._get_value_size(v)

        return v

    def _adjust_size(self, key, value):
        if key in self.od:
            self._size -= self._get_value_size(self.od[key])

        self._size += self._get_value_size(value)

    @abc.abstractmethod
    def _get_value_size(self, value):
        # 获取缓存项的大小
        raise NotImplementedError


class MemCacheLengthUnit(MemCacheUnit):
    def __init__(self, size_limit=0):
        super().__init__(size_limit=size_limit)

    def _get_value_size(self, value):
        return 1


class MemCacheSizeofUnit(MemCacheUnit):
    def __init__(self, size_limit=0):
        super().__init__(size_limit=size_limit)

    def _get_value_size(self, value):
        return sys.getsizeof(value)


class MemCache:
    """Memory cache."""

    def __init__(self, mem_cache_size_limit=None, limit_type="length"):
        """

        Parameters
        ----------
        mem_cache_size_limit:
            cache max size.
        limit_type:
            length or sizeof; length(call fun: len), size(call fun: sys.getsizeof).
        """

        size_limit = C.mem_cache_size_limit if mem_cache_size_limit is None else mem_cache_size_limit
        limit_type = C.mem_cache_limit_type if limit_type is None else limit_type

        if limit_type == "length":
            klass = MemCacheLengthUnit
        elif limit_type == "sizeof":
            klass = MemCacheSizeofUnit
        else:
            raise ValueError(f"limit_type must be length or sizeof, your limit_type is {limit_type}")

        self.__calendar_mem_cache = klass(size_limit)
        self.__instrument_mem_cache = klass(size_limit)
        self.__feature_mem_cache = klass(size_limit)

    def __getitem__(self, key):
        if key == "c":
            return self.__calendar_mem_cache
        elif key == "i":
            return self.__instrument_mem_cache
        elif key == "f":
            return self.__feature_mem_cache
        else:
            raise KeyError("Unknown memcache unit")

    def clear(self):
        self.__calendar_mem_cache.clear()
        self.__instrument_mem_cache.clear()
        self.__feature_mem_cache.clear()

H = MemCache()
