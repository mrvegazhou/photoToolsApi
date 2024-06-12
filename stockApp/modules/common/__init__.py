import hashlib
import json
import re
import copy
import redis
from typing import List, Union, Optional, Callable
import numpy as np
import pandas as pd
from packaging import version
from .mod import (
    get_module_by_module_path,
    split_module_path,
    get_callable_kwargs,
    # get_cls_kwargs,
    init_instance_by_config,
    # class_casting,
)


is_deprecated_lexsorted_pandas = version.parse(pd.__version__) > version.parse("1.3.0")


def get_redis_connection():
    from .config import C
    """get redis connection instance."""
    return redis.StrictRedis(
        host=C.redis_host,
        port=C.redis_port,
        db=C.redis_task_db,
        password=C.redis_password,
    )


#################### Wrapper 延迟初始化 #####################
class Wrapper:
    """Wrapper class for anything that needs to set up during qlib.init"""

    def __init__(self):
        self._provider = None

    def register(self, provider):
        self._provider = provider

    def __repr__(self):
        return "{name}(provider={provider})".format(name=self.__class__.__name__, provider=self._provider)

    def __getattr__(self, key):
        if self.__dict__.get("_provider", None) is None:
            raise AttributeError("Please run qlib.init() first using qlib")
        return getattr(self._provider, key)


def register_wrapper(wrapper, cls_or_obj, module_path=None):
    """register_wrapper

    :param wrapper: A wrapper.
    :param cls_or_obj:  A class or class name or object instance.
    """
    if isinstance(cls_or_obj, str):
        module = get_module_by_module_path(module_path)
        cls_or_obj = getattr(module, cls_or_obj)
    obj = cls_or_obj() if isinstance(cls_or_obj, type) else cls_or_obj
    wrapper.register(obj)


def hash_args(*args):
    # json.dumps will keep the dict keys always sorted.
    string = json.dumps(args, sort_keys=True, default=str)  # frozenset
    return hashlib.md5(string.encode()).hexdigest()


def lazy_sort_index(df: pd.DataFrame, axis=0) -> pd.DataFrame:
    """
    这个函数可以避免在索引已经排序的情况下进行排序
    make the df index sorted

    df.sort_index() will take a lot of time even when `df.is_lexsorted() == True`
    This function could avoid such case

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame:
        sorted dataframe
    """
    idx = df.index if axis == 0 else df.columns
    if (
        not idx.is_monotonic_increasing
        or not is_deprecated_lexsorted_pandas
        and isinstance(idx, pd.MultiIndex)
        and not idx.is_lexsorted()
    ):  # this case is for the old version
        return df.sort_index(axis=axis)
    else:
        return df


def parse_field(field):
    # Following patterns will be matched:
    # - $close -> Feature("close")
    # - $close5 -> Feature("close5")
    # - $open+$close -> Feature("open")+Feature("close")
    # TODO: this maybe used in the feature if we want to support the computation of different frequency data
    # - $close@5min -> Feature("close", "5min")

    if not isinstance(field, str):
        field = str(field)
    # Chinese punctuation regex:
    # \u3001 -> 、
    # \uff1a -> ：
    # \uff08 -> (
    # \uff09 -> )
    chinese_punctuation_regex = r"\u3001\uff1a\uff08\uff09"
    for pattern, new in [
        (
            rf"\$\$([\w{chinese_punctuation_regex}]+)",
            r'PFeature("\1")',
        ),  # $$ must be before $
        (rf"\$([\w{chinese_punctuation_regex}]+)", r'Feature("\1")'),
        (r"(\w+\s*)\(", r"Operators.\1("),
    ]:  # Features  # Operators
        field = re.sub(pattern, new, field)
    return field


def time_to_slc_point(t: Union[None, str, pd.Timestamp]) -> Union[None, pd.Timestamp]:
    """
    Time slicing in Qlib or Pandas is a frequently-used action.
    However, user often input all kinds of data format to represent time.
    This function will help user to convert these inputs into a uniform format which is friendly to time slicing.

    Parameters
    ----------
    t : Union[None, str, pd.Timestamp]
        original time

    Returns
    -------
    Union[None, pd.Timestamp]:
    """
    if t is None:
        # None represents unbounded in Qlib or Pandas(e.g. df.loc[slice(None, "20210303")]).
        return t
    else:
        return pd.Timestamp(t)


def remove_repeat_field(fields):
    """remove repeat field

    :param fields: list; features fields
    :return: list
    """
    fields = copy.deepcopy(fields)
    _fields = set(fields)
    return sorted(_fields, key=fields.index)


def remove_fields_space(fields: [list, str, tuple]):
    """remove fields space

    :param fields: features fields
    :return: list or str
    """
    if isinstance(fields, str):
        return fields.replace(" ", "")
    return [i.replace(" ", "") if isinstance(i, str) else str(i) for i in fields]


def normalize_cache_fields(fields: [list, tuple]):
    """normalize cache fields

    :param fields: features fields
    :return: list
    """
    return sorted(remove_repeat_field(remove_fields_space(fields)))


def normalize_cache_instruments(instruments):
    """normalize cache instruments

    :return: list or dict
    """
    if isinstance(instruments, (list, tuple, pd.Index, np.ndarray)):
        instruments = sorted(list(instruments))
    else:
        # dict type stockpool
        if "market" in instruments:
            pass
        else:
            instruments = {k: sorted(v) for k, v in instruments.items()}
    return instruments