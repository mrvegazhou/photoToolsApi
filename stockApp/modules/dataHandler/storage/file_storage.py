# coding:utf8
import struct
from pathlib import Path
from typing import Iterable, Union, Dict, Mapping, Tuple, List, Text

import numpy as np
import pandas as pd

from service.stockGroup.stockGroupService import StockGroupService
from stockApp.modules.common.time import Freq
from stockApp.modules.common.resam import resam_calendar
from stockApp.modules.common.config import C
from ..cache import H
from core.log.logger import get_module_logger
from . import CalendarStorage, InstrumentStorage, FeatureStorage, CalVT, InstKT, InstVT

logger = get_module_logger("file_storage")


class FileStorageMixin:
    """FileStorageMixin, applicable to FileXXXStorage
    Subclasses need to have provider_uri, freq, storage_name, file_name attributes

    """

    # NOTE: provider_uri priority:
    #   1. self._provider_uri : if provider_uri is provided.
    #   2. provider_uri in qlib.config.C

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
            freq_l = filter(
                lambda _freq: not _freq.endswith("_future"),
                map(lambda x: x.stem, self.dpm.get_data_uri(C.DEFAULT_FREQ).joinpath("calendars").glob("*.txt")),
            )
        else:
            freq_l = self.provider_uri.keys()
        freq_l = [Freq(freq) for freq in freq_l]
        setattr(self, _v, freq_l)
        return freq_l

    @property
    def uri(self) -> Path:
        if self.freq not in self.support_freq:
            raise ValueError(f"{self.storage_name}: {self.provider_uri} does not contain data for {self.freq}")
        return self.dpm.get_data_uri(self.freq).joinpath(f"{self.storage_name}s", self.file_name)

    def check(self):
        """check self.uri

        Raises
        -------
        ValueError
        """
        if not self.uri.exists():
            raise ValueError(f"{self.storage_name} not exists: {self.uri}")


class DatabaseCalendarStorage(FileStorageMixin, CalendarStorage):
    def __init__(self, freq: str, future: bool, provider_uri: dict = None, **kwargs):
        super(DatabaseCalendarStorage, self).__init__(freq, future, **kwargs)
        self.future = future
        self.enable_read_cache = True  # TODO: make it configurable
        self._provider_uri = None if provider_uri is None else C.DataPathManager.format_provider_uri(provider_uri)

    @property
    def file_name(self) -> str:
        # future 为期货
        return f"{self._freq_file}_future.txt" if self.future else f"{self._freq_file}.txt".lower()

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

    def _read_calendar(self) -> List[CalVT]:
        # NOTE:
        # if we want to accelerate partial reading calendar
        # we can add parameters like `skip_rows: int = 0, n_rows: int = None` to the interface.
        # Currently, it is not supported for the txt-based calendar
        if not self.uri.exists():
            self._write_calendar(values=[])

        with self.uri.open("r") as fp:
            res = []
            for line in fp.readlines():
                line = line.strip()
                if len(line) > 0:
                    res.append(line)
            return res

    def _write_calendar(self, values: Iterable[CalVT], mode: str = "wb"):
        with self.uri.open(mode=mode) as fp:
            np.savetxt(fp, values, fmt="%s", encoding="utf-8")

    @property
    def uri(self) -> Path:
        return self.dpm.get_data_uri(self._freq_file).joinpath(f"{self.storage_name}s", self.file_name)

    @property
    def data(self) -> List[CalVT]:
        # self.check()
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

    def extend(self, values: Iterable[CalVT]) -> None:
        self._write_calendar(values, mode="ab")

    def clear(self) -> None:
        self._write_calendar(values=[])

    def index(self, value: CalVT) -> int:
        self.check()
        calendar = self._read_calendar()
        return int(np.argwhere(calendar == value)[0])

    def insert(self, index: int, value: CalVT):
        calendar = self._read_calendar()
        calendar = np.insert(calendar, index, value)
        self._write_calendar(values=calendar)

    def remove(self, value: CalVT) -> None:
        self.check()
        index = self.index(value)
        calendar = self._read_calendar()
        calendar = np.delete(calendar, index)
        self._write_calendar(values=calendar)

    def __setitem__(self, i: Union[int, slice], values: Union[CalVT, Iterable[CalVT]]) -> None:
        calendar = self._read_calendar()
        calendar[i] = values
        self._write_calendar(values=calendar)

    def __delitem__(self, i: Union[int, slice]) -> None:
        self.check()
        calendar = self._read_calendar()
        calendar = np.delete(calendar, i)
        self._write_calendar(values=calendar)

    def __getitem__(self, i: Union[int, slice]) -> Union[CalVT, List[CalVT]]:
        self.check()
        return self._read_calendar()[i]

    def __len__(self) -> int:
        return len(self.data)


class DatabaseInstrumentStorage(InstrumentStorage):

    def __init__(self, market: str, freq: str, start_time: Union[pd.Timestamp, str], end_time: Union[pd.Timestamp, str], **kwargs):
        super(DatabaseInstrumentStorage, self).__init__(market, freq, **kwargs)
        self.market = market
        self.start_time = start_time
        self.end_time = end_time

    def _read_instrument(self, start_time: Union[pd.Timestamp, str], end_time: Union[pd.Timestamp, str]) -> Dict[Text, List[Tuple[str, str]]]:
        return StockGroupService.get_stock_code_date_list(self.market, start_time, end_time)

    @property
    def data(self) -> Dict[InstKT, InstVT]:
        return self._read_instrument(self.start_time, self.end_time)

    def __getitem__(self, k: InstKT) -> InstVT:
        return self._read_instrument()[k]

    def __len__(self) -> int:
        return len(self.data)


class FileFeatureStorage(FeatureStorage):
    def __init__(self, instrument: str, field: str, freq: str, provider_uri: dict = None, **kwargs):
        super(FileFeatureStorage, self).__init__(instrument, field, freq, **kwargs)
        self._provider_uri = None if provider_uri is None else C.DataPathManager.format_provider_uri(provider_uri)
        self.file_name = f"{instrument.lower()}/{field.lower()}.{freq.lower()}.bin"

    def clear(self):
        with self.uri.open("wb") as _:
            pass

    @property
    def data(self) -> pd.Series:
        return self[:]

    def write(self, data_array: Union[List, np.ndarray], index: int = None) -> None:
        if len(data_array) == 0:
            logger.info(
                "len(data_array) == 0, write"
                "if you need to clear the FeatureStorage, please execute: FeatureStorage.clear"
            )
            return
        if not self.uri.exists():
            # write
            index = 0 if index is None else index
            with self.uri.open("wb") as fp:
                np.hstack([index, data_array]).astype("<f").tofile(fp)
        else:
            if index is None or index > self.end_index:
                # append
                index = 0 if index is None else index
                with self.uri.open("ab+") as fp:
                    np.hstack([[np.nan] * (index - self.end_index - 1), data_array]).astype("<f").tofile(fp)
            else:
                # rewrite
                with self.uri.open("rb+") as fp:
                    _old_data = np.fromfile(fp, dtype="<f")
                    _old_index = _old_data[0]
                    _old_df = pd.DataFrame(
                        _old_data[1:], index=range(_old_index, _old_index + len(_old_data) - 1), columns=["old"]
                    )
                    fp.seek(0)
                    _new_df = pd.DataFrame(data_array, index=range(index, index + len(data_array)), columns=["new"])
                    _df = pd.concat([_old_df, _new_df], sort=False, axis=1)
                    _df = _df.reindex(range(_df.index.min(), _df.index.max() + 1))
                    _df["new"].fillna(_df["old"]).values.astype("<f").tofile(fp)

    @property
    def start_index(self) -> Union[int, None]:
        if not self.uri.exists():
            return None
        with self.uri.open("rb") as fp:
            index = int(np.frombuffer(fp.read(4), dtype="<f")[0])
        return index

    @property
    def end_index(self) -> Union[int, None]:
        if not self.uri.exists():
            return None
        # The next  data appending index point will be  `end_index + 1`
        return self.start_index + len(self) - 1

    def __getitem__(self, i: Union[int, slice]) -> Union[Tuple[int, float], pd.Series]:
        if not self.uri.exists():
            if isinstance(i, int):
                return None, None
            elif isinstance(i, slice):
                return pd.Series(dtype=np.float32)
            else:
                raise TypeError(f"type(i) = {type(i)}")

        storage_start_index = self.start_index
        storage_end_index = self.end_index
        with self.uri.open("rb") as fp:
            if isinstance(i, int):
                if storage_start_index > i:
                    raise IndexError(f"{i}: start index is {storage_start_index}")
                fp.seek(4 * (i - storage_start_index) + 4)
                return i, struct.unpack("f", fp.read(4))[0]
            elif isinstance(i, slice):
                start_index = storage_start_index if i.start is None else i.start
                end_index = storage_end_index if i.stop is None else i.stop - 1
                si = max(start_index, storage_start_index)
                if si > end_index:
                    return pd.Series(dtype=np.float32)
                fp.seek(4 * (si - storage_start_index) + 4)
                # read n bytes
                count = end_index - si + 1
                data = np.frombuffer(fp.read(4 * count), dtype="<f")
                return pd.Series(data, index=pd.RangeIndex(si, si + len(data)))
            else:
                raise TypeError(f"type(i) = {type(i)}")

    def __len__(self) -> int:
        self.check()
        return self.uri.stat().st_size // 4 - 1
