# coding:utf8
from .daykline import DayKline
from .sina import Sina
from .jsl import Jsl
from .timekline import TimeKline

# pylint: disable=too-many-return-statements
def use(source):
    if source in ["sina"]:
        return Sina()
    if source in ["jsl"]:
        return Jsl()
    if source in ["timekline"]:
        return TimeKline()
    if source in ["daykline"]:
        return DayKline()
    raise NotImplementedError