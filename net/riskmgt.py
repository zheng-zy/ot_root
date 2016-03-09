#!/usr/bin/env python
# -*- coding=utf-8 -*-

import gevent
# from gevent import socket
import struct
# import uuid
# import time
from common import utils
import baseclient
from pb import base_pb2
from pb import stock_trade_pb2

# Last modified: 15-12-13 01:39:23


__author__ = 'qinjing'


# -----------------------------------------------------------------------------
class RiskMgt(baseclient.BaseClient):
    def __init__(self, app, addr, handler=None):
        super(RiskMgt, self).__init__(app, addr, handler)

    def after_connect(self, err):
        fmt = ">iHHiiii"
        login = base_pb2.LoginReq()
        login.type = base_pb2.MANUAL_TRADE
        login.trader_id = self.app.rid
        login.version = base_pb2.MAJOR << 16 or base_pb2.MINOR
        headbuffer = struct.pack(fmt, login.ByteSize(), base_pb2.SYS_STOCK,
                                 base_pb2.CMD_LOGIN_REQ, 0, 0, 0, 0)
        sentdata = headbuffer + login.SerializeToString()
        self.svr_sock.sendall(sentdata)
        print('\033[5;31;1mrrrrrrrrr connect %d\033[0m' % (err))
        return

    def package_handle(self, packlen, pi, body):
        if base_pb2.CMD_ASSET_REQ == pi.cmd:
            pass
        elif base_pb2.CMD_SUB_ASSET_REQ == pi.cmd:
            print('  CMD_SUB_ASSET_REQ :')
            print pi.pack
        elif base_pb2.CMD_SUB_STOCK_POSITION_REQ == pi.cmd:
            # print('  CMD_SUB_STOCK_POSITION_REQ :')
            print pi.pack
        elif base_pb2.CMD_STOCK_POSITION_REQ == pi.cmd:
            pack = stock_trade_pb2.QueryPositionResponse()
            pack.ParseFromString(body)
            pi.pack = pack
            self.stock_position_resp_handle(pi)
            pass
        elif base_pb2.CMD_STOCK_KNOCK_REQ == pi.cmd:
            pack = stock_trade_pb2.QueryStockKnockResponse()
            pack.ParseFromString(body)
            pi.pack = pack
            self.stock_knock_resp_handle(pi)
            pass
        elif base_pb2.CMD_STOCK_ORDER_REQ == pi.cmd:
            pack = stock_trade_pb2.QueryStockOrderResponse()
            pack.ParseFromString(body)
            pi.pack = pack
            self.stock_order_resp_handle(pi)
            pass
        elif base_pb2.CMD_HEARTBEAT_REQ == pi.cmd:
            fmt = ">iHHiiii"
            headbuffer = struct.pack(
                    fmt, 0, base_pb2.SYS_STOCK, base_pb2.CMD_HEARTBEAT_RESP,
                    1, 0, 0, 0)
            self.svr_sock.sendall(headbuffer)
        else:
            print('riskmgt unknow cmd 0x%x' % (pi.cmd))

    def stock_position_resp_handle(self, pi):
        self.etfs[pi.pack.etf_code] = pi.pack
        # if pi.pack.etf_code == '510300':
        #     print pi.pack

    # --------------------------------------------------------------------------
    def send_package(self, pack):
        # self.svr_sock.send(pack)
        try:
            self.svr_sock.send(pack)
        except Exception, e:
            print('\033[31msomething wrong!!!! %s \033[0m' % (e))
            self.reconnect_server(10)
            self.svr_sock.send(pack)

    # --------------------------------------------------------------------------
    def query_position(self, seq_opr):
        pack = stock_trade_pb2.QueryPositionRequest()
        snddata = utils.make_package(
                base_pb2.SYS_STOCK, base_pb2.CMD_QUERY_STOCK_POSITION_REQ,
                seq_opr.pi, pack)
        self.send_package(snddata)

    # --------------------------------------------------------------------------
    def make_and_send(self, cmd, s3, s4, pack):
        snddata = utils.make_package_num(
                base_pb2.SYS_STOCK, cmd, s3, s4, pack)
        self.send_package(snddata)

    def make_and_send_rid(self, cmd, rid, pack):
        snddata = utils.make_package(base_pb2.SYS_STOCK, cmd, rid, pack)
        self.send_package(snddata)


# ------------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class App(object):
    rid = 'stock_con_test'


# -----------------------------------------------------------------------------
def main():
    # pre_quo = PreQuotation_1(None, ('192.168.1.176', 9114))
    with open('robot.yaml') as f:
        import yaml
        cfg = yaml.load(f)
    riskip = cfg['risksvr']['rip']
    riskport = cfg['risksvr']['rport']
    print riskip, riskport
    app = App()
    riskip = '127.0.0.1'
    riskport = 9991
    stock_sock = RiskMgt(app, (riskip, riskport))
    jobs = []
    jobs.append(gevent.spawn(stock_sock.recv_data))
    gevent.joinall(jobs)


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    main()
