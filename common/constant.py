#!usr/bin/env python
# coding=utf-8
# Author: zhezhiyong@163.com
# Created: 2016年02月19日 19:15:21
# 编辑器：pycharm5.0.2，python版本：2.7.10
"""
# TODO(purpose): 
"""

# //0x20--0x25, //基金
kInstrumentTypeFunds = 0x20  # 基金
kInstrumentTypeNLOF = 0x21  # 未上市开放基金,Not listed Open-Ended Fund
kInstrumentTypeLOF = 0x22  # 上市开放基金,Listed Open-Ended Fund
kInstrumentTypeETF = 0x23  # 交易型开放式指数基金, Exchange Traded Fund
kInstrumentTypeExtendedFunds = 0x25  # 扩展板块基金(港)

Buy = 1
Sell = 2
Create = 3
Redeem = 4

SZ = 0
SH = 1


class OrderStatus:
    """
    -11- -19 Resp err
    -1 -9 Send req err
    0 - Create
    1-9 Send Req
    11-19 Send Req Resp
    21-29 None
    31- Finish
    41-49 Canceling`Cancel
    """
    CREATE = 0
    # 发送请求
    SEND_ORDER_REQ = 3
    # 确认请求
    ORDER_REQ_REP_RIGHT = 11
    # 错误
    ORDER_REQ_REP_ERR = -11
    CANCELING = 31

    CANCEL_SUBMITTED = 32
    CANCELED = 41

    FINISH = 51
    FAILED = -21

    def __init__(self):
        pass
