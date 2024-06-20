# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import copy


class Normalize1d:
    COLUMNS = ["open", "close", "high", "low", "volume"]
    DAILY_FORMAT = "%Y-%m-%d"
    _date_field_name = 'date'
    _symbol_field_name = 'code'

    def __init__(self, date_field_name: str = "date", symbol_field_name: str = "code", **kwargs):
        self._date_field_name = date_field_name
        self._symbol_field_name = symbol_field_name
        self.kwargs = kwargs

    @staticmethod
    def calc_change(df: pd.DataFrame, last_close: float) -> pd.Series:
        df = df.copy()
        _tmp_series = df["close"].fillna(method="ffill")
        _tmp_shift_series = _tmp_series.shift(1)
        if last_close is not None:
            _tmp_shift_series.iloc[0] = float(last_close)
        change_series = _tmp_series / _tmp_shift_series - 1
        return change_series

    def adjusted_price(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        df = df.copy()
        df.set_index(self._date_field_name, inplace=True)
        if "adjclose" in df:
            df["factor"] = df["adjclose"] / df["close"]
            df["factor"] = df["factor"].fillna(method="ffill")
        else:
            df["factor"] = 1
        for _col in self.COLUMNS:
            if _col not in df.columns:
                continue
            if _col == "volume":
                df[_col] = df[_col] / df["factor"]
            else:
                df[_col] = df[_col] * df["factor"]
        df.index.names = [self._date_field_name]
        return df.reset_index()

    @classmethod
    def get_first_close(cls, df: pd.DataFrame) -> float:
        """get first close value

        Notes
        -----
            For incremental updates(append) to Yahoo 1D data, user need to use a close that is not 0 on the first trading day of the existing data
        """
        df = df.loc[df["close"].first_valid_index():]
        _close = df["close"].iloc[0]
        return _close

    @classmethod
    def manual_adj_data(cls, df: pd.DataFrame) -> pd.DataFrame:
        """manual adjust data: All fields (except change) are standardized according to the close of the first day"""
        if df.empty:
            return df
        df = df.copy()
        df.sort_values(cls._date_field_name, inplace=True)
        df = df.set_index(cls._date_field_name)
        _close = cls.get_first_close(df)

        for _col in df.columns:
            # NOTE: retain original adjclose, required for incremental updates
            if _col in [cls._symbol_field_name, "adjclose", "change", "date"]:
                continue
            if _col == "volume":
                df[_col] = df[_col] * _close
            else:
                df[_col] = df[_col] / _close
        return df.reset_index()

    @staticmethod
    def normalize_(df: pd.DataFrame, calendar_list: list = None, date_field_name: str = "date", symbol_field_name: str = "code", last_close: float = None,):
        if df.empty:
            return df
        symbol = df.loc[df[symbol_field_name].first_valid_index(), symbol_field_name]
        columns = copy.deepcopy(Normalize1d.COLUMNS)
        df = df.copy()
        df.set_index(date_field_name, inplace=True)
        df.index = pd.to_datetime(df.index)
        df.index = df.index.tz_localize(None)
        if calendar_list is not None:
            df = df.reindex(
                pd.DataFrame(index=calendar_list)
                .loc[
                pd.Timestamp(df.index.min()).date(): pd.Timestamp(df.index.max()).date()
                                                     + pd.Timedelta(hours=23, minutes=59)
                ]
                .index
            )
        df.sort_index(inplace=True)
        df["change"] = Normalize1d.calc_change(df, last_close)
        columns += ["change"]
        df.loc[(df["volume"] <= 0) | np.isnan(df["volume"]), columns] = np.nan
        df[symbol_field_name] = symbol
        df.index.names = [date_field_name]
        return df.reset_index()

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self.normalize_(df)
        df = self.adjusted_price(df)
        df = self.manual_adj_data(df)
        return df


    def update_normalized1d(self, df: pd.DataFrame) -> pd.DataFrame:
        '''
        新数据append更新到到旧数据
        '''
        df = self.normalize(df)

        df.set_index(self._date_field_name, inplace=True)
        old_qlib_data = self._get_old_data()
        symbol_name = df[self._symbol_field_name].iloc[0]
        old_symbol_list = old_qlib_data.index.get_level_values("code").unique().to_list()
        if str(symbol_name).upper() not in old_symbol_list:
            return df.reset_index()

        old_df = old_qlib_data.loc[str(symbol_name).upper()]
        latest_date = old_df.index[-1]

        df = df.loc[latest_date:]
        new_latest_data = df.iloc[0]
        old_latest_data = old_df.loc[latest_date]

        for col in self.column_list[:-1]:
            if col == "volume":
                df[col] = df[col] / (new_latest_data[col] / old_latest_data[col])
            else:
                df[col] = df[col] * (old_latest_data[col] / new_latest_data[col])
        return df.drop(df.index[0]).reset_index()






