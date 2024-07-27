# coding=utf-8
import sys

sys.path.append("/Users/vega/workspace/codes/py_space/working/stockApi")
import sys
import abc
import bisect
import numpy as np
import pandas as pd
# For supporting multiprocessing in outer code, joblib is used
from joblib import delayed
from typing import List, Union, Optional
from stockApp.modules.common.paral import ParallelExt
from stockApp.modules.common import Wrapper, hash_args, normalize_cache_fields
from stockApp.modules.dataHandler.cache import H, DiskDatasetCache
from core.log.logger import get_module_logger
from stockApp.modules.dataHandler.storage.file_storage import FileCalendarStorage, FileInstrumentStorage, FileFeatureStorage
from stockApp.modules.common import parse_field, time_to_slc_point
from stockApp.modules.common.config import C
from stockApp.modules.common import init_instance_by_config
#  eval(parse_field(field)) 这个需要
from .ops import Operators


class CalendarProvider:
    """Calendar provider base class

    Provide calendar data.
    """

    def calendar(self, start_time=None, end_time=None, freq="day"):
        """Get calendar of certain market in given time range.

        Parameters
        ----------
        start_time : str
            start of the time range.
        end_time : str
            end of the time range.
        freq : str
            time frequency, available: year/quarter/month/week/day.
        future : bool
            whether including future trading day.

        Returns
        ----------
        list
            calendar list
        """
        _calendar, _calendar_index = self._get_calendar(freq, start_time, end_time)
        if start_time == "None":
            start_time = None
        if end_time == "None":
            end_time = None
        # strip
        if start_time:
            start_time = pd.Timestamp(start_time)
            if start_time > _calendar[-1]:
                return np.array([])
        else:
            start_time = _calendar[0]
        if end_time:
            end_time = pd.Timestamp(end_time)
            if end_time < _calendar[0]:
                return np.array([])
        else:
            end_time = _calendar[-1]
        _, _, si, ei = self.locate_index(start_time, end_time, freq)
        return _calendar[si : ei + 1]

    def locate_index(
        self, start_time: Union[pd.Timestamp, str], end_time: Union[pd.Timestamp, str], freq: str
    ):
        """Locate the start time index and end time index in a calendar under certain frequency.

        Parameters
        ----------
        start_time : pd.Timestamp
            start of the time range.
        end_time : pd.Timestamp
            end of the time range.
        freq : str
            time frequency, available: year/quarter/month/week/day.
        future : bool
            whether including future trading day.

        Returns
        -------
        pd.Timestamp
            the real start time.
        pd.Timestamp
            the real end time.
        int
            the index of start time.
        int
            the index of end time.
        """
        start_time = pd.Timestamp(start_time)
        end_time = pd.Timestamp(end_time)
        calendar, calendar_index = self._get_calendar(freq=freq, start_time=start_time, end_time=end_time)
        if start_time not in calendar_index:
            try:
                start_time = calendar[bisect.bisect_left(calendar, start_time)]
            except IndexError as index_e:
                raise IndexError(
                    "`start_time` uses a future date, if you want to get future trading days, you can use: `future=True`"
                ) from index_e
        start_index = calendar_index[start_time]
        if end_time not in calendar_index:
            end_time = calendar[bisect.bisect_right(calendar, end_time) - 1]
        end_index = calendar_index[end_time]
        return start_time, end_time, start_index, end_index

    def _get_calendar(self, freq, start_time, end_time):
        """Load calendar using memcache.

        Parameters
        ----------
        freq : str
            frequency of read calendar file.

        Returns
        -------
        list
            list of timestamps.
        dict
            dict composed by timestamp as key and index as value for fast search.
        """
        flag = f"{freq}_"
        if flag not in H["c"]:
            _calendar = np.array(self.load_calendar(freq, start_time, end_time))
            _calendar_index = {x: i for i, x in enumerate(_calendar)}  # for fast search
            H["c"][flag] = _calendar, _calendar_index
        return H["c"][flag]

    def load_calendar(self, freq, start_time, end_time):
        """Load original calendar timestamp from file.

        Parameters
        ----------
        freq : str
            frequency of read calendar file.
        Returns
        ----------
        list
            list of timestamps
        """
        try:
            datas = FileCalendarStorage(freq=freq, start_time=start_time, end_time=end_time).data
        except ValueError:
            raise

        return [pd.Timestamp(x) for x in datas]


class PITProvider:
    # @abc.abstractmethod
    def period_feature(
        self,
        instrument,
        field,
        start_index: int,
        end_index: int,
        cur_time: pd.Timestamp,
        period: Optional[int] = None,
    ) -> pd.Series:
        """
        get the historical periods data series between `start_index` and `end_index`

        Parameters
        ----------
        start_index: int
            start_index is a relative index to the latest period to cur_time

        end_index: int
            end_index is a relative index to the latest period to cur_time
            in most cases, the start_index and end_index will be a non-positive values
            For example, start_index == -3 end_index == 0 and current period index is cur_idx,
            then the data between [start_index + cur_idx, end_index + cur_idx] will be retrieved.

        period: int
            This is used for query specific period.
            The period is represented with int in Qlib. (e.g. 202001 may represent the first quarter in 2020)
            NOTE: `period`  will override `start_index` and `end_index`

        Returns
        -------
        pd.Series
            The index will be integers to indicate the periods of the data
            An typical examples will be
            TODO

        Raises
        ------
        FileNotFoundError
            This exception will be raised if the queried data do not exist.
        """
        if not isinstance(cur_time, pd.Timestamp):
            raise ValueError(
                f"Expected pd.Timestamp for `cur_time`, got '{cur_time}'. Advices: you can't query PIT data directly(e.g. '$$roewa_q'), you must use `P` operator to convert data to each day (e.g. 'P($$roewa_q)')"
            )

        assert end_index <= 0  # PIT don't support querying future data

        DATA_RECORDS = [
            ("date", C.pit_record_type["date"]),
            ("period", C.pit_record_type["period"]),
            ("value", C.pit_record_type["value"]),
            ("_next", C.pit_record_type["index"]),
        ]
        VALUE_DTYPE = C.pit_record_type["value"]

        field = str(field).lower()[2:]

        if not field.endswith("_q") and not field.endswith("_a"):
            raise ValueError("period field must ends with '_q' or '_a'")
        quarterly = field.endswith("_q")
        index_path = C.dpm.get_data_uri() / "financial" / instrument.lower() / f"{field}.index"
        data_path = C.dpm.get_data_uri() / "financial" / instrument.lower() / f"{field}.data"
        if not (index_path.exists() and data_path.exists()):
            raise FileNotFoundError("No file is found.")
        # NOTE: The most significant performance loss is here.
        # Does the acceleration that makes the program complicated really matters?
        # - It makes parameters of the interface complicate
        # - It does not performance in the optimal way (places all the pieces together, we may achieve higher performance)
        #    - If we design it carefully, we can go through for only once to get the historical evolution of the data.
        # So I decide to deprecated previous implementation and keep the logic of the program simple
        # Instead, I'll add a cache for the index file.
        data = np.fromfile(data_path, dtype=DATA_RECORDS)

        # find all revision periods before `cur_time`
        cur_time_int = int(cur_time.year) * 10000 + int(cur_time.month) * 100 + int(cur_time.day)
        loc = np.searchsorted(data["date"], cur_time_int, side="right")
        if loc <= 0:
            return pd.Series(dtype=C.pit_record_type["value"])
        last_period = data["period"][:loc].max()  # return the latest quarter
        first_period = data["period"][:loc].min()
        period_list = get_period_list(first_period, last_period, quarterly)
        if period is not None:
            # NOTE: `period` has higher priority than `start_index` & `end_index`
            if period not in period_list:
                return pd.Series(dtype=C.pit_record_type["value"])
            else:
                period_list = [period]
        else:
            period_list = period_list[max(0, len(period_list) + start_index - 1): len(period_list) + end_index]
        value = np.full((len(period_list),), np.nan, dtype=VALUE_DTYPE)
        for i, p in enumerate(period_list):
            # last_period_index = self.period_index[field].get(period)  # For acceleration
            value[i], now_period_index = read_period_data(
                index_path, data_path, p, cur_time_int, quarterly  # , last_period_index  # For acceleration
            )
            # self.period_index[field].update({period: now_period_index})  # For acceleration
        # NOTE: the index is period_list; So it may result in unexpected values(e.g. nan)
        # when calculation between different features and only part of its financial indicator is published
        series = pd.Series(value, index=period_list, dtype=VALUE_DTYPE)

        return series


class FeatureProvider:
    """Feature provider class

    Provide feature data.
    """

    def feature(self, instrument, field, start_index, end_index, freq):
        """Get feature data.

        Parameters
        ----------
        instrument : str
            a certain instrument.
        field : str
            a certain field of feature.
        start_time : str
            start of the time range.
        end_time : str
            end of the time range.
        freq : str
            time frequency, available: year/quarter/month/week/day.

        Returns
        -------
        pd.Series
            data of a certain feature
        """
        field = str(field)[1:]
        return FileFeatureStorage(instrument=instrument, field=field, freq=freq)[start_index : end_index + 1]


class InstrumentProvider:
    """Instrument provider base class

    Provide instrument data.
    """

    @staticmethod
    def instruments(market: Union[List, str] = "all", filter_pipe: Union[List, None] = None):
        """Get the general config dictionary for a base market adding several dynamic filters.

        Parameters
        ----------
        market : Union[List, str]
            str:
                market/industry/index shortname, e.g. all/sse/szse/sse50/csi300/csi500.
            list:
                ["ID1", "ID2"]. A list of stocks
        filter_pipe : list
            the list of dynamic filters.

        Returns
        ----------
        dict: if isinstance(market, str)
            dict of stockpool config.

            {`market` => base market name, `filter_pipe` => list of filters}

            example :

            .. code-block::

                {'market': 'csi500',
                'filter_pipe': [{'filter_type': 'ExpressionDFilter',
                'rule_expression': '$open<40',
                'filter_start_time': None,
                'filter_end_time': None,
                'keep': False},
                {'filter_type': 'NameDFilter',
                'name_rule_re': 'SH[0-9]{4}55',
                'filter_start_time': None,
                'filter_end_time': None}]}

        list: if isinstance(market, list)
            just return the original list directly.
            NOTE: this will make the instruments compatible with more cases. The user code will be simpler.
        """
        if isinstance(market, list):
            return market
        from .filter import SeriesDFilter  # pylint: disable=C0415

        if filter_pipe is None:
            filter_pipe = []
        config = {"market": market, "filter_pipe": []}
        # the order of the filters will affect the result, so we need to keep
        # the order
        for filter_t in filter_pipe:
            if isinstance(filter_t, dict):
                _config = filter_t
            elif isinstance(filter_t, SeriesDFilter):
                _config = filter_t.to_config()
            else:
                raise TypeError(
                    f"Unsupported filter types: {type(filter_t)}! Filter only supports dict or isinstance(filter, SeriesDFilter)"
                )
            config["filter_pipe"].append(_config)
        return config

    # @abc.abstractmethod
    def list_instruments(self, instruments, start_time=None, end_time=None, freq="day", as_list=False):
        market = instruments["market"]
        if market in H["i"]:
            _instruments = H["i"][market]
        else:
            _instruments = self._load_instruments(market, freq=freq, start_time=start_time, end_time=end_time)
            H["i"][market] = _instruments
        # strip
        # use calendar boundary
        cal = Cal.calendar(freq=freq)
        start_time = pd.Timestamp(start_time or cal[0])
        end_time = pd.Timestamp(end_time or cal[-1])

        _instruments_filtered = {
            inst: list(
                filter(
                    lambda x: x[0] <= x[1],
                    [(max(start_time, pd.Timestamp(x[0])), min(end_time, pd.Timestamp(x[1]))) for x in spans],
                )
            )
            for inst, spans in _instruments.items()
        }
        _instruments_filtered = {key: value for key, value in _instruments_filtered.items() if value}

        # filter
        filter_pipe = instruments["filter_pipe"]
        for filter_config in filter_pipe:
            from . import filter as F  # pylint: disable=C0415

            filter_t = getattr(F, filter_config["filter_type"]).from_config(filter_config)
            _instruments_filtered = filter_t(_instruments_filtered, start_time, end_time, freq)
        # as list
        if as_list:
            return list(_instruments_filtered)
        return _instruments_filtered

    def _load_instruments(self, market, freq, start_time=None, end_time=None):
        return FileInstrumentStorage(market=market, freq=freq).data

    # instruments type
    LIST = "LIST"
    DICT = "DICT"
    CONF = "CONF"

    @classmethod
    def get_inst_type(cls, inst):
        if "market" in inst:
            return cls.CONF
        if isinstance(inst, dict):
            return cls.DICT
        if isinstance(inst, (list, tuple, pd.Index, np.ndarray)):
            return cls.LIST
        raise ValueError(f"Unknown instrument type {inst}")


class DatasetProvider(abc.ABC):
    """Dataset provider class

    Provide Dataset data.
    """

    def __init__(self, align_time: bool = True):
        super().__init__()
        self.align_time = align_time

    def dataset(self, instruments, fields, start_time=None, end_time=None, freq="day", inst_processors=[]):
        """Get dataset data.

        Parameters
        ----------
        instruments : list or dict
            list/dict of instruments or dict of stockpool config.
        fields : list
            list of feature instances.
        start_time : str
            start of the time range.
        end_time : str
            end of the time range.
        freq : str
            time frequency.
        inst_processors:  Iterable[Union[dict, InstProcessor]]
            the operations performed on each instrument

        Returns
        ----------
        pd.DataFrame
            a pandas dataframe with <instrument, datetime> index.
        """
        instruments_d = self.get_instruments_d(instruments, freq, start_time, end_time)
        column_names = self.get_column_names(fields)

        if self.align_time:
            # NOTE: if the frequency is a fixed value.
            # align the data to fixed calendar point
            cal = Cal.calendar(start_time, end_time, freq)
            if len(cal) == 0:
                # 返回空df
                return pd.DataFrame(
                    index=pd.MultiIndex.from_arrays([[], []], names=("instrument", "datetime")), columns=column_names
                )
            start_time = cal[0]
            end_time = cal[-1]

        # 计算列数据
        data = self.dataset_processor(
            instruments_d, column_names, start_time, end_time, freq, inst_processors=inst_processors
        )

        return data

    @staticmethod
    def get_instruments_d(instruments, freq, start_time=None, end_time=None):
        """
        Parse different types of input instruments to output instruments_d
        Wrong format of input instruments will lead to exception.

        """
        if isinstance(instruments, dict):
            if "market" in instruments:
                # dict of stockpool config
                instruments_d = Inst.list_instruments(instruments=instruments, start_time=start_time, end_time=end_time, freq=freq, as_list=False)
            else:
                # dict of instruments and timestamp
                instruments_d = instruments
        elif isinstance(instruments, (list, tuple, pd.Index, np.ndarray)):
            # list or tuple of a group of instruments
            instruments_d = list(instruments)
        else:
            raise ValueError("Unsupported input type for param `instrument`")
        return instruments_d

    @staticmethod
    def get_column_names(fields):
        """
        Get column names from input fields

        """
        if len(fields) == 0:
            raise ValueError("fields cannot be empty")
        column_names = [str(f) for f in fields]
        return column_names

    @staticmethod
    def parse_fields(fields):
        # parse and check the input fields
        return [ExpressionD.get_expression_instance(f) for f in fields]

    @staticmethod
    def dataset_processor(instruments_d, column_names, start_time, end_time, freq, inst_processors=[]):
        """
        Load and process the data, return the data set.
        - default using multi-kernel method.

        """
        normalize_column_names = normalize_cache_fields(column_names)
        # One process for one task, so that the memory will be freed quicker.
        workers = max(min(C.get_kernels(freq), len(instruments_d)), 1)

        # create iterator
        if isinstance(instruments_d, dict):
            it = instruments_d.items()
        else:
            it = zip(instruments_d, [None] * len(instruments_d))

        inst_l = []
        task_l = []
        for inst, spans in it:
            inst_l.append(inst)
            task_l.append(
                delayed(DatasetProvider.inst_calculator)(
                    inst, start_time, end_time, freq, normalize_column_names, spans, C, inst_processors
                )
            )

        data = dict(
            zip(
                inst_l,
                ParallelExt(n_jobs=workers, backend=C.joblib_backend, maxtasksperchild=C.maxtasksperchild)(task_l),
            )
        )

        new_data = dict()
        for inst in sorted(data.keys()):
            if len(data[inst]) > 0:
                # NOTE: Python version >= 3.6; in versions after python3.6, dict will always guarantee the insertion order
                new_data[inst] = data[inst]

        if len(new_data) > 0:
            data = pd.concat(new_data, names=["instrument"], sort=False)
            data = DiskDatasetCache.cache_to_origin_data(data, column_names)
        else:
            # 空值
            data = pd.DataFrame(
                index=pd.MultiIndex.from_arrays([[], []], names=("instrument", "datetime")),
                columns=column_names,
                dtype=np.float32,
            )

        return data

    @staticmethod
    def inst_calculator(inst, start_time, end_time, freq, column_names, spans=None, g_config=None, inst_processors=[]):
        """
        Calculate the expressions for **one** instrument, return a df result.
        If the expression has been calculated before, load from cache.

        return value: A data frame with index 'datetime' and other data columns.

        """
        # FIXME: Windows OS or MacOS using spawn: https://docs.python.org/3.8/library/multiprocessing.html?highlight=spawn#contexts-and-start-methods
        # NOTE: This place is compatible with windows, windows multi-process is spawn
        C.register_from_C(g_config)

        obj = dict()
        for field in column_names:
            #  The client does not have expression provider, the data will be loaded from cache using static method.
            obj[field] = ExpressionD.expression(inst, field, start_time, end_time, freq)

        data = pd.DataFrame(obj)

        if not data.empty and not np.issubdtype(data.index.dtype, np.dtype("M")):
            # If the underlaying provides the data not in datatime formmat, we'll convert it into datetime format
            _calendar = Cal.calendar(freq=freq)
            data.index = _calendar[data.index.values.astype(int)]

        data.index.names = ["datetime"]

        if not data.empty and spans is not None:
            mask = np.zeros(len(data), dtype=bool)
            for begin, end in spans:
                mask |= (data.index >= begin) & (data.index <= end)
            data = data[mask]

        for _processor in inst_processors:
            if _processor:
                _processor_obj = init_instance_by_config(_processor, accept_types=InstProcessor)
                data = _processor_obj(data, instrument=inst)
        return data


class BaseProvider:
    """Local provider class
    It is a set of interface that allow users to access data.
    Because PITD is not exposed publicly to users, so it is not included in the interface.
    To keep compatible with old qlib provider.

    这里默认freq为day
    """

    def calendar(self, start_time=None, end_time=None, freq="day", future=False):
        return Cal.calendar(start_time, end_time, freq, future=future)

    def instruments(self, market="all", filter_pipe=None, start_time=None, end_time=None):
        if start_time is not None or end_time is not None:
            get_module_logger("Provider").warning(
                "The instruments corresponds to a stock pool. "
                "Parameters `start_time` and `end_time` does not take effect now."
            )
        return InstrumentProvider.instruments(market, filter_pipe)

    def list_instruments(self, instruments, start_time=None, end_time=None, freq="day", as_list=False):
        return Inst.list_instruments(instruments, start_time, end_time, freq, as_list)

    def features(
        self,
        instruments,
        fields,
        start_time=None,
        end_time=None,
        freq="day",
        disk_cache=None,
        inst_processors=[],
    ):
        """
        Parameters
        ----------
        disk_cache : int
            whether to skip(0)/use(1)/replace(2) disk_cache


        This function will try to use cache method which has a keyword `disk_cache`,
        and will use provider method if a type error is raised because the DatasetD instance
        is a provider class.
        """
        disk_cache = C.default_disk_cache if disk_cache is None else disk_cache
        # 整个因子字段
        fields = list(fields)
        try:
            return DatasetD.dataset(
                instruments, fields, start_time, end_time, freq, disk_cache, inst_processors=inst_processors
            )
        except TypeError:
            return DatasetD.dataset(instruments, fields, start_time, end_time, freq, inst_processors=inst_processors)


class ExpressionProvider:
    """Expression provider class

    Provide Expression data.
    """

    def __init__(self, time2idx=True):
        self.expression_instance_cache = {}
        self.time2idx = time2idx

    def get_expression_instance(self, field):
        try:
            if field in self.expression_instance_cache:
                expression = self.expression_instance_cache[field]
            else:
                expression = eval(parse_field(field))
                self.expression_instance_cache[field] = expression
        except NameError as e:
            get_module_logger("data").exception(
                "ERROR: field [%s] contains invalid operator/variable [%s]" % (str(field), str(e).split()[1])
            )
            raise
        except SyntaxError:
            get_module_logger("data").exception("ERROR: field [%s] contains invalid syntax" % str(field))
            raise
        return expression

    def expression(self, instrument, field, start_time=None, end_time=None, freq="day") -> pd.Series:
        """Get Expression data.

        The responsibility of `expression`
        - parse the `field` and `load` the according data.
        - When loading the data, it should handle the time dependency of the data. `get_expression_instance` is commonly used in this method

        Parameters
        ----------
        instrument : str
            a certain instrument.
        field : str
            a certain field of feature.
        start_time : str
            start of the time range.
        end_time : str
            end of the time range.
        freq : str
            time frequency, available: year/quarter/month/week/day.

        Returns
        -------
        pd.Series
            data of a certain expression

            The data has two types of format

            1) expression with datetime index

            2) expression with integer index

                - because the datetime is not as good as
        """
        expression = self.get_expression_instance(field)
        start_time = time_to_slc_point(start_time)
        end_time = time_to_slc_point(end_time)

        # Two kinds of queries are supported
        # - Index-based expression: this may save a lot of memory because the datetime index is not saved on the disk
        # - Data with datetime index expression: this will make it more convenient to integrating with some existing databases
        if self.time2idx:
            _, _, start_index, end_index = Cal.locate_index(start_time, end_time, freq=freq)
            lft_etd, rght_etd = expression.get_extended_window_size()
            query_start, query_end = max(0, start_index - lft_etd), end_index + rght_etd
        else:
            start_index, end_index = query_start, query_end = start_time, end_time

        try:
            series = expression.load(instrument, query_start, query_end, freq)
        except Exception as e:
            get_module_logger("data").debug(
                f"Loading expression error: "
                f"instrument={instrument}, field=({field}), start_time={start_time}, end_time={end_time}, freq={freq}. "
                f"error info: {str(e)}"
            )
            raise
        # Ensure that each column type is consistent
        # FIXME:
        # 1) The stock data is currently float. If there is other types of data, this part needs to be re-implemented.
        # 2) The precision should be configurable
        try:
            series = series.astype(np.float32)
        except ValueError:
            pass
        except TypeError:
            pass
        if not series.empty:
            series = series.loc[start_index:end_index]
        return series


if sys.version_info >= (3, 9):
    from typing import Annotated
    InstrumentProviderWrapper = Annotated[InstrumentProvider, Wrapper]
    CalendarProviderWrapper = Annotated[CalendarProvider, Wrapper]
    PITProviderWrapper = Annotated[PITProvider, Wrapper]
    FeatureProviderWrapper = Annotated[FeatureProvider, Wrapper]
    ExpressionProviderWrapper = Annotated[ExpressionProvider, Wrapper]
    DatasetProviderWrapper = Annotated[DatasetProvider, Wrapper]
    BaseProviderWrapper = Annotated[BaseProvider, Wrapper]
else:
    InstrumentProviderWrapper = InstrumentProvider
    CalendarProviderWrapper = CalendarProvider
    PITProviderWrapper = PITProvider
    FeatureProviderWrapper = FeatureProvider
    ExpressionProviderWrapper = ExpressionProvider
    DatasetProviderWrapper = DatasetProvider
    BaseProviderWrapper = BaseProvider

Inst: InstrumentProviderWrapper = Wrapper()
Cal: CalendarProviderWrapper = Wrapper()
PITD: PITProviderWrapper = Wrapper()
FeatureD: FeatureProviderWrapper = Wrapper()
ExpressionD: ExpressionProviderWrapper = Wrapper()
DatasetD: DatasetProviderWrapper = Wrapper()
D: BaseProviderWrapper = Wrapper()


def register_all_wrappers(C):
    """register_all_wrappers"""
    # logger = get_module_logger("modules.dataHandler.data")

    Cal.register(CalendarProvider())

    Inst.register(InstrumentProvider())

    # feature_provider
    FeatureD.register(FeatureProvider())

    # pit_provider
    PITD.register(PITProvider())

    # expression_provider
    ExpressionD.register(ExpressionProvider())

    DatasetD.register(DatasetProvider())

    D.register(BaseProvider())


if __name__ == "__main__":
    from stockApp.modules.common import register_wrapper

    register_wrapper(D, 'BaseProvider', "stockApp.modules.dataHandler.data")
    D.instruments()
    print(D)






