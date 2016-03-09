#!/usr/bin/env python
# -*- coding: utf-8 -*-


""" global data
"""

import gevent
# from gevent import socket
import socket

import struct
import sys
import yaml

import uuid
import base_pb2
import stock_trade_pb2
import ot_pb2

from common import utils
import datatype
from common.utils import package_info


__author__ = 'qinjing'


seq = 0

TID = 'PH1'
count = 0

ETFCODE = '159909'


# -----------------------------------------------------------------------------
def login_resp_handle(sess, pi):
    print pi.cmd, pi.s1, pi.s2, pi.s3, pi.s4, pi.pack
    print '-' * 40
    # send_single_order(sess, base_pb2.OPR_BUY)
    trans_basket(sess, pi)


# -----------------------------------------------------------------------------
def mt_handle(sess, cmd, s1, s2, s3, s4, body):
    print ('mt_handle cmd %x' % (cmd))
    if base_pb2.CMD_LOGIN_RESP == cmd:
        login_resp = base_pb2.LoginResp()
        login_resp.ParseFromString(body)
        pi = package_info(cmd, s1, s2, s3, s4, login_resp, sess)
        login_resp_handle(sess, pi)

    elif base_pb2.CMD_SINGLE_ORDER_RESP == cmd:
        sngl_order_resp = stock_trade_pb2.SingleOrderResp()
        sngl_order_resp.ParseFromString(body)
        pi = package_info(cmd, s1, s2, s3, s4, sngl_order_resp, sess)
        single_order_resp_handle(sess, pi)
    elif base_pb2.CMD_SINGLE_WITHDRAWAL_RESP == cmd:
        sngl_order_resp = stock_trade_pb2.SingleOrderResp()
        sngl_order_resp.ParseFromString(body)
        pi = package_info(cmd, s1, s2, s3, s4, sngl_order_resp, sess)
        single_withdrawal_resp_handle(sess, pi)

    elif base_pb2.CMD_BASKET_ORDER_RESP == cmd:
        bp_resp = ot_pb2.BasketPolicyResp()
        bp_resp.ParseFromString(body)
        pi = package_info(cmd, s1, s2, s3, s4, bp_resp, sess)
        stock_basket_resp_handle(sess, pi)
    # elif base_pb2.lymtc_money == cmd:
    #     pass


# # -----------------------------------------------------------------------------
# def send_single_order(sess, opr, qty=1000000):
#     sng_order = stock_trade_pb2.SingleOrderReq()
#     sng_order.code = '000001'
#     global TID
#     if len(sys.argv) > 1:
#         code = sys.argv[1]
#         sng_order.code = code
#         print 'stock code %s' % (code)
#         TID = code
#     if base_pb2.OPR_BUY == opr:
#         sng_order.price = 109000
#     else:
#         sng_order.price = 100000
#     sng_order.qty = qty
#     sng_order.bs_flag = opr
#     sng_order.trader_id = TID
#     print 'TID %s' % TID
#     sng_order.market = base_pb2.MKT_SZ
#
# #    global seq seq += 1
#     seq16 = uuid.uuid4()
#     s1, s2, s3, s4 = struct.unpack('>iiii', seq16.get_bytes())
#     pi = package_info(0, s1, s2, s3, s4, 0, sess)
#     snddata = utils.make_package(
#         base_pb2.SYS_MTC, base_pb2.CMD_SINGLE_ORDER_REQ, pi,
#         sng_order)
#     sess.send(snddata)
#
#
# def send_single_order_risk(sess):
#     sng_order = stock_trade_pb2.SingleOrderReq()
#     sng_order.code = ETFCODE        #
#     sng_order.price = 123000
#     sng_order.qty = 1200
#     sng_order.bs_flag = base_pb2.OPR_BUY
#     sng_order.policy_id = '123456789'
#     sng_order.trader_id = TID
#     sng_order.instrument_type = 0x25
#     sng_order.market = base_pb2.MKT_SH
#
#     seq16 = uuid.uuid4()
#     snddata = utils.make_package(
#         base_pb2.SYS_MTC, base_pb2.CMD_SINGLE_ORDER_REQ, seq16.get_bytes(),
#         sng_order)
#     sock.send(snddata)


# # --------------------------------------------------------------------------
# def single_order_resp_handle(sess, pi):
#     print ('single_order_resp_handle: %s' % (pi))
#     print('wait for withdrawal single order')
#     gevent.sleep(5)
#
#     sw = stock_trade_pb2.SingleCancelReq()
#
# #    required string     order_no    = 1;        //订单编号
# #    optional int32      market      = 2;        //市场 0:深圳 1：上海
# #    optional bytes        policy_id    = 3;        //策略ID
# #    optional string        trader_id    = 4;        //交易员ID
# #    optional string        trader_ip    = 5;        //交易员IP
#     sw.order_no = pi.pack.order_no
#     sw.market = base_pb2.MKT_SZ
#     print('sw.policy_id %s\npack.policy_id %s' % (type(sw.policy_id), type(pi.pack.policy_id)))
#     sw.policy_id = pi.pack.policy_id
#     sw.trader_id = TID
#
#     seq16 = uuid.uuid4()
#     s1, s2, s3, s4 = struct.unpack('>iiii', seq16.get_bytes())
#     pi = package_info(0, s1, s2, s3, s4, 0, sess)
#     snddata = utils.make_package(
#         base_pb2.SYS_MTC, base_pb2.CMD_SINGLE_WITHDRAWAL_REQ, pi,
#         sw)
#     sock.send(snddata)
#     pass


# # ---------------------------------------------------------------------------
# def single_withdrawal_resp_handle(sess, pi):
#     print('S withdrawal %s' % (pi))
#     # bpr = ot_pb2.BasketPolicyReq()
#     # bpr.basket_type = base_pb2.OPR_BASEKET_BUY
#     # bpr.pricelevel = 3
#     # bpr.volume = 10
#     # bpr.etfcode = ETFCODE
#     # make_package_and_send(sess, base_pb2.CMD_BASKET_ORDER_REQ, bpr)
#     return
#     basket = ot_pb2.BasketPolicyReq()
#     basket.stkinfo.code = ETFCODE
#     basket.stkinfo.price = 12.34
#     basket.stkinfo.qty = 1000
#     basket.stkinfo.bs_flag = base_pb2.OPR_BUY
#     basket.stkinfo.trader_id = TID
#     basket.market = base_pb2.MKT_SZ
#     make_package_and_send(sess, base_pb2.CMD_BASKET_ORDER_REQ, basket)


# # --------------------------------------------------------------------------
# def single_order_resp_handle(sess, pi):
#     print ('single_order_resp_handle: %s' % (pi))
#     print('wait for withdrawal single order')
#     gevent.sleep(5)
#
#     sw = stock_trade_pb2.SingleCancelReq()
#
# #    required string     order_no    = 1;        //订单编号
# #    optional int32      market      = 2;        //市场 0:深圳 1：上海
# #    optional bytes        policy_id    = 3;        //策略ID
# #    optional string        trader_id    = 4;        //交易员ID
# #    optional string        trader_ip    = 5;        //交易员IP
#     sw.order_no = pi.pack.order_no
#     sw.market = base_pb2.MKT_SZ
#     print('sw.policy_id %s\npack.policy_id %s' % (type(sw.policy_id), type(pi.pack.policy_id)))
#     sw.policy_id = pi.pack.policy_id
#     sw.trader_id = TID
#
#     seq16 = uuid.uuid4()
#     s1, s2, s3, s4 = struct.unpack('>iiii', seq16.get_bytes())
#     pi = package_info(0, s1, s2, s3, s4, 0, sess)
#     snddata = utils.make_package(
#         base_pb2.SYS_MTC, base_pb2.CMD_SINGLE_WITHDRAWAL_REQ, pi,
#         sw)
#     sock.send(snddata)
#     pass


# ---------------------------------------------------------------------------
def make_package_and_send(sess, cmd, pack):
    seq16 = uuid.uuid4()
    s1, s2, s3, s4 = struct.unpack('>iiii', seq16.get_bytes())
    pi = package_info(0, s1, s2, s3, s4, 0, sess)
    snddata = utils.make_package(
        base_pb2.SYS_MTC, cmd, pi, pack)
    sess.sock.send(snddata)


# ----------------------------------------------------------------------------
def trans_basket(sess, pi):
    basket = ot_pb2.BasketPolicyReq()
    basket.code = ETFCODE
    basket.pl = base_pb2.B_5
    basket.qty = 1
    basket.opr = base_pb2.OPR_BUY
    # basket.market = base_pb2.MKT_SZ
    make_package_and_send(sess, base_pb2.CMD_BASKET_ORDER_REQ, basket)


# ----------------------------------------------------------------------------
def stock_basket_resp_handle(sess, pi):
    print'bbbbbbbb' * 5
    print pi

    pack = pi.pack
    if pack.rate == pack.ksh_count:
        gevent.sleep(5)
        bw = ot_pb2.BasketWithdrawalReq()
        bw.policy_id = pack.policy_id
        make_package_and_send(sess, base_pb2.CMD_BASKET_WITHDRAWAL_REQ, bw)

        print('wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww')

    return

    print pi
    if 100 == pi.pack.rate:
        basket = ot_pb2.single_order_req()
        basket.stkinfo.code = ETFCODE
        basket.stkinfo.price = 12.34
        basket.stkinfo.qty = 1000
        basket.stkinfo.bs_flag = base_pb2.OPR_BUY_PURCHASE
        basket.stkinfo.trader_id = TID
        basket.market = base_pb2.MKT_SZ
        make_package_and_send(sess, base_pb2.CMD_FUND_ORDER_REQ, basket)

        basket = ot_pb2.single_order_req()
        basket.stkinfo.code = ETFCODE
        basket.stkinfo.price = 12.34
        basket.stkinfo.qty = 1000
        basket.stkinfo.bs_flag = base_pb2.OPR_FAST_PURCHASE
        basket.stkinfo.trader_id = TID
        basket.market = base_pb2.MKT_SZ
        make_package_and_send(sess, base_pb2.CMD_FUND_ORDER_REQ, basket)

        basket = ot_pb2.single_order_req()
        basket.stkinfo.code = ETFCODE
        basket.stkinfo.price = 12.34
        basket.stkinfo.qty = 1000
        basket.stkinfo.bs_flag = base_pb2.OPR_REDEEM_SELL
        basket.stkinfo.trader_id = TID
        basket.market = base_pb2.MKT_SZ
        make_package_and_send(sess, base_pb2.CMD_FUND_ORDER_REQ, basket)

        basket = ot_pb2.single_order_req()
        basket.stkinfo.code = ETFCODE
        basket.stkinfo.price = 12.34
        basket.stkinfo.qty = 1000
        basket.stkinfo.bs_flag = base_pb2.OPR_FAST_REDEEM
        basket.stkinfo.trader_id = TID
        basket.market = base_pb2.MKT_SZ
        make_package_and_send(sess, base_pb2.CMD_FUND_ORDER_REQ, basket)

    pass


# ------------------------------------------------------------------------------------
def main():
    with open('robot.yaml') as f:
        cfg = yaml.load(f)
    esvr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if len(sys.argv) > 1:
        code = sys.argv[1]
        print 'stock code %s' % (code)
        global TID
        TID = code

    sess = datatype.Sesstion(TID, esvr)
    rip = cfg['robot_listen']['rip']
    rport = cfg['robot_listen']['rport']
    print rip, rport
    esvr.connect((rip, rport))
    # esvr.connect(("127.0.0.1", 8111))
    fmt = ">iHHiiii"
    fmt = ">iHH16s"
    # size = struct.calcsize(fmt)
    seq16 = uuid.uuid4()
    login = base_pb2.LoginReq()
    login.type = base_pb2.MANUAL_TRADE
    login.trader_id = TID
    print(login.version)
    login.version = base_pb2.MAJOR << 16 or base_pb2.MINOR
#     headbuffer = struct.pack(fmt, login.ByteSize(), base_pb2.SYS_MTC,
#                              base_pb2.CMD_LOGIN_REQ, 0, 0, 0, seq)
    headbuffer = struct.pack(fmt, login.ByteSize(), base_pb2.SYS_MTC,
                             base_pb2.CMD_LOGIN_REQ, seq16.get_bytes())
    # seq += 1
    sentdata = headbuffer + login.SerializeToString()
    esvr.send(sentdata)
    # dd = '\x1a\xff\xcc' # print('send %d %r' % (len(dd), dd))
    # esvr.send('\x1a') # esvr.send(dd)
    MAX_PACK = 1024 * 1024

    while True:
        status, packlen, sysid, cmd, s1, s2, s3, s4 = utils.recv_header(
            esvr, base_pb2.HEADER_SIZE)

        if base_pb2.SUCCESS != status:
            break
        if packlen < 0 or packlen > MAX_PACK:
            print 'close connect error length', packlen
            break

        # 获取包体 收全包体
        body = ''
        status, body = utils.recv_body(esvr, packlen)
        if base_pb2.SUCCESS != status:
            break

        print('cmd 0x%x sysid %x' % (cmd, sysid))
        # if base_pb2.SYS_ROBOT == sysid:
        mt_handle(sess, cmd, s1, s2, s3, s4, body)
#            risk_handle(self, cmd, seq, body)

    print 'disconnect close socket'

    esvr.shutdown(socket.SHUT_RDWR)
    #   esvr.shutdown(socket.SHUT_WR)
    gevent.sleep(0)
    esvr.close()
    return 0


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    ret = main()
    sys.exit(ret)
    print ('main')

