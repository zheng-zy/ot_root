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
from pb import stock_trade_pb2, base_pb2, trade_db_model_pb2, error_pb2

from common.utils import package_info
from common import utils
from dao.datatype import Sesstion
import uuid

# import quota_pb2
# import pq_quota_pb2
# import stock_def

# from time import sleep
from common import timeUtils

__author__ = 'qinjing'


# --------------------------------------------------------------------------
class BaseServer(object):
    def __init__(self, addr):
        self.svr = StreamServer(addr, self.new_session)

    def new_session(self, clnt_s, address):
        print('New connection from %s:%s' % address)
        MAX_PACK = 1024 * 1024
        # alive = True
        login_flag = 1
        while True:
            status, packlen, sysid, cmd, rid = utils.recv_header(
                    clnt_s, base_pb2.HEADER_SIZE)
            if error_pb2.SUCCESS != status:
                break

            if packlen < 0 or packlen > MAX_PACK:
                print 'close connect error length', packlen
                break

            # 获取包体 收全包体
            body = ''
            status, body = utils.recv_body(clnt_s, packlen)
            if error_pb2.SUCCESS != status:
                print('\033[31mRecv Wrong %d %d\033[0m' % (packlen, len(body)))
                break

            snddata = ''
            # print('cmd 0x%x login %d' % (cmd, login_flag))
            if base_pb2.CMD_LOGIN_REQ == cmd:
                lgn = base_pb2.LoginReq()
                lgn.ParseFromString(body)
                pi = package_info(cmd, rid, lgn)
                sess = self.login_handle(clnt_s, pi)
                login_flag = sess.login
            elif 0 == login_flag:
                status = self.package_handle(cmd, rid, body, sess)
            else:
                print 'login first'

                # num = clnt_s.send(snddata)
                # print ('snddata %d (%r)' % (num, snddata))

        print 'disconnect close socket'
        clnt_s.close()


# def package_handle(self, clnt_s, sysid, cmd, seq, body):
#        snddata = ''
#        return snddata
VERSION = base_pb2.MAJOR << 16 or base_pb2.MINOR

from common import constant


# -----------------------------------------------------------------------------
class RiskSvr(BaseServer):
    sn = 0
    swn = 0
    bn = 0
    ssss = 0

    def __init__(self, addr):
        super(RiskSvr, self).__init__(addr)

    def package_handle(self, cmd, rid, body, sess):
        snddata = ''
        if base_pb2.CMD_SINGLE_ORDER_REQ == cmd:
            print 'CMD_SINGLE_ORDER_REQ'
            sng_order = stock_trade_pb2.SingleOrderReq()
            sng_order.ParseFromString(body)
            pi = package_info(cmd, rid, sng_order, sess)
            self.single_order_req(sess, pi)
            import time
            # time.sleep(2)
            # self.single_cancel_req_c(sess, 'sn0000%02d' % self.sn, pi.pack.policy_id)
            time.sleep(2)
            self.single_knock(sess, 'sn0000%02d' % self.sn, pi.pack.bs_flag, pi.pack.market, pi.pack.code,
                              pi.pack.policy_id)
        elif base_pb2.CMD_SINGLE_WITHDRAWAL_REQ == cmd:
            print 'CMD_SINGLE_WITHDRAWAL_REQ'
            s_cancel = stock_trade_pb2.SingleCancelReq()
            s_cancel.ParseFromString(body)
            pi = package_info(cmd, rid, s_cancel, sess)
            self.single_cancel_req(sess, pi)


        # elif base_pb2.CMD_SINGLE_WITHDRAWAL_REQ == cmd:
        #     s_withdrawal = stock_trade_pb2.SingleCancelReq()
        #     s_withdrawal.ParseFromString(body)
        #     pi = package_info(cmd, s1, s2, s3, s4, s_withdrawal, clnt_s)
        #     status, snddata = self.single_withdrawal_req(clnt_s, pi)
        # elif base_pb2.CMD_BATCH_ORDER_REQ == cmd:
        #     bo = stock_trade_pb2.StockBatchOrderReq()
        #     if self.ssss < 10:
        #         print('%d\n%r' % (self.ssss, body))
        #         self.ssss += 1
        #     try:
        #         bo.ParseFromString(body)
        #     except:
        #         print('\033[31mpacklen %d seq %d 0x%x' % (pcklen, s3, s4))
        #         print('body %d\n%r\033[0m' % (len(body), body))
        #     pi = package_info(cmd, s1, s2, s3, s4, bo, clnt_s)
        #     status, snddata = self.batch_order_req(clnt_s, pi)
        else:
            print('unknow cmd 0x[%x]' % cmd)
        return error_pb2.SUCCESS

    # --------------------------------------------------------------------------
    def login_handle(self, clnt_s, pi):
        pack = pi.pack
        sess = Sesstion(pack.trader_id, clnt_s)
        login_resp = base_pb2.LoginResp()
        if pack.version >= VERSION:
            login_resp.result = error_pb2.SUCCESS
            login_resp.version = pack.version
            sess.login = error_pb2.SUCCESS
            pi.sess = sess
        else:
            login_resp.result = error_pb2.ERROR_UPDATE
            login_resp.version = VERSION

        snddata = utils.make_package(
                base_pb2.SYS_ROBOT, base_pb2.CMD_LOGIN_RESP, pi.rid, login_resp)
        sess.send_package(snddata)
        return sess

    def single_cancel_req(self, sess, pi):
        print 'risksvr receive SingleCancelReq'
        s_cancel_resp = stock_trade_pb2.SingleOrderResp()
        s_cancel_resp.ret_code = error_pb2.SUCCESS
        s_cancel_resp.order_no = pi.pack.order_no
        s_cancel_resp.policy_id = pi.pack.policy_id
        snddata = utils.make_package(base_pb2.SYS_ROBOT, base_pb2.CMD_SINGLE_WITHDRAWAL_RESP, pi.rid, s_cancel_resp)
        sess.send_package(snddata)

    def single_cancel_req_c(self, sess, order_no, policy_id):
        print 'risksvr receive SingleCancelReq'
        s_cancel_resp = stock_trade_pb2.SingleOrderResp()
        s_cancel_resp.ret_code = error_pb2.SUCCESS
        s_cancel_resp.order_no = order_no
        s_cancel_resp.policy_id = policy_id

        snddata = utils.make_package(base_pb2.SYS_ROBOT, base_pb2.CMD_SINGLE_WITHDRAWAL_RESP, uuid.uuid1(),
                                     s_cancel_resp)
        sess.send_package(snddata)

    def single_knock(self, sess, order_no, bs_flag, market, stock_id, policy_id):
        """模拟单笔撤单成交回报"""
        s_kncok_pub = stock_trade_pb2.QueryStockKnockResponse()
        s_kncok_pub.ret_code = 0
        s_knock = s_kncok_pub.stock_knock.add()
        s_knock.fund_id = '123'
        s_knock.bs_flag = bs_flag
        s_knock.order_no = order_no
        s_knock.market = market
        s_knock.stock_id = stock_id
        s_knock.match_type = constant.MATCH_TYPE_NORMAL
        # s_knock.match_type = constant.MATCH_TYPE_WITHDRAWS
        s_knock.inner_match_no = 'inner_match_no'
        s_knock.match_time = 123
        s_knock.match_volume = 1000000
        s_knock.policy_id = policy_id
        s_knock.data_date = 123
        s_knock.create_time = timeUtils.getCurrentTotalMSeconds()
        print 'risksvr send cancel knock: [%s]' % s_kncok_pub
        snddata = utils.make_package(base_pb2.SYS_ROBOT, base_pb2.CMD_SUB_STOCK_KNOCK_REQ, uuid.uuid1(), s_kncok_pub)
        sess.send_package(snddata)
        return error_pb2.SUCCESS

    # --------------------------------------------------------------------------
    def single_order_req(self, sess, pi):
        # print('single_order_req seg %d %d' % (pi.s3, pi.s4))
        self.sn += 1
        print 'risksvr receive SingleOrderReq: [%s]' % pi.pack

        sng_ord_resp = stock_trade_pb2.SingleOrderResp()
        sng_ord_resp.ret_code = error_pb2.SUCCESS
        sng_ord_resp.order_no = 'sn0000%02d' % self.sn
        # sng_ord_resp.ret_message = 'risksvr ok'
        sng_ord_resp.policy_id = pi.pack.policy_id

        print 'risksvr send SingleOrderResp: [%s]' % sng_ord_resp
        snddata = utils.make_package(
                base_pb2.SYS_ROBOT, base_pb2.CMD_SINGLE_ORDER_RESP, pi.rid,
                sng_ord_resp)
        sess.send_package(snddata)

        return error_pb2.SUCCESS
        # socket.send(snddata)

    # --------------------------------------------------------------------------
    def single_withdrawal_req(self, clnt_s, pi):
        # print('wwwwwwwwwwwwwwwwww', pi)
        self.swn += 1
        s_withdrawal_resp = stock_trade_pb2.SingleOrderResp()
        s_withdrawal_resp.ret_code = error_pb2.SUCCESS
        s_withdrawal_resp.order_no = 'weibu8000%02d' % self.swn
        snddata = utils.make_package(
                base_pb2.SYS_ROBOT, base_pb2.CMD_SINGLE_WITHDRAWAL_RESP, pi,
                s_withdrawal_resp)
        return error_pb2.SUCCESS, snddata

    # --------------------------------------------------------------------------
    def batch_order_req(self, clnt_s, pi):
        # print('%s bn %d cnt %d' % ('=' * 50, self.bn, len(pi.pack.order_list)))
        # print pi
        snddata = ''
        self.bn += 1

        bo_resp = stock_trade_pb2.StockBatchOrderResp()
        bo_resp.ret_code = error_pb2.SUCCESS
        bo_resp.groupid = pi.pack.groupid
        # bo_resp.ret_message
        bo_resp.batch_no = 'bon700000%02d' % self.bn
        for i in xrange(len(pi.pack.order_list)):
            single = bo_resp.order_resp_list.add()
            self.sn += 1
            if 1 == pi.s4 % 2:
                if 0 == i % 2:
                    single.ret_code = error_pb2.SUCCESS
                    single.order_no = 'sn0000%02d' % self.sn
                else:
                    single.ret_code = error_pb2.ERROR_WAIT
                    single.order_no = 'sn8000%02d' % self.sn
            else:
                single.ret_code = error_pb2.SUCCESS
                single.order_no = 'sn0000%02d' % self.sn

        snddata = utils.make_package(
                base_pb2.SYS_ROBOT, base_pb2.CMD_BATCH_ORDER_RESP, pi,
                bo_resp)
        return error_pb2.SUCCESS, snddata

        # --------------------------------------------------------------------------


# -----------------------------------------------------------------------------
def server_start(app):
    # socksvr.start()
    app.svr.serve_forever()
    print 'x2' * 30


# # --------------------------------------------------------------------------
def main():
    import yaml
    with open('robot.yaml') as f:
        cfg = yaml.load(f)
    rip = cfg['risksvr']['rip']
    rport = cfg['risksvr']['rport']
    print 'risksvr listen on ip: [%s] port :[%s]' % (rip, rport)
    svr = RiskSvr((rip, rport))
    jobs = []
    jobs.append(gevent.spawn(server_start, svr))
    gevent.joinall(jobs)


if __name__ == '__main__':
    ret = main()
    sys.exit(ret)
    print ('main')
