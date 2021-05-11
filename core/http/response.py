# coding: utf-8
import json
import decimal
from datetime import date, time, datetime
from flask import Response

CODE = {
    # 正常操作
    10000: '操作成功',

    # 逻辑异常
    10001: '用户不存在',
    10002: '帐号或密码错误',
    10003:'该帐号已被封禁',
    10004:'该角色已被封禁',
    10005:'包含不可操作用户',
    10006:'该记录已存在',
    10007:'机构封禁',
    10008:'邮箱格式错误',
    10009:'电话格式错误',
    10010:'已启用虚拟设备中',
    10021: '用户密码重置失败',
    # http异常
    20001: 'token超时',
    20002: 'ssl证书异常',
    20003: 'JSON格式异常',
    20004: '服务端链接超时',
    20005:'COS服务异常',
    # 非法行为
    30001: '操作非法',
    30002: 'IP黑名单',
    30003: '访问过于频繁',
    30004: '创建帐号含非法角色',
    30005: '填入数据非法',
    30006: '机构类型非法',
    30007: '非法获取授权资源',
    # 系统异常
    40001: '系统异常',
    40002: 'mysql服务异常',
    40003: 'redis服务异常',
    40004: '模型文件丢失',
    40005: 'FFmpeg异常',
    40006: 'shell功能异常',
    # 接口服务
    50001: '接口鉴权失败',
    50002: '参数名错误',
    50003: '参数类型错误',
    50004: '文件格式异常',
    50005: '数据长度溢出',
    50006: '转码失败',
    50007: '文件上传失败',
    50008: '数据格式异常',

    -1:    '未知错误'
}

class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, time):
            return obj.strftime('%H:%M:%S')
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        else:
            return super().default(self, obj)

def json_return(data):
    return Response(json.dumps(data, cls=JsonEncoder, separators=(",", ":")), mimetype="application/json")

# 返回数据封装
def send(code, msg=None, data=None, **kwargs):
    if code not in CODE.keys():
        code = -1
    if msg is None:
        msg = CODE[code]
    if data is None:
        data = ""
    result = {"code": code, "msg": msg, "data": data}
    result.update(kwargs)
    return json_return(result)