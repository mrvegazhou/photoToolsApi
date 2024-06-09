# coding: utf-8
"""
日志插件
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
处理日志相关配置
"""
import os
from logging import handlers, Formatter
from time import time
from flask.logging import default_handler
from typing import Optional, Text, Dict, Any
from contextlib import contextmanager
import logging
from logging import config as logging_config


class Logger(object):
    def __init__(self, app=None, log_dir=None, log_level=None, log_keep_day=None):
        self.log_dir = "logs"
        self.log_level = 20     # CRITICAL:50,ERROR:40,WARNING:30,INFO:20,DEBUG:10,NOTSET:0
        self.log_keep_day = 30

        self.app = app
        if app is not None:
            self.init_app(app, log_dir, log_level, log_keep_day)

    def init_app(self, app, log_dir=None, log_level=None, log_keep_day=None):
        # 移除缺省的日志记录器
        app.logger.removeHandler(default_handler)

        self.log_dir = log_dir if log_dir else app.config.get("LOG_DIR", self.log_dir)
        self.log_level = log_level if log_level else app.config.get("LOG_LEVEL", self.log_level)
        self.log_keep_day = log_keep_day if log_keep_day else app.config.get("LOG_KEEP_DAY", self.log_keep_day)

        if self.log_dir.startswith("/"):
            log_path = os.path.normpath(self.log_dir)
        else:
            log_path = os.path.normpath(os.path.join(app.root_path, '../', self.log_dir))
        if not os.path.isdir(log_path):
            try:
                os.makedirs(log_path)
            except Exception as e:
                raise e

        formatter = Formatter('%(asctime)s|%(levelname)s|%(pathname)s(%(lineno)d)|%(funcName)s|%(message)s')
        log_file = os.path.join(log_path, app.name + '.log')
        log_file_handler = handlers.TimedRotatingFileHandler(log_file, when="D", backupCount=self.log_keep_day)
        log_file_handler.setFormatter(formatter)
        app.logger.addHandler(log_file_handler)
        app.logger.setLevel(int(self.log_level))


class MetaLogger(type):
    def __new__(mcs, name, bases, attrs):  # pylint: disable=C0204
        wrapper_dict = logging.Logger.__dict__.copy()
        for key, val in wrapper_dict.items():
            if key not in attrs and key != "__reduce__":
                attrs[key] = val
        return type.__new__(mcs, name, bases, attrs)


class StockLogger(metaclass=MetaLogger):
    """
    Customized logger for Qlib.
    """

    def __init__(self, module_name):
        self.module_name = module_name
        # this feature name conflicts with the attribute with Logger
        # rename it to avoid some corner cases that result in comparing `str` and `int`
        self.__level = 0

    @property
    def logger(self):
        logger = logging.getLogger(self.module_name)
        logger.setLevel(self.__level)
        return logger

    def setLevel(self, level):
        self.__level = level

    def __getattr__(self, name):
        # During unpickling, python will call __getattr__. Use this line to avoid maximum recursion error.
        if name in {"__setstate__"}:
            raise AttributeError
        return self.logger.__getattribute__(name)


class _LoggerManager:
    def __init__(self):
        self._loggers = {}

    def setLevel(self, level):
        for logger in self._loggers.values():
            logger.setLevel(level)

    def __call__(self, module_name, level: Optional[int] = None) -> StockLogger:
        """
        Get a logger for a specific module.

        :param module_name: str
            Logic module name.
        :param level: int
        :return: Logger
            Logger object.
        """
        if level is None:
            level = logging.INFO

        if not module_name.startswith("stockApp."):
            # Add a prefix of qlib. when the requested ``module_name`` doesn't start with ``qlib.``.
            # If the module_name is already qlib.xxx, we do not format here. Otherwise, it will become qlib.qlib.xxx.
            module_name = "stockApp.{}".format(module_name)

        # Get logger.
        module_logger = self._loggers.setdefault(module_name, StockLogger(module_name))
        module_logger.setLevel(level)
        return module_logger


get_module_logger = _LoggerManager()


class TimeInspector:
    timer_logger = get_module_logger("timer")

    time_marks = []

    @classmethod
    def set_time_mark(cls):
        """
        Set a time mark with current time, and this time mark will push into a stack.
        :return: float
            A timestamp for current time.
        """
        _time = time()
        cls.time_marks.append(_time)
        return _time

    @classmethod
    def pop_time_mark(cls):
        """
        Pop last time mark from stack.
        """
        return cls.time_marks.pop()

    @classmethod
    def get_cost_time(cls):
        """
        Get last time mark from stack, calculate time diff with current time.
        :return: float
            Time diff calculated by last time mark with current time.
        """
        cost_time = time() - cls.time_marks.pop()
        return cost_time

    @classmethod
    def log_cost_time(cls, info="Done"):
        """
        Get last time mark from stack, calculate time diff with current time, and log time diff and info.
        :param info: str
            Info that will be logged into stdout.
        """
        cost_time = time() - cls.time_marks.pop()
        cls.timer_logger.info("Time cost: {0:.3f}s | {1}".format(cost_time, info))

    @classmethod
    @contextmanager
    def logt(cls, name="", show_start=False):
        """logt.
        Log the time of the inside code

        Parameters
        ----------
        name :
            name
        show_start :
            show_start
        """
        if show_start:
            cls.timer_logger.info(f"{name} Begin")
        cls.set_time_mark()
        try:
            yield None
        finally:
            pass
        cls.log_cost_time(info=f"{name} Done")


def set_log_with_config(log_config: Dict[Text, Any]):
    """set log with config

    :param log_config:
    :return:
    """
    logging_config.dictConfig(log_config)


class LogFilter(logging.Filter):
    def __init__(self, param=None):
        super().__init__()
        self.param = param

    @staticmethod
    def match_msg(filter_str, msg):
        match = False
        try:
            if re.match(filter_str, msg):
                match = True
        except Exception:
            pass
        return match

    def filter(self, record):
        allow = True
        if isinstance(self.param, str):
            allow = not self.match_msg(self.param, record.msg)
        elif isinstance(self.param, list):
            allow = not any(self.match_msg(p, record.msg) for p in self.param)
        return allow

