# coding:utf8
from pathlib import Path
import pandas as pd
from loguru import logger
from modules.dataHandler.cache import CacheUtils
from ..common import get_redis_connection
from ..common.hepler import get_stock_type


class DumpDataBase:
    INSTRUMENTS_START_FIELD = "start_datetime"
    INSTRUMENTS_END_FIELD = "end_datetime"
    DAILY_FORMAT = "%Y-%m-%d"
    HIGH_FREQ_FORMAT = "%Y-%m-%d %H:%M:%S"
    CALENDARS_DIR_NAME = "calendars"
    FEATURES_DIR_NAME = "features"
    INSTRUMENTS_DIR_NAME = "instruments"
    symbol_field_name: str = "code"
    H5_NAME = 'store.h5'

    def __init__(
        self,
        stock_app_dir: str,
        freq: str = "day",
        market: str = "all",
        max_workers: int = 2,
        date_field_name: str = "date",
        symbol_field_name: str = "code",
    ):
        # self.provider: DayTradingService = DayTradingService()
        self.stock_app_dir = Path(stock_app_dir).expanduser()
        self.freq = freq
        self.market = market
        self.date_field_name = date_field_name
        self.calendar_format = self.DAILY_FORMAT if self.freq == "day" else self.HIGH_FREQ_FORMAT
        self._calendars_list = []

        self._h5_dir = self.stock_app_dir
        self.symbol_field_name = symbol_field_name
        self.works = max_workers
        self.r = get_redis_connection()

    def _format_datetime(self, datetime_d: [str, pd.Timestamp]):
        datetime_d = pd.Timestamp(datetime_d)
        return datetime_d.strftime(self.calendar_format)

    def save_calendars(self, df: pd.DataFrame):
        self._h5_dir.mkdir(parents=True, exist_ok=True)
        hdf5_path = Path(self._h5_dir, self.H5_NAME)
        lock_name = f"{self.stock_app_dir}:{self.CALENDARS_DIR_NAME}"
        if df.empty:
            logger.error("calendars df is empty.")
        else:
            df['date'] = pd.to_datetime(df['date']).dt.strftime(self.calendar_format)
            with CacheUtils.writer_lock(self.r, lock_name):
                try:
                    df.rename(columns={'trading_date': self.date_field_name}, inplace=True)
                    df[self.date_field_name] = pd.to_datetime(df[self.date_field_name])
                    df.sort_values(by=self.date_field_name, inplace=True)
                    idx = range(len(df))
                    df = df.reindex(idx)
                    key = f"{self.CALENDARS_DIR_NAME}/{self.freq}"
                    store = pd.HDFStore(hdf5_path, mode='a')
                    if f"/{key}" in store.keys():
                        store.remove(key)
                    store.put(key, df, format='table', data_columns=True)
                except Exception as e:
                    print(f"Save calendars an error occurred: {e}")
                finally:
                    if 'store' in locals():
                        store.close()

    def data_merge_calendar(self, df: pd.DataFrame, calendars_df: pd.DataFrame) -> pd.DataFrame:
        # calendars
        # calendars_df[self.date_field_name] = calendars_df[self.date_field_name].astype("datetime64[ns]")
        calendars_df['id'] = range(len(calendars_df))
        cal_df = calendars_df[
            (calendars_df[self.date_field_name] >= df[self.date_field_name].min())
            & (calendars_df[self.date_field_name] <= df[self.date_field_name].max())
            ]

        # align index
        cal_df = cal_df.sort_values(by=self.date_field_name)
        cal_df.set_index(self.date_field_name, inplace=True)
        df.set_index(self.date_field_name, inplace=True)
        df['id'] = pd.to_numeric(cal_df.loc[cal_df.index.values, 'id'], downcast='integer')
        r_df = df.reindex(cal_df.index)
        r_df.set_index('id', append=True, inplace=True)
        return r_df

    def save_instruments(self, instruments_data: pd.DataFrame, name='all'):
        self._h5_dir.mkdir(parents=True, exist_ok=True)
        hdf5_path = Path(self._h5_dir, self.H5_NAME)
        _df_fields = [self.symbol_field_name, self.INSTRUMENTS_START_FIELD, self.INSTRUMENTS_END_FIELD]
        instruments_data = instruments_data.loc[:, _df_fields]
        lock_name = f"{self.stock_app_dir}:{self.INSTRUMENTS_DIR_NAME}"
        if instruments_data.empty:
            logger.error("instruments df is empty.")
        else:
            with CacheUtils.writer_lock(self.r, lock_name):
                try:
                    key = f"{self.INSTRUMENTS_DIR_NAME}/{name}"
                    store = pd.HDFStore(hdf5_path, mode='a')
                    if f"/{key}" in store.keys():
                        store.remove(key)
                    store.put(key, instruments_data, format='table', data_columns=True)
                except Exception as e:
                    print(f"Save instruments an error occurred: {e}")
                finally:
                    if 'store' in locals():
                        store.close()

    def save_features(self, instrument: str, feature_df: pd.DataFrame, calendar_df: pd.DataFrame):
        self._h5_dir.mkdir(parents=True, exist_ok=True)
        if not instrument:
            logger.warning("instrument data is None or empty")
            return
        if feature_df.empty:
            logger.warning(f"{instrument} feature data is None or empty")
            return
        if calendar_df.empty:
            logger.warning("calendar is empty")
            return
        feature_df = feature_df.drop_duplicates(subset=['date'])
        # align index
        _df = self.data_merge_calendar(feature_df, calendar_df)
        if _df.empty:
            logger.warning("Features data is not in calendars")
            return
        hdf5_path = Path(self._h5_dir, self.H5_NAME)
        lock_name = f"{self.stock_app_dir}:{self.FEATURES_DIR_NAME}:{instrument}"
        with CacheUtils.writer_lock(self.r, lock_name):
            try:
                store = pd.HDFStore(hdf5_path, mode='a')
                prefix = get_stock_type(instrument)
                key = f"{self.FEATURES_DIR_NAME}/{prefix}{instrument}"
                if f"/{key}" in store.keys():
                    store.remove(key)
                store.put(key, _df, format='table', data_columns=True)
            except Exception as e:
                print(f"Save features an error occurred: {key} {e}")
            finally:
                if 'store' in locals():
                    store.close()



