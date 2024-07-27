from .dict import *

"""
  大模型输出结构化处理
 input:
 {
        "dimension": "东方财富",
        "indicators": "PE",
        "operator": "对比",
        "time_type": "day",
        "date_range": "2023-07-01,2023-12-31",
        "compares": "招商银行"
 }
 output:
 {  "dimensions": "东方财富",
    "indicators": "PE",
    "operator": "compare",
    "time_type": "day",
    "date_range": "2023-02-01,2023-02-25",
    "compares": "招商银行"
 }

"""
obj_dict = Dict()


def out_json_data(info):
    out_json = {}
    if "data_indicators" in info:
        out_json["data_indicators"] = obj_dict.__value__(FILE_DICT_TYPE, str(info["data_indicators"]))
    if "operator_type" in info:
        out_json["operator_type"] = obj_dict.__value__(FILE_OPERATOR_TYPE, str(info["operator_type"]))
    if "time_type" in info:
        out_json["time_type"] = obj_dict.__value__(FILE_DICT_TYPE, str(info["time_type"]))
    if "dimension" in info:
        out_json["dimensions"] = [{"enName": "name"}]
    if "filter" in info:
        out_json["filters"] = [{"enName": "name", "val": info["filter"]}]
    if "filter_type" in info:
        out_json["filter_type"] = obj_dict.__value__(FILE_DICT_TYPE, str(info["filter_type"]))
    if "date_range" in info:
        out_json["date_range"] = info["date_range"]
    if "compare_type" in info:
        out_json["compare_type"] = info["compare_type"]
    return out_json