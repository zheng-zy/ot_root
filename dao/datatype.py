#!/usr/bin/env python
# -*- coding: utf-8 -*-


""" global data type define
"""

# import gevent
# # from gevent import socket
# from gevent.server import StreamServer
#
import collections

# import base_pb2


__author__ = 'qinjing'


class BatchGroup(object):
    def __init__(self, gid):
        self.gid = gid
        self.bno = None
        self.stklist = []
        self.bg_phase = -1

    def __str__(self):
        sss = ''
        return ''
        for bi in self.stklist:
            sss += bi.stkcode + ', '
        return 'gid:%s bno:%s len(stk):%d\n\t%s' % \
               (self.gid, self.bno, len(self.stklist), sss)


# -----------------------------------------------------------------------------
class BInfo(object):
    __slots__ = ('stkcode', 'policyid', 'order_no',
                 'qty', 'remain_qty', 'stkinfo')

    def __init__(self, code, qty, policyid, stkinfo):
        self.stkcode = code
        self.policyid = policyid
        self.order_no = None
        self.qty = qty
        self.remain_qty = qty
        self.stkinfo = stkinfo

    def __str__(self):
        return 'code:%s ' % \
               (self.stkcode)


#
# BatItem = collections.namedtuple('BatchItemInfo', 'code qty pl key ')


# -----------------------------------------------------------------------------
class package_info(object):
    __slots__ = ('cmd', 's1', 's2', 's3', 's4', 'pack', 'sess', 'opr', 'sock')

    def __init__(self, cmd, s1, s2, s3, s4, pack=None, sess=None):
        self.cmd = cmd
        # self.basecmd = cmd
        self.s1 = s1
        self.s2 = s2
        self.s3 = s3
        self.s4 = s4
        self.opr = 0
        self.pack = pack
        # self.sock = sock
        if sess is not None:
            assert isinstance(sess, Sesstion)
            self.sess = sess
        if (sess is not None):
            self.sock = sess.sock

    def __str__(self):
        return ('cmd:0x%x seq:%s-%s-%s-%s sock:%s sess %s\npack:%s' %
                (self.cmd, self.s1, self.s2, self.s3,
                 self.s4, self.sess, self.sess, self.pack))


# ------------------------------------------------------------------------
# class StockInfo(object):
#     __slots__ = ('stkcode', 'mkid', 'md', 'buy', 'sell',
#                  'purchase', 'redeem')
#
#     def __init__(self, code, mkid, market_data=None):
#         self.mkid = mkid
#         self.md = market_data
#         self.stkcode = code
#         self.buy = 0
#         self.sell = 0
#         self.purchase = 0
#         self.redeem = 0
#
#     def price(self, pl, bs_flag):
#         # if base_pb2.PRICE_2_PERCENT == pl:
#         #     if base_pb2.OPR_BUY == bs_flag:
#         #         price = self.prices[base_pb2.PRICE_CURRENT] * 1.02
#         #         if price > self.prices[base_pb2.LIMIT_UP]:
#         #             price = self.prices[base_pb2.LIMIT_UP]
#         #     elif base_pb2.OPR_SELL == bs_flag:
#         #         price = self.prices[base_pb2.PRICE_CURRENT] * 0.98
#         #         if price < self.prices[base_pb2.LIMIT_DOWN]:
#         #             price = self.prices[base_pb2.LIMIT_DOWN]
#         #     else:
#         #         print('error bs flag 0x%x' % (bs_flag))
#         #         price = self.prices[base_pb2.PRICE_CURRENT]
#         # else:
#         #     price = self.prices[pl]
#
#         if base_pb2.PRICE_2_PERCENT == pl:
#             if base_pb2.OPR_BUY == bs_flag:
#                 price = self.md.match * 1.02
#                 if price > self.md.high_limited:
#                     price = self.md.high_limited
#             elif base_pb2.OPR_SELL == bs_flag:
#                 price = self.md.match * 0.98
#                 if price < self.md.low_limited:
#                     price = self.md.low_limited
#             else:
#                 print('error bs flag 0x%x' % (bs_flag))
#                 price = self.md.ask_price
#         elif base_pb2.LIMIT_DOWN == pl:
#             price = self.md.low_limited
#         elif base_pb2.LIMIT_UP == pl:
#             price = self.md.high_limited
#         elif pl > base_pb2.PRICE_MATCH:
#             price = self.md.bid_price[pl - base_pb2.S_1]
#         elif pl >= base_pb2.B_10:
#             price = self.md.ask_price[pl - base_pb2.B_10]
#         else:
#             price = self.md.match
#             print('error price level %d' % (pl))
#
#         return price


class Sesstion(object):
    def __init__(self, tid, sock):
        self.tid = tid
        self.sock = sock
        self.login = -1
        self.closed = 0

    def __str__(self):
        return 'tid:%s sock:%s' % (self.tid, self.sock)

    def close(self):
        self.closed = 1
        self.sock.close()

    def send_package(self, pack):
        if 0 == self.closed:
            try:
                self.sock.send(pack)
            except Exception, e:
                print('\033[31msomething wrong!!!! %s \033[0m' % (e))
