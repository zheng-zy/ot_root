#!/usr/bin/env python
# -*- coding: utf-8 -*-


""" global data
"""

import gevent
# from gevent import socket

import struct
import sys
import yaml

import uuid
from net import baseclient
from quota import pre_quotation, quotation
import base_pb2
import stock_trade_pb2
import ot_pb2

from common import utils
from common.utils import package_info


__author__ = 'qinjing'


seq = 0

TID = 'PH1'
count = 0

ETFCODE = '159909'


class Tester(baseclient.BaseClient):
    def __init__(self, tid, addr):
        self.rid = tid
        super(Tester, self).__init__(self, addr)
        self.seq = 0
        self.pre_quo = None
        self.quo = None

    def after_connect(self, err):
        # self.sess = datatype.Sesstion(TID, self.svr_sock)
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
        self.svr_sock.sendall(sentdata)
        print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        # dd = '\x1a\xff\xcc' # print('send %d %r' % (len(dd), dd))
        # esvr.send('\x1a') # esvr.send(dd)

    # -----------------------------------------------------------------------------
    def login_resp_handle(self, pi):
        print pi.cmd, pi.s1, pi.s2, pi.s3, pi.s4, pi.pack
        print '-' * 40
        # send_single_order(base_pb2.OPR_BUY)
        self.trans_etf_purchase(pi)

    # --------------------------------------------------------------------
    def package_handle(self, packlen, pi, body):
        cmd = pi.cmd
        print ('mt_handle cmd %x' % (cmd))
        if base_pb2.CMD_LOGIN_RESP == cmd:
            login_resp = base_pb2.LoginResp()
            login_resp.ParseFromString(body)
            pi.pack = login_resp
            self.login_resp_handle(pi)

        elif base_pb2.CMD_SINGLE_ORDER_RESP == cmd:
            sngl_order_resp = stock_trade_pb2.SingleOrderResp()
            sngl_order_resp.ParseFromString(body)
            pi.pack = sngl_order
            self.single_order_resp_handle(pi)
        elif base_pb2.CMD_SINGLE_WITHDRAWAL_RESP == cmd:
            sngl_order_resp = stock_trade_pb2.SingleOrderResp()
            sngl_order_resp.ParseFromString(body)
            pi.pack = sngl_order_resp
            self.single_withdrawal_resp_handle(pi)

        elif base_pb2.CMD_BASKET_ORDER_RESP == cmd:
            bp_resp = ot_pb2.BasketPolicyResp()
            bp_resp.ParseFromString(body)
            pi.pack = bp_resp
            self.stock_basket_resp_handle(pi)

        elif base_pb2.CMD_POLICY_STATUS == cmd:
            pack = ot_pb2.PolicyStatus()
            pack.ParseFromString(body)
            pi.pack = pack
            self.trans_etf_purchse_resp(pi)

    # ------------------------------------------------------------------
    def make_package_and_send(self, cmd, pack):
        seq16 = uuid.uuid4()
        s1, s2, s3, s4 = struct.unpack('>iiii', seq16.get_bytes())
        pi = package_info(0, s1, s2, s3, s4, 0, self.sess)
        snddata = utils.make_package(
            base_pb2.SYS_MTC, cmd, pi, pack)
        self.sess.sock.send(snddata)

    # -------------------------------------------------------------------
    def trans_etf_purchase(self, pi):
        purchs = ot_pb2.ETFCreateOrRedeemPolicy()
        purchs.base_param.policy_direction = \
            base_pb2.POLICY_DIRECTION_NEGATIVE
        purchs.code = '510300'
        purchs.volume = 1000000

        make_package_and_send(base_pb2.CMD_ETF_CREATE_OR_REDEEM_POLICY, purchs)

    # -------------------------------------------------------------------
    def trans_etf_purchase_resp(self, pi):
        print('purchase', pi)

    # -------------------------------------------------------------------
    def stock_basket_resp_handle(self, pi):
        print'bbbbbbbb' * 5
        print pi

        pack = pi.pack
        if pack.rate == pack.ksh_count:
            gevent.sleep(5)
            bw = ot_pb2.BasketWithdrawalReq()
            bw.policy_id = pack.policy_id
            make_package_and_send(base_pb2.CMD_BASKET_WITHDRAWAL_REQ, bw)

            print('wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww')

        return


# ---------------------------------------------------------------------------
def main():

    if len(sys.argv) > 1:
        code = sys.argv[1]
        print 'stock code %s' % (code)
        global TID
        TID = code

    with open('robot.yaml') as f:
        cfg = yaml.load(f)
    rip = cfg['robot_listen']['rip']
    rport = cfg['robot_listen']['rport']
    addr = (rip, rport)
    print addr
    tester = Tester(TID, addr)

    pq_ip = cfg['pre_quo']['pqip']
    pq_port = cfg['pre_quo']['port']
    print pq_ip, pq_port
    pre_quo = pre_quotation.PreQuotation(tester, (pq_ip, pq_port))
    tester.pre_quo = pre_quo

    q_ip = cfg['quo_server']['qip']
    q_port = cfg['quo_server']['port']
    print q_ip, q_port
    quota = quotation.Quotation(tester, (q_ip, q_port))
    tester.quo = quota

    jobs = []
    jobs.append(gevent.spawn(pre_quo.recv_data))
    jobs.append(gevent.spawn(quota.recv_data))
    jobs.append(gevent.spawn(tester.recv_data))
    gevent.joinall(jobs)

    return 0


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    ret = main()
    sys.exit(ret)
    print ('main')

