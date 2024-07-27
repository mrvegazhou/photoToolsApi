import sys, datetime

from dao.dayTrading import DayTrading
from modules.dataHandler.normalize1d import Normalize1d
from modules.dataLoader.stockData.eastIntradayData import EastIntradayData

sys.path.append("/Users/vega/workspace/codes/py_space/working/stockApi")
import pandas as pd
from pathlib import Path
import pickle
from concurrent.futures import ThreadPoolExecutor
import numpy as np

from modules.common.hepler import get_stock_type
from modules.dataHandler.data import Cal
from service.dayTrading.dayTradingService import DayTradingService

if __name__ == '__main__':


    # cache_path = "/Users/vega/workspace/codes/py_space/working/stockApi/test2.py"
    # cache_path = Path(cache_path)
    # meta_path = cache_path.with_suffix(".meta")
    # print(meta_path)
    # with meta_path.open("rb") as f:
    #     d = pickle.load(f)
    # provider_uri = "/Users/vega/workspace/codes/py_space/working/stockApi/stockApp/crontab/_datas2"
    #
    # hdf5_path = Path(provider_uri, 'calendars', "day.h5")
    # df1 = pd.read_hdf(hdf5_path, key='calendar')

    import tables
    hdf5_path = '/Users/vega/workspace/codes/py_space/working/stockApi/stockApp/crontab/_datas/store.h5'
    store = pd.HDFStore(hdf5_path, mode='r')
    hdf5_file = tables.open_file(hdf5_path, mode='r')
    group_path = '/features'
    group = hdf5_file.get_node(group_path)
    for node in group:
        print(node.name)
    hdf5_file.close()
    try:
        key = '/features/sh6000823'
        # print(store.keys())
        df = store[key]
        print(df)
    except Exception as e:
        print(e)
    # print(df)
    # print(df.index.names)
    # print(df[df.index.get_level_values('id')==8119]['close'])
    # print(df.index.get_level_values('id')[-1])

    store.close()
    xxxx



    import pandas as pd
    from stockApp import app

    date_range = pd.date_range(start='2024-06-01', periods=5)
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [10, 20, 30, 40, 50],
        'date': date_range
    })

    date_range = pd.date_range(start='2024-05-20', periods=20)
    df2 = pd.DataFrame({
        'date': date_range
    })
    # df2.index = pd.RangeIndex(start=0, stop=df2.shape[0], step=1, name='id')
    df2['id'] = range(len(df2))
    cal_df = df2[
        (df2['date'] >= df['date'].min())
        & (df2['date'] <= df['date'].max())
    ]

    cal_df.set_index('date', inplace = True)
    # print(cal_df)
    # 使用RangeIndex创建一个新的序列索引
    # 假设我们想要索引从1开始，长度为5
    # new_index = pd.RangeIndex(start=0, stop=df.shape[0], step=1, name='id')
    # df['id'] = new_index
    df.set_index('date', inplace = True)

    df['id'] = cal_df.loc[cal_df.index.values, 'id']

    r_df = df.reindex(cal_df.index)
    print(r_df)

    # print(df, df.loc[pd.IndexSlice[:,'2024-06-01':'2024-06-02'], :])
    ddd
    from concurrent.futures import ThreadPoolExecutor, as_completed

    # with Path('/Users/vega/workspace/codes/py_space/案例/股票/qlib/.qlib/qlib_data/cn_data/features/sh600083/close.day.bin').open("rb") as fp:
    #     _old_data = np.fromfile(fp, dtype="<f")
    #     _old_index = _old_data[0]
    #
    #     # print(_old_data, _old_index, _old_data[len(_old_data)-1])
    #     # xxxx
    #     # '20200101', '20200201'
    #     print(_old_data[0:11])
    with app.app_context():
        res = DayTradingService.get_feature_datas('600083', '19991110', '19991125')
        _close = Normalize1d.get_first_close(res)
        print(res)
        for _col in res.columns:
            # NOTE: retain original adjclose, required for incremental updates
            if _col in ['code', 'date', "adjclose", "change"]:
                continue
            if _col == "volume":
                res[_col] = res[_col] * _close
            else:
                res[_col] = res[_col] / _close
        # res.reset_index()
        # _mask = pd.to_datetime(df[self._date_field_name]) <= pd.Timestamp(self._end_date)
        # df = df[_mask]
        print(res)
    aaa



    store_path = '/Users/vega/workspace/codes/py_space/working/stockApi/stockApp/crontab/_datas/store.h5'
    store = pd.HDFStore(store_path, 'r')
    # print(store.get_node('data'), '-x----')
    # df = pd.DataFrame([[1, 2], [3, 4]], columns=['A', 'B'])
    # store.put("foo/bar/bah", df)
    # store.put('/data/t2', df)
    # print(store.groups())
    # for group in store.walk():
    #     print(group)

    df = store['/features/sz301567']
    # df = store['/calendars/day']
    print(df.first_valid_index())
    # print(df, df.index)


    # def read_data_store(store_path, key):
    #     with pd.HDFStore(store_path, 'r') as store:
    #         data = store[key]
    #         return data
    #
    # executor = ThreadPoolExecutor(max_workers=3)
    # # keys = ['foo/bar/bah', 'data/t2', 'data/t2', 'data/t2']
    # keys = ['calendars/day', 'features/sz300516', 'features/sz301509', 'instruments/all']
    # with pd.HDFStore(store_path, 'r') as store:
    #     all_keys = store.keys()
    #     filtered_keys = [key for key in all_keys if 'calendars' in key]
    #     print(filtered_keys, filtered_keys[0].split('/'))
    #
    #     print([sublist[2] for key in filtered_keys for sublist in [key.split('/')]])

    # with ThreadPoolExecutor(max_workers=10) as executor:
    #     future_to_key = {executor.submit(read_data_store, store_path, key): key for key in keys}
    #     for future in as_completed(future_to_key):
    #         key = future_to_key[future]
    #         try:
    #             data = future.result()
    #             print(f"Data from {key}:")
    #             print(data.head())  # 打印数据的前几行
    #         except Exception as exc:
    #             print(f"{key} generated an exception: {exc}")

    store.close()
