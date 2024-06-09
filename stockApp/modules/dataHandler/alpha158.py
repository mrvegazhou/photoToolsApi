# coding:utf8
from modules.dataHandler.dataHandlerLP import DataHandlerLP

_DEFAULT_LEARN_PROCESSORS = [
    {"class": "DropnaLabel"},
    {"class": "CSZScoreNorm", "kwargs": {"fields_group": "label"}},
]

def check_transform_proc(proc_l, fit_start_time, fit_end_time):
    new_l = []
    for p in proc_l:
        new_l.append(p)
    return new_l

class Alpha158(DataHandlerLP):

    def __init__(
            self,
            instruments="csi500",
            start_time=None,
            end_time=None,
            freq="day",
            infer_processors=[],
            learn_processors=_DEFAULT_LEARN_PROCESSORS,
            fit_start_time=None,
            fit_end_time=None,
            process_type=DataHandlerLP.PTYPE_A,
            filter_pipe=None,
            inst_processors=None,
            **kwargs
    ):
        infer_processors = check_transform_proc(infer_processors, fit_start_time, fit_end_time)
        learn_processors = check_transform_proc(learn_processors, fit_start_time, fit_end_time)

        data_loader = {
            "class": "QlibDataLoader",
            "kwargs": {
                "config": {
                    "feature": self.get_feature_config(),
                    "label": kwargs.pop("label", self.get_label_config()),
                },
                "filter_pipe": filter_pipe,
                "freq": freq,
                "inst_processors": inst_processors,
            },
        }

        super().__init__(
            instruments=instruments,
            start_time=start_time,
            end_time=end_time,
            data_loader=data_loader,
            infer_processors=infer_processors,
            learn_processors=learn_processors,
            process_type=process_type,
            **kwargs
        )