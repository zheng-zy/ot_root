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


# ---------------------------------------------------------------------------
def make_package_and_send(sess, cmd, pack):
    seq16 = uuid.uuid4()
    s1, s2, s3, s4 = struct.unpack('>iiii', seq16.get_bytes())
    pi = package_info(0, s1, s2, s3, s4, 0, sess)
    snddata = utils.make_package(
        base_pb2.SYS_MTC, cmd, pi, pack)
    sess.sock.send(snddata)


# -----------------------------------------------------------------------------
def login_resp_handle(sess, pi):
    print pi.cmd, pi.s1, pi.s2, pi.s3, pi.s4, pi.pack
    print '-' * 40
    # send_single_order(sess, base_pb2.OPR_BUY)
    trans_basket_complete(sess, pi)


# ----------------------------------------------------------------------------
def trans_basket_complete(sess, pi):
    basket = ot_pb2.BasketPolicyReq()
    basket.code = ETFCODE
    basket.pl = base_pb2.B_5
    basket.qty = 1
    basket.opr = base_pb2.OPR_BASEKET_COMPLETE
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

