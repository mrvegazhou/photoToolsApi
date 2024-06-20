# coding:utf8
import struct
from pathlib import Path
from typing import Iterable, Union, Dict, Mapping, Tuple, List, Text
import re
import numpy as np
import pandas as pd

from service.dayTrading.dayTradingService import DayTradingService
from stockApp.modules.common.time import Freq
from stockApp.modules.common.resam import resam_calendar
from stockApp.modules.common.config import C
from ..cache import H
from core.log.logger import get_module_logger
from . import CalendarStorage, InstrumentStorage, FeatureStorage
from ...common.hepler import get_stock_type

logger = get_module_logger("file_storage")


class FileStorageMixin:
    """FileStorageMixin, applicable to FileXXXStorage
    Subclasses need to have provider_uri, freq, storage_name, file_name attributes

    """

    # NOTE: provider_uri priority:
    #   1. self._provider_uri : if provider_uri is provided.
    #   2. provider_uri in qlib.config.C
    @property
    def store_path(self) -> Path:
        return Path(self.dpm.get_data_uri(C.DEFAULT_FREQ), self.file_name)

    @property
    def file_name(self):
        if 'h5' in C:
            return C['h5']
        else:
            return 'store.h5'

    @property
    def provider_uri(self):
        return C["provider_uri"] if getattr(self, "_provider_uri", None) is None else self._provider_uri

    @property
    def dpm(self):
        return (
            C.dpm
            if getattr(self, "_provider_uri", None) is None
            else C.DataPathManager(self._provider_uri, C.mount_path)
        )

    @property
    def support_freq(self) -> List[str]:
        _v = "_support_freq"
        if hasattr(self, _v):
            return getattr(self, _v)
        # 如果provider_uri内包含__DEFAULT_FREQ 这是默认配置
        if len(self.provider_uri) == 1 and C.DEFAULT_FREQ in self.provider_uri:
            with pd.HDFStore(self.store_path, 'r') as store:
                filtered_keys = [key for key in store.keys() if 'calendars' in key]
                freq_l = [sublist[2] for key in filtered_keys for sublist in [key.split('/')]]
        else:
            freq_l = self.provider_uri.keys()
        freq_l = [Freq(freq) for freq in freq_l]
        setattr(self, _v, freq_l)
        return freq_l

    @property
    def uri(self) -> Path:
        if self.freq not in self.support_freq:
            raise ValueError(f"{self.storage_name}: {self.provider_uri} does not contain data for {self.freq}")
        # get_data_uri方法里包括了config的provider_uri
        return self.dpm.get_data_uri(self.freq).joinpath(self.file_name)

    def check(self):
        """check self.uri

        Raises
        -------
        ValueError
        """
        if not self.uri.exists():
            raise ValueError(f"{self.storage_name} not exists: {self.uri}")


class FileCalendarStorage(FileStorageMixin, CalendarStorage):
    def __init__(self, freq: str, provider_uri: dict = None, **kwargs):
        super(FileCalendarStorage, self).__init__(freq, **kwargs)
        self._provider_uri = None if provider_uri is None else C.DataPathManager.format_provider_uri(provider_uri)
        self.enable_read_cache = True  # TODO: make it configurable
        self.key = f"{self.storage_name}s/{self.freq}"

    @property
    def _freq_file(self) -> str:
        """the freq to read from file"""
        if not hasattr(self, "_freq_file_cache"):
            freq = Freq(self.freq)
            if freq not in self.support_freq:
                # NOTE: uri
                #   1. If `uri` does not exist
                #       - Get the `min_uri` of the closest `freq` under the same "directory" as the `uri`
                #       - Read data from `min_uri` and resample to `freq`

                freq = Freq.get_recent_freq(freq, self.support_freq)
                if freq is None:
                    raise ValueError(f"can't find a freq from {self.support_freq} that can resample to {self.freq}!")
            self._freq_file_cache = freq
        return self._freq_file_cache

    def _read_calendar(self) -> List[str]:
        with pd.HDFStore(self.store_path, mode='r') as store:
            res = []
            if f"/{self.key}" in store.keys():
                df = store[self.key]
                for row in df.itertuples(index=False):
                    res.append(row.date)
                return res
    @property
    def data(self) -> List[str]:
        self.check()
        # If cache is enabled, then return cache directly
        if self.enable_read_cache:
            key = "orig_file" + str(self.uri)
            if key not in H["c"]:
                H["c"][key] = self._read_calendar()
            _calendar = H["c"][key]
        else:
            _calendar = self._read_calendar()
        if Freq(self._freq_file) != Freq(self.freq):
            _calendar = resam_calendar(
                np.array(list(map(pd.Timestamp, _calendar))), self._freq_file, self.freq, self.region
            )
        return _calendar

    def _get_storage_freq(self) -> List[str]:
        return sorted(set(map(lambda x: x.stem.split("_")[0], self.uri.parent.glob("*.txt"))))

    def __getitem__(self, i: Union[int, slice]) -> Union[str, List[str]]:
        self.check()
        return self._read_calendar()[i]

    def __len__(self) -> int:
        return len(self.data)


class FileInstrumentStorage(FileStorageMixin, InstrumentStorage):

    def __init__(self, market: str, freq: str, provider_uri: dict = None, **kwargs):
        super(FileInstrumentStorage, self).__init__(market, freq, **kwargs)
        self._provider_uri = None if provider_uri is None else C.DataPathManager.format_provider_uri(provider_uri)
        self.key = f"{self.storage_name}s/{self.market}"

    def _read_instrument(self) -> Dict[Text, List[Tuple[str, str]]]:
        _instruments = dict()
        with pd.HDFStore(self.store_path, 'r') as store:
            if f"/{self.key}" in store.keys():
                df = store[self.key]
                for row in df.itertuples(index=False):
                    _instruments.setdefault(row[0], []).append((row[1], row[2]))
        return _instruments

    @property
    def data(self) -> Dict[Text, List[Tuple[str, str]]]:
        self.check()
        return self._read_instrument()

    def __getitem__(self, k: Text) -> List[Tuple[str, str]]:
        return self._read_instrument()[k]

    def __len__(self) -> int:
        return len(self.data)


class FileFeatureStorage(FileStorageMixin, FeatureStorage):
    def __init__(self, instrument: str, field: str, freq: str, provider_uri: dict = None, **kwargs):
        super(FileFeatureStorage, self).__init__(instrument, field, freq, **kwargs)
        self._provider_uri = None if provider_uri is None else C.DataPathManager.format_provider_uri(provider_uri)
        prefix = get_stock_type(self.instrument)
        self.key = f"{self.storage_name}s/{prefix}{self.instrument}"

    @property
    def data(self) -> pd.Series:
        #  self[:] 调用了类的 __getitem__ 方法
        return self[:]

    @property
    def start_index(self) -> Union[int, None]:
        with pd.HDFStore(self.store_path, 'r') as store:
            if f"/{self.key}" in store.keys():
                df = store[self.key]
                return df.index.get_level_values('id')[0]
        return None

    @property
    def end_index(self) -> Union[int, None]:
        with pd.HDFStore(self.store_path, 'r') as store:
            if f"/{self.key}" in store.keys():
                df = store[self.key]
                return df.index.get_level_values('id')[-1]
        return None

    def __getitem__(self, i: Union[int, slice]) -> Union[Tuple[int, float], pd.Series]:
        with pd.HDFStore(self.store_path, 'r') as store:
            if f"/{self.key}" not in store.keys():
                if isinstance(i, int):
                    return None, None
                elif isinstance(i, slice):
                    return pd.Series(dtype=np.float32)
                else:
                    raise TypeError(f"type(i) = {type(i)}")
            df = store[self.key]
            # 判断columns是否存在field
            if self.field not in df.columns:
                if isinstance(i, int):
                    return None, None
                elif isinstance(i, slice):
                    return pd.Series(dtype=np.float32)

            storage_start_index = self.start_index
            storage_end_index = self.end_index
            if isinstance(i, int):
                if storage_start_index > i:
                    raise IndexError(f"{i}: start index is {storage_start_index}")
                return i, df[df.index.get_level_values('id')==i][self.field]
            elif isinstance(i, slice):
                start_index = storage_start_index if i.start is None else i.start
                end_index = storage_end_index if i.stop is None else i.stop - 1
                si = max(start_index, storage_start_index)
                if si > end_index:
                    return pd.Series(dtype=np.float32)
                # read n bytes
                level_values = df.index.get_level_values('id')
                df_reset = df[(level_values >= si) & (level_values <= end_index)][self.field]
                df_reset = df_reset.reset_index(level='date', drop=True)
                return df_reset
            else:
                raise TypeError(f"type(i) = {type(i)}")

    def _get_datas(self, i: Union[int, slice]):
        DayTradingService.get_feature_datas(self.instrument)

    def __len__(self) -> int:
        self.check()
        return self.uri.stat().st_size // 4 - 1
