from modules.common.serial import Serializable
from modules.dataHandler.data import D

class Dataset(Serializable):

    def __init__(self, **kwargs):
        super(Dataset, self).__init__()
        print(D, "====ooo=====")
