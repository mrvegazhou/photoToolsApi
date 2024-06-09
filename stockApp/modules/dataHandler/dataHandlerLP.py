# coding=utf-8
import pandas as pd

class DataHandlerLP(DataHandler):
    # based on `self._data`, _infer and _learn are genrated after processors
    _infer: pd.DataFrame  # data for inference
    _learn: pd.DataFrame  # data for learning models

    # data key
    DK_R: DATA_KEY_TYPE = "raw"
    DK_I: DATA_KEY_TYPE = "infer"
    DK_L: DATA_KEY_TYPE = "learn"
    # map data_key to attribute name
    ATTR_MAP = {DK_R: "_data", DK_I: "_infer", DK_L: "_learn"}

    # process type
    PTYPE_I = "independent"
    # - self._infer will be processed by shared_processors + infer_processors
    # - self._learn will be processed by shared_processors + learn_processors

    # NOTE:
    PTYPE_A = "append"

    # - self._infer will be processed by shared_processors + infer_processors
    # - self._learn will be processed by shared_processors + infer_processors + learn_processors
    #   - (e.g. self._infer processed by learn_processors )

    def __init__(
            self,
            instruments=None,
            start_time=None,
            end_time=None,
            data_loader: Union[dict, str, DataLoader] = None,
            infer_processors: List = [],
            learn_processors: List = [],
            shared_processors: List = [],
            process_type=PTYPE_A,
            drop_raw=False,
            **kwargs,
    ):
        """
        Parameters
        ----------
        infer_processors : list
            - list of <description info> of processors to generate data for inference

            - example of <description info>:

            .. code-block::

                1) classname & kwargs:
                    {
                        "class": "MinMaxNorm",
                        "kwargs": {
                            "fit_start_time": "20080101",
                            "fit_end_time": "20121231"
                        }
                    }
                2) Only classname:
                    "DropnaFeature"
                3) object instance of Processor

        learn_processors : list
            similar to infer_processors, but for generating data for learning models

        process_type: str
            PTYPE_I = 'independent'

            - self._infer will be processed by infer_processors

            - self._learn will be processed by learn_processors

            PTYPE_A = 'append'

            - self._infer will be processed by infer_processors

            - self._learn will be processed by infer_processors + learn_processors

              - (e.g. self._infer processed by learn_processors )
        drop_raw: bool
            Whether to drop the raw data
        """

        # Setup preprocessor
        self.infer_processors = []  # for lint
        self.learn_processors = []  # for lint
        self.shared_processors = []  # for lint
        for pname in "infer_processors", "learn_processors", "shared_processors":
            for proc in locals()[pname]:
                getattr(self, pname).append(
                    init_instance_by_config(
                        proc,
                        None if (isinstance(proc, dict) and "module_path" in proc) else processor_module,
                        accept_types=processor_module.Processor,
                    )
                )

        self.process_type = process_type
        self.drop_raw = drop_raw
        super().__init__(instruments, start_time, end_time, data_loader, **kwargs)