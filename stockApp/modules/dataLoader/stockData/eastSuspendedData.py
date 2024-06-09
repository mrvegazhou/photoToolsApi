# -*- coding: utf-8 -*-
import pandas as pd
from .stockDataBase import StockDataBase
from ..config.stockDataConst import Constants, EastConfig


class EastSuspendedData(StockDataBase):
    ''' 停牌 '''

    @property
    def stock_api(self) -> str:
        return Constants.SUSPENDED_URL.value

    def get_suspended_data(self, date: str = "20240603") -> pd.DataFrame:
        data_df = self._fetch_stock_data(date)
        return self._format_response_data(data_df)

    def _fetch_stock_data(self, date: str) -> pd.DataFrame:
        params = {
            "sortColumns": "SUSPEND_START_DATE",
            "sortTypes": "-1",
            "pageSize": "500",
            "pageNumber": "1",
            "reportName": "RPT_CUSTOM_SUSPEND_DATA_INTERFACE",
            "columns": "ALL",
            "source": "WEB",
            "client": "WEB",
            "filter": f"""(MARKET="全部")(DATETIME='{"-".join([date[:4], date[4:6], date[6:]])}')""",
        }
        r = self._session.get(self.stock_api, params=params)
        data_json = r.json()
        total_page = data_json["result"]["pages"]
        big_df = pd.DataFrame()
        for page in range(1, total_page + 1):
            params.update({"pageNumber": page})
            r = self._session.get(self.stock_api, params=params)
            data_json = r.json()
            temp_df = pd.DataFrame(data_json["result"]["data"])
            big_df = pd.concat(objs=[big_df, temp_df], ignore_index=True)
        return big_df

    def _format_response_data(self, big_df: pd.DataFrame) -> pd.DataFrame:
        big_df.reset_index(inplace=True)
        column_list = EastConfig.suspended_info_dict.value
        keys_column_list = list(column_list.keys())
        big_df.columns = keys_column_list + [
            "-",
            "-",
        ]
        big_df = big_df[
            keys_column_list
        ]

        # big_df.loc[:, "suspended_date"] = pd.to_datetime(big_df["suspended_date"], errors="coerce").dt.date
        # big_df.loc[:, "suspended_deadline"] = pd.to_datetime(big_df["suspended_deadline"], errors="coerce").dt.date
        # big_df.loc[:, "suspended_end_date"] = pd.to_datetime(big_df["suspended_end_date"], errors="coerce").dt.date
        return big_df