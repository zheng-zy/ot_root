#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""  etf class
"""

# import math
import gevent

from pb import base_pb2
# import quotation_def_pb2

__author__ = 'qinjing'

# RF_MUST = 0
# RF_ALLOW = 1
# RF_FORBIDDEN = 2


# class StockInfo:
#         # 股票代码, 数量
#     __slots__ = ['code', 'md']
#
#     def __init__(self, code):
#         self.code = code
#         # self.price = qty
#         self.md = None
#         self.market = base_pb2.MKT_SH
#
#     def __str__(self):
#         return ('price %s:%s qty %s flag %d payment %d' % (self.bprc[0],
#                 self.sprc[0], self.qty, self.rflag, self.payment))
#
#     def price(self, pl, bs_flag):
#         if base_pb2.PRICE_2_PERCENT == pl:
#             if base_pb2.OPR_BUY == bs_flag:
#                 price = self.prices[base_pb2.PRICE_CURRENT] * 1.02
#                 if price > self.prices[base_pb2.LIMIT_UP]:
#                     price = self.prices[base_pb2.LIMIT_UP]
#             elif base_pb2.OPR_SELL == bs_flag:
#                 price = self.prices[base_pb2.PRICE_CURRENT] * 0.98
#                 if price < self.prices[base_pb2.LIMIT_DOWN]:
#                     price = self.prices[base_pb2.LIMIT_DOWN]
#             else:
#                 print('error bs flag 0x%x' % (bs_flag))
#                 price = self.prices[base_pb2.PRICE_CURRENT]
#         else:
#             price = self.prices[pl]
#
#         return price


# -------------------------------------------------------------------
class StockInfo(object):
    __slots__ = ('stkcode', 'mkid', 'md', 'buy', 'sell', 'purchase',
                 'redeem', 'qty', 'opr')

    def __init__(self, code, mkid, market_data=None):
        self.mkid = mkid
        self.md = market_data
        self.stkcode = code
        self.buy = 0
        self.sell = 0
        self.purchase = 0
        self.redeem = 0
        # qty[etfcode] = etf_qty
        self.qty = {}

    def price(self, pl, bs_flag):
        i = 0
        while self.md is None and i < 5:
            gevent.sleep(1)
            # print('%s no quotation %r' % (self.stkcode, self))
            i += 1
        else:
            if self.md is None:
                print('stock def %s price 1' % (self.stkcode))
                return 1

        if pl > 100:
            r = float(pl) / 100000
            if base_pb2.OPR_BUY == bs_flag:
                price = self.md.match * (1 + r)
                if price > self.md.high_limited:
                    price = self.md.high_limited
            elif base_pb2.OPR_SELL == bs_flag:
                price = self.md.match * (1 - r)
                if price < self.md.low_limited:
                    price = self.md.low_limited
            else:
                print('error bs flag 0x%x' % (bs_flag))
                price = self.md.ask_price

            # 停牌???
            if 0 == price:
                print 'price == 0 %s %d %d' % (self.stkcode, self.md.pre_close, self.md.match)
                price = self.md.pre_close
            return price

        # if base_pb2.PRICE_2_PERCENT == pl:
        #     if base_pb2.OPR_BUY == bs_flag:
        #         price = self.md.match * 1.02
        #         if price > self.md.high_limited:
        #             price = self.md.high_limited
        #     elif base_pb2.OPR_SELL == bs_flag:
        #         price = self.md.match * 0.98
        #         if price < self.md.low_limited:
        #             price = self.md.low_limited
        #     else:
        #         print('error bs flag 0x%x' % (bs_flag))
        #         price = self.md.ask_price
        if base_pb2.LIMIT_DOWN == pl:
            price = self.md.low_limited
        elif base_pb2.LIMIT_UP == pl:
            price = self.md.high_limited
        elif base_pb2.PRICE_MATCH == pl:
            price = self.md.match
        elif pl > base_pb2.PRICE_MATCH:
            price = self.md.bid_price[pl - base_pb2.S_1]
        elif pl >= base_pb2.B_10:
            price = self.md.ask_price[pl - base_pb2.B_10]
        else:
            price = self.md.match
            print('error price level %d' % (pl))

        return price


# -----------------------------------------------------------------------------
class EtfInfo(object):

    # 510050 （交易代码） 510051 （申赎代码）
    # 一级市场, 二级市场, 现金差额, 预估现金, 最小申购、赎回单位净值,
    # 最小申购、赎回单位, 现金替代比例上限
    __slots__ = ('etfcode', 'stcks', 'buy', 'sell', 'purchase', 'redeem',
                 'etf_base_info', 'count')

    def __init__(self, code, stklist=None):
        self.etfcode = code
        self.stcks = {}
        self.stcks[base_pb2.MKT_SZ] = []
        self.stcks[base_pb2.MKT_SH] = []
        self.stcks[base_pb2.MKT_CF] = []
        # self.stcks[base_pb2.MKT_SZ] = {}
        # self.stcks[base_pb2.MKT_SH] = {}
        # self.stcks[base_pb2.MKT_CF] = {}
        self.buy = 0
        self.sell = 0
        self.purchase = 0
        self.redeem = 0
        self.count = 0
        self.etf_base_info = None

        if stklist is not None:
            for stk_code in stklist:
                stock = self.StockInEtf(stk_code, 100, 1, 10, 2000)
                self.etf_stks.append(stock)

    # # 买价计算净值
    # def iopv_b(self, bi):
    #     pstk = (sts[st].payment for st in self.etf_stks
    #             if base_pb2.RF_MUST == sts[st].rflag)
    #     mcash = math.fsum(pstk)
    #     print mcash

    #     allow = (sts[st].bprc[bi] * sts[st].qty for st in self.etf_stks
    #              if RF_ALLOW == sts[st].rflag)
    #     acash = math.fsum(allow)
    #     for l in allow:
    #         print 'allow', l
    #     print 'acash', acash

    #     forbid = (sts[st].bprc[bi] * sts[st].qty for st in self.etf_stks
    #               if RF_FORBIDDEN == sts[st].rflag)
    #     fcash = math.fsum(forbid)
    #     print 'fcash', fcash

    #     sumcash = ((mcash + fcash + acash + self.estimated) / self.min_unit)
    #     return sumcash

    # # 卖价计算净值
    # def iopv_s(self, si):
    #     pstk = (sts[st].payment for st in self.etf_stks
    #             if base_pb2.RF_MUST == sts[st].rflag)
    #     mcash = math.fsum(pstk)
    #     print mcash

    #     allow = (sts[st].sprc[si] * sts[st].qty for st in self.etf_stks
    #              if RF_ALLOW == sts[st].rflag)
    #     acash = math.fsum(allow)
    #     print 'acash', acash

    #     forbid = (sts[st].sprc[si] * sts[st].qty for st in self.etf_stks
    #               if RF_FORBIDDEN == sts[st].rflag)
    #     fcash = math.fsum(forbid)
    #     print 'fcash', fcash

    #     sumcash = ((mcash + fcash + acash + self.estimated) / self.min_unit)
    #     return sumcash

    # class StockInEtf:
    #     # 股票代码, 数量, 现金替代标志, 溢价比率, 替代金额
    #     __slots__ = ('stkcode', 'quo', 'buy', 'sell', 'purchase', 'redeem', )

    #     def __init__(self, code):
    #         self.stkcode = code
    #         self.quo = None
    #         self.buy = 0
    #         self.sell = 0
    #         self.purchase = 0
    #         self.redeem = 0
    #         # self.market = base_pb2.MKT_UNKNOW
    #         # if quotation_def_pb2.RF_MUST == replace_flag:
    #         #     self.payment = payment
    #         # else:
    #         #     self.payment = 0

    #     def __str__(self):
    #         return ('buy %d sell %d purchase %s redeem %d quo %r' %
    #                 (self.buy, self.sell, self.purchase,  self.redeem,
    #                 self.quo))
# eee = etf(111, 222, 333, 0.0003)
# for i in range(10):
#     code = i * 10000 + i
#     st = stockinfo(code, 1.2, 1000, i % 3, 0.1, i * 1000 + i)
#     eee.etf_stks.append(code)
#     sts[code] = st
#     #eee.sts.append(st)
#     print st
#
# # for stcode in eee.sts:
# #     st = sts[stcode]
# #     print 'price flag', st.price, st.rflag
#
# print eee.iopv_b(0)
# print eee.iopv_s(0)
