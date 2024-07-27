# coding:utf8
import pandas as pd
from typing import Tuple


def calc_ic(pred: pd.Series, label: pd.Series, date_col="datetime", dropna=False) -> (pd.Series, pd.Series):
    """calc_ic.
    按日期groupby后计算 pred 和 label 这两个序列的 pearson相关性和spearman相关性

    Parameters
    ----------
    pred :
        pred
    label :
        label
    date_col :
        date_col

    Returns
    -------
    (pd.Series, pd.Series)
        ic and rank ic
    """
    df = pd.DataFrame({"pred": pred, "label": label})
    ic = df.groupby(date_col).apply(lambda df: df["pred"].corr(df["label"]))
    ric = df.groupby(date_col).apply(lambda df: df["pred"].corr(df["label"], method="spearman"))
    if dropna:
        return ic.dropna(), ric.dropna()
    else:
        return ic, ric


def calc_long_short_return(
    pred: pd.Series,
    label: pd.Series,
    date_col: str = "datetime",
    quantile: float = 0.2,
    dropna: bool = False,
) -> Tuple[pd.Series, pd.Series]:
    """
    calculate long-short return

    Note:
        `label` must be raw stock returns.

    Parameters
    ----------
    pred : pd.Series
        stock predictions
    label : pd.Series
        stock returns
    date_col : str
        datetime index name
    quantile : float
        long-short quantile

    Returns
    ----------
    long_short_r : pd.Series
        daily long-short returns
    long_avg_r : pd.Series
        daily long-average returns
    """
    df = pd.DataFrame({"pred": pred, "label": label})
    if dropna:
        df.dropna(inplace=True)
    group = df.groupby(level=date_col)

    def N(x):
        return int(len(x) * quantile)

    # 打分的前20%， 与后20% 对应的 真实收益率
    # r_long是买入前20 % 高分的股票的平均收益；
    r_long = group.apply(lambda x: x.nlargest(N(x), columns="pred").label.mean())
    # r_short是买入后20%（低分）的股票的收益；
    r_short = group.apply(lambda x: x.nsmallest(N(x), columns="pred").label.mean())
    r_avg = group.label.mean()
    return (r_long - r_short) / 2, r_avg