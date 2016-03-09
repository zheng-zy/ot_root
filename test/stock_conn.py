#!/usr/bin/env python
# -*- coding: utf-8 -*-


""" connection of stock server
"""


import gevent
# from gevent import socket
import struct
import yaml
# import time
from common import utils
from net import baseclient
from pb import base_pb2
from pb import stock_trade_pb2


__author__ = 'qinjing'


# -----------------------------------------------------------------------------
class StackConn(baseclient.BaseClient):
    def __init__(self, app, addr, handler=None):
        super(StackConn, self).__init__(app, addr, handler)

    def after_connect(self, err):
        print('\033[5;31;1mstock server connect %d\033[0m' % (err))
        fmt = ">iHHiiii"
        # fmt = ">iHH16s"
        # size = struct.calcsize(fmt)
        login = base_pb2.LoginReq()
        login.type = base_pb2.MANUAL_TRADE
        login.trader_id = self.app.rid
        login.version = base_pb2.MAJOR << 16 or base_pb2.MINOR
    #     headbuffer = struct.pack(fmt, login.ByteSize(), base_pb2.SYS_MTC,
    #                              base_pb2.CMD_LOGIN_REQ, 0, 0, 0, seq)
        # seq += 1
        headbuffer = struct.pack(fmt, login.ByteSize(), base_pb2.SYS_STOCK,
                                 base_pb2.CMD_LOGIN_REQ, 0, 0, 0, 0)
        sentdata = headbuffer + login.SerializeToString()
        self.svr_sock.sendall(sentdata)

        sub = stock_trade_pb2.SubTradeMsgRequest()
        sub.type = base_pb2.SUB_STOCK_KNOCK | base_pb2.SUB_STOCK_POSITION
        headbuffer = struct.pack(fmt, sub.ByteSize(), base_pb2.SYS_STOCK,
                                 base_pb2.CMD_SUBSCRIBE_TRADE_REQ, 0, 0, 0, 1)
        sentdata = headbuffer + sub.SerializeToString()
        self.svr_sock.sendall(sentdata)
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
            print('stock unknow cmd 0x%x' % (pi.cmd))

    def stock_position_resp_handle(self, pi):
        self.etfs[pi.pack.etf_code] = pi.pack
        # if pi.pack.etf_code == '510300':
        #     print pi.pack

    # ---------------------------------------------------------------------
    def query_position(self, s3, s4, seq_opr):
        pack = stock_trade_pb2.QueryPositionRequest()

        snddata = utils.make_package_num(
            base_pb2.SYS_STOCK,
            base_pb2.CMD_QUERY_STOCK_POSITION_REQ, s3, s4, pack)

        self.send_package(snddata)
        print 'query_positino'

    # def try_send(self, cmd, pack):
    #     fmt = ">iHHiiii"
    #     headbuffer = struct.pack(fmt, pack.ByteSize(), base_pb2.SYS_STOCK,
    #                              cmd, base_pb2.SYS_STOCK, s3, s4, self.seq)
    #     self.seq += 1
    #     snddata = headbuffer + pack.SerializeToString()


# -----------------------------------------------------------------------------
class app(object):
    rid = 'stock_con_test'


# ----------------------------------------------------------------------------
def main():
    # pre_quo = PreQuotation_1(None, ('192.168.1.176', 9114))
    with open('robot.yaml') as f:
        cfg = yaml.load(f)
    stock_ip = cfg['stocksvr']['sip']
    stock_port = cfg['stocksvr']['port']
    print stock_ip, stock_port
    stock_sock = StackConn(app, (stock_ip, stock_port))
    jobs = []
    jobs.append(gevent.spawn(stock_sock.recv_data))
    gevent.joinall(jobs)


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    main()
