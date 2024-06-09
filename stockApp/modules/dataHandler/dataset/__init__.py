from typing import Callable, Union, List, Tuple, Dict, Text, Optional
import pandas as pd
from copy import copy, deepcopy
from ...common.serial import Serializable
from .handler import DataHandler, DataHandlerLP
from ...common import init_instance_by_config
from .. import D


class Dataset(Serializable):
    """
    Preparing data for model training and inferencing.
    """

    def __init__(self, **kwargs):
        """
        init is designed to finish following steps:

        - init the sub instance and the state of the dataset(info to prepare the data)
            - The name of essential state for preparing data should not start with '_' so that it could be serialized on disk when serializing.

        - setup data
            - The data related attributes' names should start with '_' so that it will not be saved on disk when serializing.

        The data could specify the info to calculate the essential data for preparation
        """
        self.setup_data(**kwargs)
        super().__init__()

    def config(self, **kwargs):
        """
        config is designed to configure and parameters that cannot be learned from the data
        """
        super().config(**kwargs)

    def setup_data(self, **kwargs):
        """
        Setup the data.

        We split the setup_data function for following situation:

        - User have a Dataset object with learned status on disk.

        - User load the Dataset object from the disk.

        - User call `setup_data` to load new data.

        - User prepare data for model based on previous status.
        """

    def prepare(self, **kwargs) -> object:
        """
        The type of dataset depends on the model. (It could be pd.DataFrame, pytorch.DataLoader, etc.)
        The parameters should specify the scope for the prepared data
        The method should:
        - process the data

        - return the processed data

        Returns
        -------
        object:
            return the object
        """


class DatasetH(Dataset):
    """
    Dataset with Data(H)andler

    User should try to put the data preprocessing functions into handler.
    Only following data processing functions should be placed in Dataset:

    - The processing is related to specific model.

    - The processing is related to data split.
    """

    def __init__(
            self,
            handler: Union[Dict, DataHandler],
            segments: Dict[Text, Tuple],
            fetch_kwargs: Dict = {},
            **kwargs,
    ):
        """
        Setup the underlying data.

        Parameters
        ----------
        handler : Union[dict, DataHandler]
            handler could be:

            - instance of `DataHandler`

            - config of `DataHandler`.  Please refer to `DataHandler`

        segments : dict
            Describe the options to segment the data.
            Here are some examples:

            .. code-block::

                1) 'segments': {
                        'train': ("2008-01-01", "2014-12-31"),
                        'valid': ("2017-01-01", "2020-08-01",),
                        'test': ("2015-01-01", "2016-12-31",),
                    }
                2) 'segments': {
                        'insample': ("2008-01-01", "2014-12-31"),
                        'outsample': ("2017-01-01", "2020-08-01",),
                    }
        """
        self.handler: DataHandler = init_instance_by_config(handler, accept_types=DataHandler)
        self.segments = segments.copy()
        self.fetch_kwargs = copy(fetch_kwargs)

        super().__init__(**kwargs)

    def config(self, handler_kwargs: dict = None, **kwargs):
        """
        Initialize the DatasetH

        Parameters
        ----------
        handler_kwargs : dict
            Config of DataHandler, which could include the following arguments:

            - arguments of DataHandler.conf_data, such as 'instruments', 'start_time' and 'end_time'.

        kwargs : dict
            Config of DatasetH, such as

            - segments : dict
                Config of segments which is same as 'segments' in self.__init__

        """
        if handler_kwargs is not None:
            self.handler.config(**handler_kwargs)
        if "segments" in kwargs:
            self.segments = deepcopy(kwargs.pop("segments"))
        super().config(**kwargs)

    def setup_data(self, handler_kwargs: dict = None, **kwargs):
        """
        Setup the Data

        Parameters
        ----------
        handler_kwargs : dict
            init arguments of DataHandler, which could include the following arguments:

            - init_type : Init Type of Handler

            - enable_cache : whether to enable cache

        """
        super().setup_data(**kwargs)
        if handler_kwargs is not None:
            self.handler.setup_data(**handler_kwargs)

    def __repr__(self):
        return "{name}(handler={handler}, segments={segments})".format(
            name=self.__class__.__name__, handler=self.handler, segments=self.segments
        )

    def _prepare_seg(self, slc, **kwargs):
        """
        Give a query, retrieve the according data

        Parameters
        ----------
        slc : please refer to the docs of `prepare`
                NOTE: it may not be an instance of slice. It may be a segment of `segments` from `def prepare`
        """
        if hasattr(self, "fetch_kwargs"):
            return self.handler.fetch(slc, **kwargs, **self.fetch_kwargs)
        else:
            return self.handler.fetch(slc, **kwargs)

    def prepare(
            self,
            segments: Union[List[Text], Tuple[Text], Text, slice, pd.Index],
            col_set=DataHandler.CS_ALL,
            data_key=DataHandlerLP.DK_I,
            **kwargs,
    ) -> Union[List[pd.DataFrame], pd.DataFrame]:
        """
        Prepare the data for learning and inference.

        Parameters
        ----------
        segments : Union[List[Text], Tuple[Text], Text, slice]
            Describe the scope of the data to be prepared
            Here are some examples:

            - 'train'

            - ['train', 'valid']

        col_set : str
            The col_set will be passed to self.handler when fetching data.
            TODO: make it automatic:

            - select DK_I for test data
            - select DK_L for training data.
        data_key : str
            The data to fetch:  DK_*
            Default is DK_I, which indicate fetching data for **inference**.

        kwargs :
            The parameters that kwargs may contain:
                flt_col : str
                    It only exists in TSDatasetH, can be used to add a column of data(True or False) to filter data.
                    This parameter is only supported when it is an instance of TSDatasetH.

        Returns
        -------
        Union[List[pd.DataFrame], pd.DataFrame]:

        Raises
        ------
        NotImplementedError:
        """
        logger = get_module_logger("DatasetH")
        seg_kwargs = {"col_set": col_set}
        seg_kwargs.update(kwargs)
        if "data_key" in getfullargspec(self.handler.fetch).args:
            seg_kwargs["data_key"] = data_key
        else:
            logger.info(f"data_key[{data_key}] is ignored.")

        # Conflictions may happen here
        # - The fetched data and the segment key may both be string
        # To resolve the confliction
        # - The segment name will have higher priorities

        # 1) Use it as segment name first
        if isinstance(segments, str) and segments in self.segments:
            return self._prepare_seg(self.segments[segments], **seg_kwargs)

        if isinstance(segments, (list, tuple)) and all(seg in self.segments for seg in segments):
            return [self._prepare_seg(self.segments[seg], **seg_kwargs) for seg in segments]

        # 2) Use pass it directly to prepare a single seg
        return self._prepare_seg(segments, **seg_kwargs)

    # helper functions
    @staticmethod
    def get_min_time(segments):
        return DatasetH._get_extrema(segments, 0, (lambda a, b: a > b))

    @staticmethod
    def get_max_time(segments):
        return DatasetH._get_extrema(segments, 1, (lambda a, b: a < b))

    @staticmethod
    def _get_extrema(segments, idx: int, cmp: Callable, key_func=pd.Timestamp):
        """it will act like sort and return the max value or None"""
        candidate = None
        for k, seg in segments.items():
            point = seg[idx]
            if point is None:
                # None indicates unbounded, return directly
                return None
            elif candidate is None or cmp(key_func(candidate), key_func(point)):
                candidate = point
        return candidate