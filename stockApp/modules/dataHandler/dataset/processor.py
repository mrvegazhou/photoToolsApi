import abc
from typing import Union, Text, Optional
import pandas as pd
from ...common.serial import Serializable
from ...common.data import zscore, robust_zscore


def get_group_columns(df: pd.DataFrame, group: Union[Text, None]):
    """
    get a group of columns from multi-index columns DataFrame

    Parameters
    ----------
    df : pd.DataFrame
        with multi of columns.
    group : str
        the name of the feature group, i.e. the first level value of the group index.
    """
    if group is None:
        return df.columns
    else:
        return df.columns[df.columns.get_loc(group)]


class Processor(Serializable):
    def fit(self, df: pd.DataFrame = None):
        """
        learn data processing parameters

        Parameters
        ----------
        df : pd.DataFrame
            When we fit and process data with processor one by one. The fit function reiles on the output of previous
            processor, i.e. `df`.

        """

    @abc.abstractmethod
    def __call__(self, df: pd.DataFrame):
        """
        process the data

        NOTE: **The processor could change the content of `df` inplace !!!!! **
        User should keep a copy of data outside

        Parameters
        ----------
        df : pd.DataFrame
            The raw_df of handler or result from previous processor.
        """

    def is_for_infer(self) -> bool:
        """
        Is this processor usable for inference
        Some processors are not usable for inference.

        Returns
        -------
        bool:
            if it is usable for infenrece.
        """
        return True

    def readonly(self) -> bool:
        """
        Does the processor treat the input data readonly (i.e. does not write the input data) when processing

        Knowning the readonly information is helpful to the Handler to avoid uncessary copy
        """
        return False

    def config(self, **kwargs):
        attr_list = {"fit_start_time", "fit_end_time"}
        for k, v in kwargs.items():
            if k in attr_list and hasattr(self, k):
                setattr(self, k, v)

        for attr in attr_list:
            if attr in kwargs:
                kwargs.pop(attr)
        super().config(**kwargs)


class DropnaProcessor(Processor):
    def __init__(self, fields_group=None):
        self.fields_group = fields_group

    def __call__(self, df):
        return df.dropna(subset=get_group_columns(df, self.fields_group))

    def readonly(self):
        return True


class DropnaLabel(DropnaProcessor):
    def __init__(self, fields_group="label"):
        super().__init__(fields_group=fields_group)

    def is_for_infer(self) -> bool:
        """The samples are dropped according to label. So it is not usable for inference"""
        return False


class CSZScoreNorm(Processor):
    """Cross Sectional ZScore Normalization"""

    def __init__(self, fields_group=None, method="zscore"):
        self.fields_group = fields_group
        if method == "zscore":
            self.zscore_func = zscore
        elif method == "robust":
            self.zscore_func = robust_zscore
        else:
            raise NotImplementedError(f"This type of input is not supported")

    def __call__(self, df):
        # try not modify original dataframe
        if not isinstance(self.fields_group, list):
            self.fields_group = [self.fields_group]
        # depress warning by references:
        # https://stackoverflow.com/questions/20625582/how-to-deal-with-settingwithcopywarning-in-pandas
        # https://pandas.pydata.org/pandas-docs/stable/user_guide/options.html#getting-and-setting-options
        with pd.option_context("mode.chained_assignment", None):
            for g in self.fields_group:
                cols = get_group_columns(df, g)
                df[cols] = df[cols].groupby("datetime", group_keys=False).apply(self.zscore_func)
        return df
