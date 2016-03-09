#!usr/bin/env python
# coding=utf-8
# Author: zhezhiyong@163.com
# Created: 2016年02月03日 03:09:34
# 编辑器：pycharm3.4，python版本：2.7.10
"""
# TODO(purpose): 
"""

import socket
import uuid
import struct
from common import utils
import gevent
from dao import datatype
from pb import base_pb2, ot_pb2, stock_trade_pb2, error_pb2

TRADER_ID = 'haha'
TRADER_IP = '0.0.0.0'
LOGIC_TYPE = 'LogicTypeManual'
CODE = '502048'
CODE_A = '502049'
CODE_B = '502050'


def client(TID):
    cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cli.connect(('192.168.15.34', 9810))
    # cli.connect(('192.168.15.34', 9991))
    # TID = '10001'

    sess = datatype.Sesstion(TID, cli)

    fmt = ">iHH16s"

    seq16 = uuid.uuid1()
    login = base_pb2.LoginReq()
    login.type = base_pb2.MANUAL_TRADE
    login.trader_id = TRADER_ID
    print 'login.version: [%s]' % login.version
    login.version = base_pb2.MAJOR << 16 or base_pb2.MINOR
    headbuffer = struct.pack(fmt, login.ByteSize(), base_pb2.SYS_ROBOT,
                             base_pb2.CMD_LOGIN_REQ, seq16.get_bytes())
    # seq += 1
    sentdata = headbuffer + login.SerializeToString()
    cli.send(sentdata)
    MAX_PACK = 1024 * 1024

    while True:
        status, packlen, sysid, cmd, rid = utils.recv_header(
                cli, base_pb2.HEADER_SIZE)

        if error_pb2.SUCCESS != status:
            break
        if packlen < 0 or packlen > MAX_PACK:
            print 'close connect error length', packlen
            break

        # 获取包体 收全包体
        body = ''
        status, body = utils.recv_body(cli, packlen)
        # print 'status: [%s], body: [%s] ' % (status, body)

        if error_pb2.SUCCESS != status:
            break

        print('cmd 0x[%x] sysid [%x]' % (cmd, sysid))
        # if base_pb2.SYS_ROBOT == sysid:
        mt_handle(sess, cmd, rid, body)
        # risk_handle(self, cmd, seq, body)

    print 'disconnect close socket'

    cli.shutdown(socket.SHUT_RDWR)
    #   esvr.shutdown(socket.SHUT_WR)
    gevent.sleep(0)
    cli.close()
    return 0


def mt_handle(sess, cmd, rid, body):
    print ('mt_handle cmd %x' % (cmd))
    if base_pb2.CMD_LOGIN_RESP == cmd:
        login_resp = base_pb2.LoginResp()
        login_resp.ParseFromString(body)
        pi = utils.package_info(cmd, rid, login_resp)
        login_resp_handle(sess, pi)
    if base_pb2.CMD_POLICY_STATUS == cmd:
        policy_status = ot_pb2.PolicyStatus()
        policy_status.ParseFromString(body)
        print 'client receive robot policy_id: [%s] policy_status: [%s]' % (
            policy_status.policy_id, policy_status.status)
    if base_pb2.CMD_SINGLE_WITHDRAWAL_RESP == cmd:
        pass
    if base_pb2.CMD_ERROR_REQ == cmd:
        stock_err = stock_trade_pb2.ErrResp()
        stock_err.ParseFromString(body)
        print stock_err


def login_resp_handle(sess, pi):
    print pi.cmd, pi.rid, pi.pack
    print '-' * 40
    # 单笔买
    # send_single_order(sess, code='502048', price_level=base_pb2.S_1, qty=1000000)
    send_single_order(sess, code='502049', qty=1000000)
    # send_single_order(sess, code='502050', qty=1000000)
    # 单笔卖
    # send_single_order(sess=sess, code='510050', direction=base_pb2.POLICY_DIRECTION_NEGATIVE)
    # 失败
    # send_single_order(sess=sess, code='510030', direction=base_pb2.POLICY_DIRECTION_NEGATIVE)
    # # 单笔申购
    # send_single_order(sess=sess, qty=60000, cmd=base_pb2.CMD_STOCK_CREATE_OR_REDEEM_POLICY)
    # # 单笔赎回
    # send_single_order(sess=sess, qty=60000, direction=base_pb2.POLICY_DIRECTION_NEGATIVE,
    #                   cmd=base_pb2.CMD_STOCK_CREATE_OR_REDEEM_POLICY)
    # # 拆分
    # send_single_order(sess=sess, qty=50000, cmd=base_pb2.CMD_STRUCTURED_FUND_SPLIT_OR_MERGE_POLICY)
    # # 合并
    # send_single_order(sess=sess, qty=50000, direction=base_pb2.POLICY_DIRECTION_NEGATIVE,
    #                   cmd=base_pb2.CMD_STRUCTURED_FUND_SPLIT_OR_MERGE_POLICY)

    # cancel(sess, 'sn000002')
    # # 申购
    # send_stock_create_or_redeem_policy(sess, base_pb2.CMD_STOCK_CREATE_OR_REDEEM_POLICY,
    #                                    base_pb2.POLICY_DIRECTION_POSITIVE, '502048', 1000000)
    # # 赎回
    # send_stock_create_or_redeem_policy(sess, base_pb2.CMD_STOCK_CREATE_OR_REDEEM_POLICY,
    #                                    base_pb2.POLICY_DIRECTION_NEGATIVE, '502048', 1000000)

    # # 拆分
    # send_structured_fund_split_or_merge_policy(sess, base_pb2.CMD_STRUCTURED_FUND_SPLIT_OR_MERGE_POLICY,
    #                                            base_pb2.POLICY_DIRECTION_NEGATIVE, CODE, 1000000)
    # # 合并
    # send_structured_fund_split_or_merge_policy(sess, base_pb2.CMD_STRUCTURED_FUND_SPLIT_OR_MERGE_POLICY,
    #                                            base_pb2.POLICY_DIRECTION_POSITIVE, CODE, 1000000)


    # 分级基金ab联动买卖
    # a联动b 买
    # send_structured_fund_link_policy(sess, base_pb2.CMD_STRUCTURED_FUND_LINK_POLICY, base_pb2.POLICY_DIRECTION_POSITIVE,
    #                                  CODE_A, CODE_B, 1000, 1000,
    #                                  9970, base_pb2.S_5, 0)
    #
    # # b联动a 买
    # send_structured_fund_link_policy(sess, base_pb2.CMD_STRUCTURED_FUND_LINK_POLICY, base_pb2.POLICY_DIRECTION_POSITIVE,
    #                                  CODE_A, CODE_B, 1000, 1000,
    #                                  11140, base_pb2.S_5, 1)
    # # a联动b 卖
    # send_structured_fund_link_policy(sess, base_pb2.CMD_STRUCTURED_FUND_LINK_POLICY, base_pb2.POLICY_DIRECTION_NEGATIVE,
    #                                  CODE_A, CODE_B, 1000, 1000,
    #                                  9970, base_pb2.B_5, 0)
    # # b联动a 卖
    # send_structured_fund_link_policy(sess, base_pb2.CMD_STRUCTURED_FUND_LINK_POLICY, base_pb2.POLICY_DIRECTION_NEGATIVE,
    #                                  CODE_A, CODE_B, 1000, 1000,
    #                                  9970, base_pb2.B_5, 1)

    # a+b买
    # send_structured_fund_ab_policy(sess, base_pb2.CMD_STRUCTURED_FUND_AB_POLICY, base_pb2.POLICY_DIRECTION_POSITIVE,
    #                                CODE, 10000, 2000)
    # a+b卖
    # send_structured_fund_ab_policy(sess, base_pb2.CMD_STRUCTURED_FUND_AB_POLICY, base_pb2.POLICY_DIRECTION_NEGATIVE,
    #                                CODE, 10000, 2000)


def send_structured_fund_split_or_merge_policy(sess, cmd, direction, code, volume):
    policy = ot_pb2.StructuredFundSplitOrMergePolicy()
    policy.base_param.direction = direction
    policy.base_param.trader_id = TRADER_ID
    policy.base_param.trader_ip = TRADER_IP
    policy.base_param.logic_type = LOGIC_TYPE
    policy.code = code
    policy.volume = volume
    rid = uuid.uuid1()
    snddata = utils.make_package(base_pb2.SYS_ROBOT, cmd, rid, policy)
    sess.sock.send(snddata)


# 分级基金A+B买卖
def send_structured_fund_ab_policy(sess, cmd, direction, code, volume, price_ratio):
    policy = ot_pb2.StructuredFundABPolicy()
    policy.base_param.direction = direction
    policy.base_param.trader_id = TRADER_ID
    policy.base_param.trader_ip = TRADER_IP
    policy.base_param.logic_type = LOGIC_TYPE
    policy.code = code
    policy.volume = volume
    policy.price_ratio = price_ratio
    rid = uuid.uuid1()
    snddata = utils.make_package(base_pb2.SYS_ROBOT, cmd, rid, policy)
    sess.sock.send(snddata)


# 分级基金AB联动买卖
def send_structured_fund_link_policy(sess, cmd, direction, code_a, code_b, volume_a, volume_b, price,
                                     price_level, link_direction):
    policy = ot_pb2.StructuredFundLinkPolicy()
    policy.base_param.direction = direction
    policy.base_param.trader_id = TRADER_ID
    policy.base_param.trader_ip = TRADER_IP
    policy.base_param.logic_type = LOGIC_TYPE
    policy.code_a = code_a
    policy.code_b = code_b
    policy.volume_a = volume_a
    policy.volume_b = volume_b
    policy.price = price
    policy.price_level = price_level
    policy.link_direction = link_direction
    rid = uuid.uuid1()
    snddata = utils.make_package(base_pb2.SYS_ROBOT, cmd, rid, policy)
    sess.sock.send(snddata)


# 申购赎回
def send_stock_create_or_redeem_policy(sess, cmd, direction, code, volume):
    policy = ot_pb2.StockCreateOrRedeemPolicy()
    policy.base_param.direction = direction
    policy.base_param.trader_id = TRADER_ID
    policy.base_param.trader_ip = TRADER_IP
    policy.base_param.logic_type = LOGIC_TYPE
    policy.code = code
    policy.volume = volume
    rid = uuid.uuid1()
    snddata = utils.make_package(base_pb2.SYS_ROBOT, cmd, rid, policy)
    sess.sock.send(snddata)
    pass


def send_single_order(sess, code='502048', direction=base_pb2.POLICY_DIRECTION_POSITIVE, qty=200,
                      price_level=base_pb2.S_1,
                      price=10000, cmd=base_pb2.CMD_STOCK_POLICY):
    sng_order = ot_pb2.StockPolicy()
    sng_order.base_param.direction = direction
    sng_order.base_param.trader_id = TRADER_ID
    sng_order.base_param.trader_ip = TRADER_IP
    sng_order.base_param.logic_type = LOGIC_TYPE
    sng_order.code = code
    sng_order.volume = qty
    sng_order.price_level = price_level
    # sng_order.price = 11170
    # 0表示不启用
    sng_order.reorder_interval = 0
    # print sng_order.__getattribute__(sng_order.WhichOneof('price_type'))
    print sng_order
    rid = uuid.uuid1()
    snddata = utils.make_package(base_pb2.SYS_ROBOT, cmd, rid, sng_order)
    sess.sock.send(snddata)


from common import pack_stock_pb


# 237868
def cancel(sess, order_no):
    s_cancel = pack_stock_pb.pack_single_cancel(order_no, 0, '1', 'PH1', '127.0.0.1')
    rid = uuid.uuid1()
    snddata = utils.make_package(base_pb2.SYS_STOCK, base_pb2.CMD_SINGLE_WITHDRAWAL_REQ, rid, s_cancel)
    sess.sock.send(snddata)


if __name__ == '__main__':
    client('PH1')
    # send_single_order(None)
    pass
