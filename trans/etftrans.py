#!/usr/bin/env python
# -*- coding: utf-8 -*-


import gevent
import time

from common import utils
import basket
import message

from dao.datatype import BatchGroup
# from datatype import BInfo


from pb import base_pb2
from pb import error_pb2
from pb import ot_pb2
from pb import stock_trade_pb2


RED = '\033[31m'
GREEN = '\033[32m'
BLUE = '\033[33m'
CLEAR = '\033[0m'


# -----------------------------------------------------------------------------
class TranETF(object):
    __slots__ = ('robot', 'key', 'policyid', 'etfcode', 'pr_remain_qty',
                 'bs_remain_qty', 'order_no', 'count', 'pi',
                 'task', 'opr', 's3', 'pr_volume',
                 'bs_volume', 'status_id', )

    def __init__(self, robot, key, pi, policyid, opr, etfcode, volume,
                 count=0):
        self.robot = robot
        self.count = count
        self.pi = pi
        self.task = []
        # self.phase = pi.cmd
        self.s3 = 0
        self.pr_volume = volume
        self.bs_volume = volume
        # self.etf = etf
        self.policyid = policyid
        self.opr = opr
        self.key = key
        self.status_id = 0
        self.etfcode = etfcode
        self.pr_remain_qty = 0
        self.bs_remain_qty = 0

        if base_pb2.CMD_STOCK_CREATE_OR_REDEEM_POLICY == pi.cmd:
            self.robot.set_transaction(key, self)

    # ------------------------------------------------------------------------
    def etf_purchase_redeem(self, volume, flag, policyid, etf):
        self.pr_remain_qty = volume
        self.bs_remain_qty = volume
        order = stock_trade_pb2.SingleOrderReq()
        pi = self.pi
        # str(int(self.etfcode) + 1)
        order.code = etf.etf_base_info.etf_p_r_code
        order.price = 0
        order.qty = volume * etf.etf_base_info.creation_redemption_unit  #
        order.bs_flag = flag                #
        if policyid is None:
            policyid = self.policyid
        if policyid is None:
            policyid = self.robot.get_policy_id_sub(self.key)
        order.policy_id = policyid
        order.trader_id = pi.pack.base_param.trader_id
        order.trader_ip = pi.pack.base_param.trader_ip
        mkid, stkinf = self.robot.quo.try_get_id(self.etfcode)
        if stkinf is None:
            if self.etfcode.find('510') >= 0:
                order.market = 1
            else:
                order.market = 0
        else:
            order.market = mkid

        print '\033[5;1;31m'
        print order
        print CLEAR
        self.task.append((policyid, base_pb2.CMD_ETF_ORDER_REQ))

        s3 = self.robot.get_seq()
        self.s3 = s3

        self.robot.riskmgt.make_and_send(base_pb2.CMD_ETF_ORDER_REQ, s3,
                                         base_pb2.CMD_ETF_ORDER_REQ, order)

        return error_pb2.SUCCESS

    # ------------------------------------------------------------------------
    # def etf_basket_old(self, opr, price):
    #     totalcash = 0
    #     tid = self.pi.sess.tid
    #     s4 = 0
    #     batgrp = BatchGroup(s4)

    #     etf = None
    #     s3 = self.robot.get_seq()
    #     stk_batch = stock_trade_pb2.StockBatchOrderReq()
    #     stk_batch.policy_id = self.key
    #     print('bbs %s %d' % (etf.etfcode, len(etf.etf_base_info.etf_list)))
    #     for mkid, etfstks in etf.stcks.items():
    #         for stk_info in etfstks:
    #             if len(stk_batch.order_list) < base_pb2.MAX_BATCH:
    #                 cash = self.robot.batch_item_new(
    #                     stk_batch, stk_info, batgrp, self.pi.pack.volume,
    #                     opr, self.key, tid, etf.etfcode, price)
    #                 totalcash += cash

    #             elif len(stk_batch.order_list) == base_pb2.MAX_BATCH:
    #                 snddata = basket.make_package_num(
    #                     base_pb2.CMD_BATCH_ORDER_REQ, s3, s4, stk_batch)
    #                 self.robot.riskmgt.send_package(snddata)
    #                 self.batchs[s4] = batgrp
    #                 print('\033[34mkey %s mkid %d s3 %d s4 0x%x pcklen'
    #                       '%d\033[0m\n' %
    #                       (self.key, mkid, s3, s4, stk_batch.ByteSize()))
    #                 s4 += 1

    #                 batgrp = BatchGroup(s4)
    #                 stk_batch = stock_trade_pb2.StockBatchOrderReq()
    #                 stk_batch.policy_id = self.key
    #                 cash = self.robot.batch_item_new(
    #                     stk_batch, stk_info, batgrp, self.pi.pack.volume,
    #                     opr, self.key, tid, etf.etfcode, price)
    #                 totalcash += cash

    #         snddata = basket.make_package_num(
    #             base_pb2.CMD_BATCH_ORDER_REQ, s3, s4, stk_batch)
    #         self.robot.riskmgt.send_package(snddata)
    #         self.batchs[s4] = batgrp
    #         s4 += 1

    #     self.totalcash = totalcash

    #     snddata = basket.make_package_num(
    #         base_pb2.CMD_BATCH_ORDER_REQ,
    #         s3, s4, stk_batch)
    #     self.robot.riskmgt.send_package(snddata)
    #     self.batchs[s4] = batgrp

    #     print('\033[34mput %s in s3 %d 0x%x pcklen %d\033[0m\n' %
    #           (self.key, s3, s4, stk_batch.ByteSize()))  # self))

    #     # for gid, batgrp in seq_opr.batchs.items():
    #     #     print('gid %d' % (gid))
    #     #     for bi in batgrp.stklist:
    #     #         print('\tcode %s qty %d' % (bi.stkcode, bi.qty))

    def knock_handle(self, pi, sknock):
        if ((base_pb2.OPR_PURCHASE == sknock.order_bs_flag or
             base_pb2.OPR_REDEEM == sknock.order_resp_list)):
            self.pr_remain_qty -= sknock.match_volume
        else:
            self.bs_remain_qty -= sknock.match_volume
        print 'tranetf knock_handl', sknock

    def get_status(self, pi, sknock):
        status = message.PLC_STS_PROGRESSED
        if self.pr_remain_qty == 0 or self.bs_remain_qty == 0:
            status = message.PLC_STS_FINISHED

        return status

    def policy_status(self, pi, sknock):
        self.status_id += 1

        # self.robot.send_policy_status(
        #     self.pi.sess, self.pi, sknock.policy_id,
        #     error_pb2.SUCCESS, status, self.status_id)

        ps = ot_pb2.PolicyStatus()
        ps.policy_id = sknock.policy_id
        ps.time_stamp = int(time.time())
        err = ot_pb2.Error()
        err.code = error_pb2.SUCCESS
        ps.err.code = error_pb2.SUCCESS
        ps.status = self.get_status()
        ps.status_id = self.status_id
        ps.robot_ip = self.robot.rip

        # print'etf policy_status remain_qty %d volume %d ps\n%s' % (
        #     self.remain_qty, self.volume, ps)

        snddata = utils.make_package(
            base_pb2.SYS_MTC,
            base_pb2.CMD_POLICY_STATUS, pi, ps)
        return snddata


# -----------------------------------------------------------------------------
class TranBuyPurchase(basket.TranBasket):
    """ basket buy sell withdrawal submit, auto """

    def __init__(self, robot, key, pi, etf, count, ):
        super(TranBuyPurchase, self).__init__(
            robot, key, pi, etf.etfcode, count,
            base_pb2.OPR_BUY, base_pb2.OPR_BUY_PURCHASE)
        self.etf = etf
        self.phase = base_pb2.CMD_BATCH_ORDER_REQ
        self.opr = base_pb2.OPR_BUY_PURCHASE
        self.etftran = None

    def __str__(self):
        return ('TBP: %d btch: %d\n%s\n%s' %
                (len(self.task), len(self.batchs), self.task, self.batchs))

    # ------------------------------------------------------------------------
    def etf_basket(self, opr, pl):
        totalcash = 0
        tid = self.pi.sess.tid
        s4 = 0
        batgrp = BatchGroup(s4)

        etf = self.etf
        key = self.key
        s3 = self.robot.get_seq()
        stk_batch = stock_trade_pb2.StockBatchOrderReq()
        stk_batch.policy_id = self.key
        qty = self.pi.pack.volume
        pl = base_pb2.B_5
        print('bbs %s %d pl %d' % (
            etf.etfcode, len(etf.etf_base_info.etf_list), pl))
        for mkid, etfstks in etf.stcks.items():
            print'mkid %d len(etfstks) %s' % (mkid, len(etfstks))
            if len(etfstks) < 1:
                continue
            stk_batch = stock_trade_pb2.StockBatchOrderReq()
            stk_batch.policy_id = key
            batgrp = BatchGroup(s4)
            for stk_info in etfstks:
                if len(stk_batch.order_list) < base_pb2.MAX_BATCH:
                    cash = self.batch_item_new(
                        stk_batch, stk_info, batgrp, qty, opr,
                        key, tid, pl)

                    totalcash += cash

                elif len(stk_batch.order_list) == base_pb2.MAX_BATCH:
                    snddata = basket.make_package_num(
                        base_pb2.CMD_BATCH_ORDER_REQ, s3, s4, stk_batch)
                    self.robot.riskmgt.send_package(snddata)
                    self.batchs[s4] = batgrp
                    print('\033[34mkey %s mkid %d s3 %d s4 0x%x pcklen'
                          '%d count %d \033[0m\n\t%s' %
                          (key, mkid, s3, s4, stk_batch.ByteSize(),
                           len(stk_batch.order_list), batgrp))
                    s4 += 1

                    batgrp = BatchGroup(s4)
                    stk_batch = stock_trade_pb2.StockBatchOrderReq()
                    stk_batch.policy_id = key
                    # cash = self.robot.batch_item_build(
                    #     stk_batch, stk_info, batgrp, pack, key,
                    #     tid, etf.etfcode)
                    cash = self.batch_item_new(
                        stk_batch, stk_info, batgrp, qty, opr,
                        key, tid, pl)
                    totalcash += cash
                else:
                    print('%s????????????????%s' % (RED, CLEAR))

            snddata = basket.make_package_num(base_pb2.CMD_BATCH_ORDER_REQ,
                                              s3, s4, stk_batch)
            self.robot.riskmgt.send_package(snddata)
            self.batchs[s4] = batgrp
            s4 += 1
            print('\033[34mkey %s mkid %d s3 %d s4 0x%x pcklen'
                  '%d count %d \033[0m\n\t%s' %
                  (key, mkid, s3, s4, stk_batch.ByteSize(),
                   len(stk_batch.order_list), batgrp))

        self.totalcash = totalcash

        if len(stk_batch.order_list) > 0:
            snddata = basket.make_package_num(
                base_pb2.CMD_BATCH_ORDER_REQ,
                s3, s4, stk_batch)
            self.robot.riskmgt.send_package(snddata)
            self.batchs[s4] = batgrp

        print('\033[34mkey %s mkid %d s3 %d s4 0x%x pcklen'
              '%d count %d \033[0m\n\t%s' %
              (key, mkid, s3, s4, stk_batch.ByteSize(),
               len(stk_batch.order_list), batgrp))

        print('\033[34mput %s in s3 %d 0x%x pcklen %d\033[0m\n' %
              (key, s3, s4, stk_batch.ByteSize()))  # self))

        # for gid, batgrp in self.batchs.items():
        #     print('gid %d' % (gid))
        #     for bi in batgrp.stklist:
        #         print('\tcode %s qty %d' % (bi.stkcode, bi.qty))

    # ------------------------------------------------------------------------
    def etf_buy_purchase(self, ):
        # message ETFBCOrRSPolicy
        # {
        #     required    PolicyBaseParam base_param             = 1;
        #     required    string     code                        = 2;
        #     required    uint32     volume                      = 3;
        #     required    int32      price_ratio                 = 4;
        #     required    uint32     delayed_single              = 5;
        #     required    uint32     delayed_max                 = 6;

        # buy stocks
        self.etf_basket(base_pb2.OPR_BUY, self.pi.pack.price_ratio)
        gevent.sleep(float(self.pi.pack.delayed_max) / 1000)

        # pruchase etf
        policyid = self.robot.get_policy_id_sub(self.key)
        self.etftran = TranETF(
            self.robot, self.key, self.pi, policyid,
            base_pb2.OPR_PURCHASE, self.etf.etfcode, self.etf)
        self.etftran.etf_purchase_redeem(
            self.pi.pack.volume, base_pb2.OPR_PURCHASE, policyid, self.etf)

        # just for debug
        gevent.sleep(0.5)

        pi = self.pi
        etf = self.etf
        policyid = self.robot.get_policy_id_sub(self.key)
        volume = pi.pack.volume * etf.etf_base_info.creation_redemption_unit  #
        self.robot.single_order2(
            self, policyid, self.pi.pack.code, volume,
            int(1.9 * 10000), base_pb2.OPR_SELL, 1)

    # --------------------------------------------------------------------
    def sub_knock_handle(self, pi, sknock):
        print('%s ETF::sub_knock(%s)%s' %
              (RED, sknock, CLEAR))
        for gid, batgrp in self.batchs.items():
            for bi in batgrp.stklist:
                # print 'bi.ordr %s skno %s' % (bi.order_no, sknock.order_no)
                if bi.order_no == sknock.order_no:
                    bi.remain_qty -= sknock.match_volume
                    self.robot.quo.update_knock_info(
                        sknock.stock_id,  sknock.market, sknock.bs_flag,
                        sknock.match_volume)
                    return

    def get_status(self, pi, sknock):
        if self.etftran.policyid == sknock.policy_id:
            status = self.etftran.get_status(pi, sknock)
        else:
            status = super(TranBuyPurchase, self).get_status(pi, sknock)
        return status

    def get_percentage(self, pi, sknock):
        return 80

    def get_start_time(self, pi, sknock):
        pass

    def get_end_time(self, pi, sknock):
        pass

    def get_b_s_amount(self, pi, sknock):
        pass

    def get_s_s_amount(self, pi, sknock):
        pass

    def get_b_f_amount(self, pi, sknock):
        pass

    def get_s_f_amount(self, pi, sknock):
        pass

    def get_match_volume(self, pi, sknock):
        pass

    def get_logic_type(self, pi, sknock):
        pass

    def get_trader_id(self, pi, sknock):
        pass

    def get_trader_ip(self, pi, sknock):
        pass

    def get_direction(self, pi, sknock):
        pass


# -----------------------------------------------------------------------------
class TranFastPurchase(TranBuyPurchase):
    """ basket buy sell withdrawal submit, auto """

    def __init__(self, robot, key, pi, etf, count, ):
        super(TranFastPurchase, self).__init__(
            robot, key, pi, etf.etfcode, count,
            base_pb2.OPR_BUY, base_pb2.OPR_BUY_PURCHASE)
        self.etf = etf
        self.phase = base_pb2.CMD_BATCH_ORDER_REQ
        self.opr = base_pb2.OPR_BUY_PURCHASE
        self.etftran = None

    def __str__(self):
        return ('TBP: %d btch: %d\n%s\n%s' %
                (len(self.task), len(self.batchs), self.task, self.batchs))

    # ------------------------------------------------------------------------
    def etf_fast_purchase(self):
        # message ETFBCOrRSPolicy
        # {
        #     required    PolicyBaseParam base_param             = 1;
        #     required    string     code                        = 2;
        #     required    uint32     volume                      = 3;
        #     required    int32      price_ratio                 = 4;
        #     required    uint32     delayed_single              = 5;
        #     required    uint32     delayed_max                 = 6;

        # buy stocks
        self.etf_basket(base_pb2.OPR_BUY, self.pi.pack.price_ratio)
        gevent.sleep(float(self.pi.pack.delayed_max) / 1000)

        # pruchase etf
        policyid = self.robot.get_policy_id_sub(self.key)
        self.etftran = TranETF(
            self.robot, self.key, self.pi, policyid,
            base_pb2.OPR_PURCHASE, self.etf.etfcode, self.etf)
        self.etftran.etf_purchase_redeem(
            self.pi.pack.volume, base_pb2.OPR_PURCHASE, policyid, self.etf)

        gevent.sleep(0.5)

        pi = self.pi
        etf = self.etf
        policyid = self.robot.get_policy_id_sub(self.key)
        volume = pi.pack.volume * etf.etf_base_info.creation_redemption_unit  #
        self.robot.single_order2(
            self, policyid, self.pi.pack.code, volume,
            int(1.9 * 10000), base_pb2.OPR_SELL, 1)

    # --------------------------------------------------------------------
    def sub_knock_handle(self, pi, sknock):
        print('%s ETFASTPUR::sub_knock(%s)%s' %
              (RED, sknock, CLEAR))
        if self.etftran is None:
            super(TranFastPurchase, self).sub_knock_handle(pi, sknock)
            # for gid, batgrp in self.batchs.items():
            #     for bi in batgrp.stklist:
            #     # print 'bi.ordr %s skno %s' % (bi.order_no, sknock.order_no)
            #         if bi.order_no == sknock.order_no:
            #             bi.remain_qty -= sknock.match_volume
            #             self.robot.quo.update_knock_info(
            #                 sknock.stock_id,  sknock.market, sknock.bs_flag,
            #                 sknock.match_volume)
            #             return
        else:
            if self.etftran.policyid == sknock.policy_id:
                self.etftran.knock_handle(pi, sknock)
            else:
                super(TranFastPurchase, self).sub_knock_handle(pi, sknock)
                # for gid, batgrp in self.batchs.items():
                #     for bi in batgrp.stklist:
                #     # print 'bi.ordr %s skno %s' % (bi.order_no,
                #           sknock.order_no)
                #         if bi.order_no == sknock.order_no:
                #             bi.remain_qty -= sknock.match_volume
                #             self.robot.quo.update_knock_info(
                #                 sknock.stock_id,  sknock.market,
                #                 sknock.bs_flag,
                #                 sknock.match_volume)
                #             return

    def get_status(self, pi, sknock):
        status = message.PLC_STS_BASKET_PROGRESSED
        if self.etftran.policyid == sknock.policy_id:
            if base_pb2.OPR_PURCHASE == sknock.order_bs_flag:
                if self.etftran.pr_remain_qty == 0:
                    status = message.PLC_STS_FINISHED
                else:
                    status = message.PLC_STS_ETF_PUR_PROGRESSED
            else:
                if self.etftran.bs_remain_qty == 0:
                    status = message.PLC_STS_FINISHED
                else:
                    status = message.PLC_STS_ETF_SEL_PROGRESSED
        else:
            status = super(TranFastPurchase, self).get_status(pi, sknock)
            return status


# -----------------------------------------------------------------------------
class TranFastRedeem(TranBuyPurchase):
    """ basket buy sell withdrawal submit, auto """
    def __init__(self, robot, key, pi, etf, count, ):
        super(TranFastRedeem, self).__init__(
            robot, key, pi, etf.etfcode, count,
            base_pb2.OPR_BUY, base_pb2.OPR_BUY_PURCHASE)
        self.etf = etf
        self.phase = base_pb2.CMD_BATCH_ORDER_REQ
        self.opr = base_pb2.OPR_FAST_REDEEM
        self.etftran = None

    # ------------------------------------------------------------------------
    def etf_fast_redeem(self):
        pi = self.pi
        policyid = self.robot.get_policy_id_sub(self.key)
        self.robot.single_order2(
            self, policyid, pi.pack.code, pi.pack.volume,
            pi.pack.price, base_pb2.OPR_BUY, self.etf.mkid)
        gevent.sleep(0.5)

        # redeem etf
        policyid = self.robot.get_policy_id_sub(self.key)
        self.etftran = TranETF(
            self.robot, self.key, pi, policyid,
            base_pb2.OPR_REDEEM, self.etf.etfcode, self.etf)
        self.etftran.etf_purchase_redeem(
            pi.pack.volume, base_pb2.OPR_REDEEM, policyid, self.etf)
        # self.etf_purchase_redeem(
        #     pi.pack.volume, base_pb2.OPR_REDEEM)

        # sell stocks
        gevent.sleep(float(pi.pack.delayed_max) / 1000)
        self.etf_basket(base_pb2.OPR_SELL, pi.pack.price_ratio)
        pass

    def get_status(self, pi, sknock):
        status = message.PLC_STS_BASKET_PROGRESSED
        if self.etftran.policyid == sknock.policy_id:
            if base_pb2.OPR_PURCHASE == sknock.order_bs_flag:
                if self.etftran.pr_remain_qty == 0:
                    status = message.PLC_STS_FINISHED
                else:
                    status = message.PLC_STS_ETF_RED_PROGRESSED
            else:
                if self.etftran.bs_remain_qty == 0:
                    status = message.PLC_STS_FINISHED
                else:
                    status = message.PLC_STS_ETF_BUY_PROGRESSED
        else:
            status = super(TranFastRedeem, self).get_status(pi, sknock)
            return status


# -----------------------------------------------------------------------------
class TranRedeemSell(TranBuyPurchase):
    """ basket buy sell withdrawal submit, auto """
    def __init__(self, robot, key, pi, etf, count, ):
        super(TranRedeemSell, self).__init__(
            robot, key, pi, etf.etfcode, count,
            base_pb2.OPR_BUY, base_pb2.OPR_BUY_PURCHASE)
        self.phase = base_pb2.CMD_BATCH_ORDER_REQ
        self.opr = base_pb2.OPR_REDEEM_SELL
        self.etftran = None

    # ------------------------------------------------------------------------
    def etf_redeem_sell(self, pi):
        # self.etf_purchase_redeem(pi.pack.volume, base_pb2.OPR_REDEEM)
        # redeem etf
        policyid = self.robot.get_policy_id_sub(self.key)
        self.etftran = TranETF(
            self.robot, self.key, pi, policyid,
            base_pb2.OPR_REDEEM, self.etf.etfcode, self.etf)
        self.etftran.etf_purchase_redeem(
            pi.pack.volume, base_pb2.OPR_REDEEM, policyid, self.etf)

        # sell stock
        gevent.sleep(float(pi.pack.delayed_max) / 1000)
        self.etf_basket(base_pb2.OPR_SELL, pi.pack.price_ratio)

    def get_status(self, pi, sknock):
        status = message.PLC_STS_BASKET_PROGRESSED
        if self.etftran.policyid == sknock.policy_id:
            if base_pb2.OPR_PURCHASE == sknock.order_bs_flag:
                if self.etftran.pr_remain_qty == 0:
                    status = message.PLC_STS_FINISHED
                else:
                    status = message.PLC_STS_ETF_RED_PROGRESSED
            else:
                if self.etftran.bs_remain_qty == 0:
                    status = message.PLC_STS_FINISHED
                else:
                    status = message.PLC_STS_ETF_BUY_PROGRESSED
        else:
            status = super(TranRedeemSell, self).get_status(pi, sknock)
            return status
