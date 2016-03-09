#!/usr/bin/env python
# -*- coding: utf-8 -*-


""" global data
"""

import gevent
# from gevent import socket
from gevent.server import StreamServer

# import struct
import sys
# import yaml


from common import utils

from pb import base_pb2
from pb import stock_trade_pb2
from dao.datatype import package_info, Sesstion

# import quota_pb2
# import pq_quota_pb2
# import stock_def

# from time import sleep


__author__ = 'qinjing'


# --------------------------------------------------------------------------
class BaseServer(object):
    def __init__(self, addr):
        self.svr = StreamServer(addr, self.new_session)

    def new_session(self, clnt_s, address):
        print('New connection from %s:%s' % address)
        MAX_PACK = 1024 * 1024
        # alive = True
        login_flag = 0
        while True:
            status, packlen, sysid, cmd, s1, s2, s3, s4 = utils.recv_header(
                clnt_s, base_pb2.HEADER_SIZE)
            if base_pb2.SUCCESS != status:
                break

            if packlen < 0 or packlen > MAX_PACK:
                print 'close connect error length', packlen
                break

            # 获取包体 收全包体
            body = ''
            status, body = utils.recv_body(clnt_s, packlen)
            if base_pb2.SUCCESS != status:
                print('\033[31mRecv Wrong %d %d\033[0m' % (packlen, len(body)))
                break

            snddata = ''
            # print('cmd 0x%x login %d' % (cmd, login_flag))
            if base_pb2.CMD_LOGIN_REQ == cmd:
                lgn = base_pb2.LoginReq()
                lgn.ParseFromString(body)
                pi = package_info(cmd, s1, s2, s3, s4, lgn)
                status, snddata = self.login_handle(clnt_s, pi)
                sess = Sesstion(lgn.trader_id, clnt_s)
                pi.sess = sess

                if base_pb2.SUCCESS == status:
                    login_flag = 1
            elif 1 == login_flag:
                status, snddata = self.package_handle(
                    clnt_s, sysid, cmd, s1, s2, s3, s4, body, packlen)
            else:
                print 'login first'

            num = clnt_s.send(snddata)
            # print ('snddata %d (%r)' % (num, snddata))

        print 'disconnect close socket'
        clnt_s.close()

#    def package_handle(self, clnt_s, sysid, cmd, seq, body):
#        snddata = ''
#        return snddata


# -----------------------------------------------------------------------------
class RiskSvr(BaseServer):
    sn = 0
    swn = 0
    bn = 0
    ssss = 0

    def __init__(self, addr):
        super(RiskSvr, self).__init__(addr)

    def package_handle(self, clnt_s, sysid, cmd, s1, s2, s3, s4, body, pcklen):
        snddata = ''
        if base_pb2.CMD_SINGLE_ORDER_REQ == cmd:
            sng_order = stock_trade_pb2.SingleOrderReq()
            sng_order.ParseFromString(body)
            pi = package_info(cmd, s1, s2, s3, s4, sng_order, clnt_s)
            status, snddata = self.single_order_req(clnt_s, pi)
        elif base_pb2.CMD_SINGLE_WITHDRAWAL_REQ == cmd:
            s_withdrawal = stock_trade_pb2.SingleCancelReq()
            s_withdrawal.ParseFromString(body)
            pi = package_info(cmd, s1, s2, s3, s4, s_withdrawal, clnt_s)
            status, snddata = self.single_withdrawal_req(clnt_s, pi)
        elif base_pb2.CMD_BATCH_ORDER_REQ == cmd:
            bo = stock_trade_pb2.StockBatchOrderReq()
            if self.ssss < 10:
                print('%d\n%r' % (self.ssss, body))
                self.ssss += 1
            try:
                bo.ParseFromString(body)
            except:
                print('\033[31mpacklen %d seq %d 0x%x' % (pcklen, s3, s4))
                print('body %d\n%r\033[0m' % (len(body), body))
            pi = package_info(cmd, s1, s2, s3, s4, bo, clnt_s)
            status, snddata = self.batch_order_req(clnt_s, pi)
        else:
            print('unknow cmd 0x%x %s' % (cmd, pi))

        return base_pb2.SUCCESS, snddata

    # --------------------------------------------------------------------------
    def login_handle(self, clnt_s, pi):
        pack = pi.pack
        print pi.cmd, pi.s1, pi.s2, pi.s3, pi.s4, pack
        login_resp = base_pb2.LoginResp()
        login_resp.result = 0
        snddata = utils.make_package(
            base_pb2.SYS_ROBOT, base_pb2.CMD_LOGIN_RESP, pi, login_resp)
        return base_pb2.SUCCESS, snddata
        # socket.send(snddata)

    # --------------------------------------------------------------------------
    def single_order_req(self, clnt_s, pi):
        # print('single_order_req seg %d %d' % (pi.s3, pi.s4))
        self.sn += 1
        sng_ord_resp = stock_trade_pb2.SingleOrderResp()
        sng_ord_resp.ret_code = base_pb2.SUCCESS
        sng_ord_resp.order_no = 'sn0000%02d' % self.sn
        snddata = utils.make_package(
            base_pb2.SYS_ROBOT, base_pb2.CMD_SINGLE_ORDER_RESP, pi,
            sng_ord_resp)
        return base_pb2.SUCCESS, snddata
        # socket.send(snddata)

    # --------------------------------------------------------------------------
    def single_withdrawal_req(self, clnt_s, pi):
        # print('wwwwwwwwwwwwwwwwww', pi)
        self.swn += 1
        s_withdrawal_resp = stock_trade_pb2.SingleOrderResp()
        s_withdrawal_resp.ret_code = base_pb2.SUCCESS
        s_withdrawal_resp.order_no = 'sw8000%02d' % self.swn
        snddata = utils.make_package(
            base_pb2.SYS_ROBOT, base_pb2.CMD_SINGLE_WITHDRAWAL_RESP, pi,
            s_withdrawal_resp)
        return base_pb2.SUCCESS, snddata

    # --------------------------------------------------------------------------
    def batch_order_req(self, clnt_s, pi):
        # print('%s bn %d cnt %d' % ('=' * 50, self.bn, len(pi.pack.order_list)))
        # print pi
        snddata = ''
        self.bn += 1

        bo_resp = stock_trade_pb2.StockBatchOrderResp()
        bo_resp.ret_code = base_pb2.SUCCESS
        bo_resp.groupid = pi.pack.groupid
        # bo_resp.ret_message
        bo_resp.batch_no = 'bon700000%02d' % self.bn
        for i in xrange(len(pi.pack.order_list)):
            single = bo_resp.order_resp_list.add()
            self.sn += 1
            if 1 == pi.s4 % 2:
                if 0 == i % 2:
                    single.ret_code = base_pb2.SUCCESS
                    single.order_no = 'sn0000%02d' % self.sn
                else:
                    single.ret_code = base_pb2.ERROR_WAIT
                    single.order_no = 'sn8000%02d' % self.sn
            else:
                single.ret_code = base_pb2.SUCCESS
                single.order_no = 'sn0000%02d' % self.sn

        snddata = utils.make_package(
            base_pb2.SYS_ROBOT, base_pb2.CMD_BATCH_ORDER_RESP, pi,
            bo_resp)
        return base_pb2.SUCCESS, snddata

    # --------------------------------------------------------------------------


# -----------------------------------------------------------------------------
def server_start(app):
    # socksvr.start()
    app.svr.serve_forever()
    print 'x2' * 30


# # --------------------------------------------------------------------------
def main():
    svr = RiskSvr(('0.0.0.0', 9991))
    jobs = []
    # jobs.append(gevent.spawn(quo_recv, app))
    jobs.append(gevent.spawn(server_start, svr))
    # jobs.append(gevent.spawn(riskmgt.riskmgt_interact, app))
    gevent.joinall(jobs)


if __name__ == '__main__':
    ret = main()
    sys.exit(ret)
    print ('main')
