# -*- coding: utf-8 -*-
from typing import Union
import re
import pandas as pd


def to_numeric(df_values, ignore_columns):
    if isinstance(df_values, pd.DataFrame):
        for column in df_values.columns:
            if column not in ignore_columns:
                df_values[column] = df_values[column].apply(_convert)
    elif isinstance(df_values, pd.Series):
        for index in df_values.index:
            if index not in ignore_columns:
                df_values[index] = _convert(df_values[index])
    return df_values

def _convert(o: Union[str, int, float]) -> Union[str, float, int]:
    if not re.findall('\d', str(o)):
        return o
    try:
        if str(o).isalnum():
            o = int(o)
        else:
            o = float(o)
    except:
        pass
    return o
