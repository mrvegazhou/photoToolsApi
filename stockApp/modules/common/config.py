# coding:utf8
import copy
import logging
import re
import os
import platform
import multiprocessing
from pathlib import Path
from typing import Optional, Union, Callable

from core.log.logger import get_module_logger  # pylint: disable=C0415


class Config:
    def __init__(self, default_conf):
        self.__dict__["_default_config"] = copy.deepcopy(default_conf)  # avoiding conflicts with __getattr__
        self.reset()

    def __getitem__(self, key):
        return self.__dict__["_config"][key]

    def __getattr__(self, attr):
        if attr in self.__dict__["_config"]:
            return self.__dict__["_config"][attr]

        raise AttributeError(f"No such `{attr}` in self._config")

    def get(self, key, default=None):
        return self.__dict__["_config"].get(key, default)

    def __setitem__(self, key, value):
        self.__dict__["_config"][key] = value

    def __setattr__(self, attr, value):
        self.__dict__["_config"][attr] = value

    def __contains__(self, item):
        return item in self.__dict__["_config"]

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __str__(self):
        return str(self.__dict__["_config"])

    def __repr__(self):
        return str(self.__dict__["_config"])

    def reset(self):
        self.__dict__["_config"] = copy.deepcopy(self._default_config)

    def update(self, *args, **kwargs):
        self.__dict__["_config"].update(*args, **kwargs)

    def set_conf_from_C(self, config_c):
        self.update(**config_c.__dict__["_config"])

    @staticmethod
    def register_from_C(config, skip_register=True):
        from core.log.logger import set_log_with_config  # pylint: disable=C0415

        if C.registered and skip_register:
            return

        C.set_conf_from_C(config)
        if C.logging_config:
            set_log_with_config(C.logging_config)
        C.register()

NUM_USABLE_CPU = max(multiprocessing.cpu_count() - 2, 1)

_default_config = {
    "provider_uri": "/Users/vega/workspace/codes/py_space/working/stockApi/stockApp/crontab/_datas",
    "mount_path": '',
    "h5": 'store.h5',
    # cache
    "expression_cache": None,
    "calendar_cache": None,
    # How many tasks belong to one process. Recommend 1 for high-frequency data and None for daily data.
    "maxtasksperchild": None,

    "kernels": NUM_USABLE_CPU,
    # pickle.dump protocol version
    "dump_protocol_version": 4,

    # If joblib_backend is None, use loky
    "joblib_backend": "multiprocessing",

    "default_disk_cache": 1,  # 0:skip/1:use

    "mem_cache_size_limit": 500,
    "mem_cache_limit_type": "length",
    # memory cache expire second, only in used 'DatasetURICache' and 'client D.calendar'
    # default 1 hour
    "mem_cache_expire": 60 * 60,
    # cache dir name
    "dataset_cache_dir_name": "dataset_cache",
    "features_cache_dir_name": "features_cache",

    # in order to use cache
    "redis_host": "127.0.0.1",
    "redis_port": 6379,
    "redis_task_db": 1,
    "redis_password": None,

    # This value can be reset via qlib.init
    "logging_level": logging.DEBUG,
    # Global configuration of qlib log
    # logging_level can control the logging level more finely
    "logging_config": {
        "version": 1,
        "formatters": {
            "logger_format": {
                "format": "[%(process)s:%(threadName)s](%(asctime)s) %(levelname)s - %(name)s - [%(filename)s:%(lineno)d] - %(message)s"
            }
        },
        "filters": {
            "field_not_found": {
                "()": "core.log.logger.LogFilter",
                "param": [".*?WARN: data not found for.*?"],
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": logging.DEBUG,
                "formatter": "logger_format",
                "filters": ["field_not_found"],
            }
        },
        "loggers": {"stockApp": {"level": logging.DEBUG, "handlers": ["console"]}},
        # To let qlib work with other packages, we shouldn't disable existing loggers.
        # Note that this param is default to True according to the documentation of logging.
        "disable_existing_loggers": False,


    },
    "exp_manager": {
        "uri": "file:" + str(Path(os.getcwd()).resolve() / "crontab/mlruns"),
        "default_exp_name": "Experiment",
    },
}


class QlibConfig(Config):
    # URI_TYPE
    LOCAL_URI = "local"
    NFS_URI = "nfs"
    DEFAULT_FREQ = "__DEFAULT_FREQ"

    def __init__(self, default_conf):
        super().__init__(default_conf)
        self._registered = False

    class DataPathManager:
        def __init__(self, provider_uri: Union[str, Path, dict], mount_path: Union[str, Path, dict]):
            """
            The relation of `provider_uri` and `mount_path`
            - `mount_path` is used only if provider_uri is an NFS path
            - otherwise, provider_uri will be used for accessing data
            """
            self.provider_uri = provider_uri
            self.mount_path = mount_path

        @staticmethod
        def format_provider_uri(provider_uri: Union[str, dict, Path]) -> dict:
            if provider_uri is None:
                raise ValueError("provider_uri cannot be None")
            if isinstance(provider_uri, (str, dict, Path)):
                if not isinstance(provider_uri, dict):
                    provider_uri = {QlibConfig.DEFAULT_FREQ: provider_uri}
            else:
                raise TypeError(f"provider_uri does not support {type(provider_uri)}")
            for freq, _uri in provider_uri.items():
                if QlibConfig.DataPathManager.get_uri_type(_uri) == QlibConfig.LOCAL_URI:
                    provider_uri[freq] = str(Path(_uri).expanduser().resolve())
            return provider_uri

        @staticmethod
        def get_uri_type(uri: Union[str, Path]):
            uri = uri if isinstance(uri, str) else str(uri.expanduser().resolve())
            is_win = re.match("^[a-zA-Z]:.*", uri) is not None  # such as 'C:\\data', 'D:'
            # such as 'host:/data/'   (User may define short hostname by themselves or use localhost)
            is_nfs_or_win = re.match("^[^/]+:.+", uri) is not None

            if is_nfs_or_win and not is_win:
                return QlibConfig.NFS_URI
            else:
                return QlibConfig.LOCAL_URI

        def get_data_uri(self, freq: Optional[Union[str, object]] = None) -> Path:
            """
            please refer DataPathManager's __init__ and class doc
            """
            if freq is not None:
                freq = str(freq)  # converting Freq to string
            if freq is None or freq not in self.provider_uri:
                freq = QlibConfig.DEFAULT_FREQ
            _provider_uri = self.provider_uri[freq]
            if self.get_uri_type(_provider_uri) == QlibConfig.LOCAL_URI:
                return Path(_provider_uri)
            elif self.get_uri_type(_provider_uri) == QlibConfig.NFS_URI:
                if "win" in platform.system().lower():
                    # windows, mount_path is the drive
                    _path = str(self.mount_path[freq])
                    return Path(f"{_path}:\\") if ":" not in _path else Path(_path)
                return Path(self.mount_path[freq])
            else:
                raise NotImplementedError(f"This type of uri is not supported")

    @property
    def dpm(self):
        return self.DataPathManager(self["provider_uri"], self["mount_path"])

    def resolve_path(self):
        # resolve path
        _mount_path = self["mount_path"]

        _provider_uri = self.DataPathManager.format_provider_uri(self["provider_uri"])
        if not isinstance(_mount_path, dict):
            _mount_path = {_freq: _mount_path for _freq in _provider_uri.keys()}

        # check provider_uri and mount_path
        _miss_freq = set(_provider_uri.keys()) - set(_mount_path.keys())
        assert len(_miss_freq) == 0, f"mount_path is missing freq: {_miss_freq}"

        # resolve
        for _freq in _provider_uri.keys():
            # mount_path
            _mount_path[_freq] = (
                _mount_path[_freq] if _mount_path[_freq] is None else str(Path(_mount_path[_freq]).expanduser())
            )
        self["provider_uri"] = _provider_uri
        self["mount_path"] = _mount_path

    def set(self, **kwargs):
        from core.log.logger import set_log_with_config
        self.reset()
        _logging_config = kwargs.get("logging_config", self.logging_config)

        # set global config
        if _logging_config:
            set_log_with_config(_logging_config)

        logger = get_module_logger("Initialization", kwargs.get("logging_level", self.logging_level))

        for k, v in kwargs.items():
            if k not in self:
                logger.warning("Unrecognized config %s" % k)
            self[k] = v

        self.resolve_path()

    @property
    def registered(self):
        return self._registered

    def register(self):
        from ..workflow.expm import MLflowExpManager
        from ..dataHandler.ops import register_all_ops
        from ..dataHandler.data import register_all_wrappers  # pylint: disable=C0415
        from ..workflow import register_R, R  # pylint: disable=C0415
        # from ..workflow.utils import experiment_exit_handler  # pylint: disable=C0415

        register_all_ops(self)
        register_all_wrappers(self)

        register_R(self)
        print(R, '----r-----')
        # # clean up experiment when python program ends
        # experiment_exit_handler()

        self._registered = True

    def get_kernels(self, freq: str):
        """get number of processors given frequency"""
        if isinstance(self["kernels"], Callable):
            return self["kernels"](freq)
        return self["kernels"]

# global config
C = QlibConfig(_default_config)