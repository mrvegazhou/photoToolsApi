# coding:utf8
import pandas as pd
import re
import json


def get_stock_type(stock_code) -> str:
    assert type(stock_code) is str, "stock code need str type"
    if stock_code.startswith(('600', '601', '603', '688')):
        return 'sh'
    elif stock_code.startswith(('000', '001', '002')):
        return 'sz'
    elif stock_code.startswith('30'):
        return 'sz'
    elif stock_code.startswith(('83', '87')):  # 注意：北交所代码可能有所变化，这里只是示例
        return 'bj'
    else:
        return ''


def trans_num(df, ignore_cols):
    '''df为需要转换数据类型的dataframe
    ignore_cols为dataframe中忽略要转换的列名的list
    如ignore_cols=['代码','名称','所处行业']
    '''
    trans_cols = list(set(df.columns) - set(ignore_cols))
    df[trans_cols] = df[trans_cols].apply(lambda s: pd.to_numeric(s, errors='coerce'))
    return df


def contains_chinese(s):
    pattern = re.compile(r'[\u4e00-\u9fff]+')  # 基本汉字范围
    return pattern.search(s) is not None


def grep_comma(num_str):
    return num_str.replace(",", "")


def str2num(num_str, convert_type="float"):
    num = float(grep_comma(num_str))
    return num if convert_type == "float" else int(num)


def file2dict(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)