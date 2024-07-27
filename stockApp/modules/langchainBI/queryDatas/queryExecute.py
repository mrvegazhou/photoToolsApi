

from core.log.logger import get_module_logger

logger = get_module_logger("langchainBI-queryDatas-queryExecute")


def query_execute(out_dict):
    print(out_dict, "====out_dict====")
    result_data = []
    if out_dict:
        out_dict_result, datasource_info, datasource_type = verify_query(out_dict)
        if out_dict_result:
            out_dict["table_name"] = out_dict_result
            sql_query = sql_assemble(out_dict)
            list_data = selectMysql(sql_query)
            for row in list_data:
                result = {
                    "name": row[0],
                    "value": int(row[1])
                }
                result_data.append(result)

    return result_data


def verify_query(out_dict: dict):
    if out_dict is None:
        return None
    indicators_code = out_dict["data_indicators"]