# coding=utf-8
import pandas as pd

class DataHandler:
    """
        The steps to using a handler
        1. initialized data handler  (call by `init`).
        2. use the data.


        The data handler try to maintain a handler with 2 level.
        `datetime` & `instruments`.

        Any order of the index level can be supported (The order will be implied in the data).
        The order  <`datetime`, `instruments`> will be used when the dataframe index name is missed.

        Example of the data:
        The multi-index of the columns is optional.

        .. code-block:: text

                                    feature                                                            label
                                    $close     $volume  Ref($close, 1)  Mean($close, 3)  $high-$low  LABEL0
            datetime   instrument
            2010-01-04 SH600000    81.807068  17145150.0       83.737389        83.016739    2.741058  0.0032
                       SH600004    13.313329  11800983.0       13.313329        13.317701    0.183632  0.0042
                       SH600005    37.796539  12231662.0       38.258602        37.919757    0.970325  0.0289


        Tips for improving the performance of datahandler
        - Fetching data with `col_set=CS_RAW` will return the raw data and may avoid pandas from copying the data when calling `loc`
        """

    _data: pd.DataFrame  # underlying data.

    def __init__(
            self,
            instruments=None,
            start_time=None,
            end_time=None,
            data_loader: Union[dict, str, DataLoader] = None,
            init_data=True,
            fetch_orig=True,
    ):
        """
        Parameters
        ----------
        instruments :
            The stock list to retrieve.
        start_time :
            start_time of the original data.
        end_time :
            end_time of the original data.
        data_loader : Union[dict, str, DataLoader]
            data loader to load the data.
        init_data :
            initialize the original data in the constructor.
        fetch_orig : bool
            Return the original data instead of copy if possible.
        """

        # Setup data loader
        assert data_loader is not None  # to make start_time end_time could have None default value

        # what data source to load data
        self.data_loader = init_instance_by_config(
            data_loader,
            None if (isinstance(data_loader, dict) and "module_path" in data_loader) else data_loader_module,
            accept_types=DataLoader,
        )

        # what data to be loaded from data source
        # For IDE auto-completion.
        self.instruments = instruments
        self.start_time = start_time
        self.end_time = end_time

        self.fetch_orig = fetch_orig
        if init_data:
            with TimeInspector.logt("Init data"):
                self.setup_data()
        super().__init__()