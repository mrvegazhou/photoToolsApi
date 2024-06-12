# coding=utf-8
from core.log.logger import get_module_logger
from stockApp.modules.common.config import C
from stockApp.modules.dataHandler.cache import H


def init(**kwargs):

    logger = get_module_logger("Initialization")

    skip_if_reg = kwargs.pop("skip_if_reg", False)
    if skip_if_reg and C.registered:
        # if we reinitialize Qlib during running an experiment `R.start`.
        # it will result in loss of the recorder
        logger.warning("Skip initialization because `skip_if_reg is True`")
        return

    clear_mem_cache = kwargs.pop("clear_mem_cache", True)
    if clear_mem_cache:
        H.clear()

    C.set(**kwargs)
    get_module_logger.setLevel(C.logging_level)
    C.register()

    logger.info("stock app successfully initialized based on settings.")