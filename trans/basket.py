#!/usr/bin/env python
# -*- coding: utf-8 -*-


import time
# import transactoin

from common import utils
import message

from dao.datatype import BatchGroup
from dao.datatype import BInfo

from pb import base_pb2
from pb import error_pb2
from pb import stock_trade_pb2
from pb import ot_pb2


RED = '\033[31m'
GREEN = '\033[32m'
BLUE = '\033[33m'
CLEAR = '\033[0m'


# -----------------------------------------------------------------------------
def make_package_num(cmd, s3, s4, pack):
    snddata = utils.make_package_num(
        base_pb2.SYS_STOCK, cmd, s3, s4, pack)
    return snddata


# -----------------------------------------------------------------------------
class TranBasket(object):
    """ basket buy sell withdrawal submit, auto """
    __slots__ = ('robot', 'key', 'count', 'pi', 'task', 'phase', 's3',
                 'totalcash', 'batchs', 'recv_grp', 'withdrawal', 'opr',
                 'etfcode', 'status_id')

    def __init__(self, robot, key, pi, etfcode, count, phase, opr):
        # super(TranBasket, self).__init__(robot, key, pi, count)
        self.robot = robot
        self.key = key
        self.pi = pi
        self.count = count
        self.phase = phase
        self.opr = opr
        self.batchs = {}
        self.recv_grp = 0
        self.phase = phase
        self.withdrawal = 0
        self.etfcode = etfcode
        self.task = []
        self.robot.set_transaction(key, self)
        self.status_id = 0

    def __str__(self):
        return ('task: %d btch: %d\n%s\n%s' %
                (len(self.task), len(self.batchs), self.task, self.batchs))

    def auto(self, timeout, timer_handler=None, data=None):
        # wait 1 second ,then withdrawal
        if timer_handler is not None:
            self.robot.timer_proc.add_task(timer_handler, timeout, data)
        else:
            self.robot.timer_proc.add_task(self.timer_auto, timeout, data)

    def basket_withdrawal(self, key):
        # 遍历批次号, 撤单
        bdrwl = stock_trade_pb2.StockBatchOrderCancelReq()
        for gid, batgrp in self.batchs:
            bdrwl.batch_no = batgrp.bno
            bdrwl.policy_id = key
            bdrwl.trader_id = self.pi.sess.tid
            self.robot.riskmgt.make_and_send(
                base_pb2.CMD_BATCH_WITHDRAWAL_REQ, self.pi.s3,
                gid, batgrp)
        self.phase = base_pb2.OPR_WITHDRAWS
        return error_pb2.SUCCESS

    def knock_handle(self, pi):
        pass

    def sub_knock_handle(self, pi, sknock):
        print('%s sub_knock_handle(self, sknock): %s%s' %
              (RED, sknock.order_no, CLEAR))
        for gid, batgrp in self.batchs.items():
            for bi in batgrp.stklist:
                print 'bi.order_no', bi.order_no
                if bi.order_no == sknock.order_no:
                    bi.remain_qty -= sknock.match_volume
                    self.robot.quo.update_knock_info(
                        sknock.stock_id,  sknock.market, sknock.bs_flag,
                        sknock.match_volume)
                    return

    def timer_auto(self, data):
        # data = policyid
        self.robot.basket_withdrawal(data, self)
        return False

    # -------------------------------------------------------------------------
    # def batch_item_bud(self, stkbtch, stkinf, btgrp, pack, key, tid, ecode):
    def batch_item_new(self, s_btch, stkinf, btgrp, qty, opr,
                       key, tid, pl):
        # TIMES = 10000
        # print 'self.etfcode %s ' % (self.etfcode)
        TIMES = 1
        s_order = s_btch.order_list.add()
        s_order.code = stkinf.stkcode
        s_order.market = stkinf.mkid                #
        s_order.price = int(stkinf.price(pl, opr) * TIMES)
        s_order.qty = stkinf.qty[self.etfcode] * qty              #
        s_order.bs_flag = opr
        s_order.trader_id = tid           #
        s_order.policy_id = self.robot.get_policy_id_sub(key)
        bi = BInfo(s_order.code, s_order.qty, s_order.policy_id, stkinf)
        btgrp.stklist.append(bi)
        cash = s_order.price * s_order.qty

        # print 'stkcode %s %d [%d] (%f)' % \
        #       (s_order.code, s_order.qty, s_order.price,
        #        s_order.price / TIMES)

        return cash

    # -------------------------------------------------------------------------
    def basket_buy_sell(self, s3, s4, etf, key, opr):
        pi = self.pi
        pack = pi.pack
        pl = pack.price_level
        print('buy_sell seq_opr pl %s %r key %s opr 0x%x'
              % (pl, etf, key, opr))

        totalcash = 0

        s3 = self.robot.get_seq()
        tid = pi.sess.tid
        print('bbs %s %d' % (etf.etfcode, len(etf.etf_base_info.etf_list)))
        for mkid, etfstks in etf.stcks.items():
            if len(etfstks) < 1:
                continue
            stk_batch = stock_trade_pb2.StockBatchOrderReq()
            stk_batch.policy_id = key
            batgrp = BatchGroup(s4)
            for stk_info in etfstks:
                if len(stk_batch.order_list) < base_pb2.MAX_BATCH:
                    cash = self.batch_item_new(
                        stk_batch, stk_info, batgrp, pack.volume, opr,
                        key, tid, pl)

                    totalcash += cash

                elif len(stk_batch.order_list) == base_pb2.MAX_BATCH:
                    snddata = make_package_num(
                        base_pb2.CMD_BATCH_ORDER_REQ, s3, s4, stk_batch)
                    self.robot.riskmgt.send_package(snddata)
                    self.batchs[s4] = batgrp
                    print('\033[34mkey %s mkid %d s3 %d s4 0x%x pcklen'
                          '%d count %d \033[0m\n\t%s\npacklen %d' %
                          (key, mkid, s3, s4, stk_batch.ByteSize(),
                           len(stk_batch.order_list), '----',  # batgrp,
                           len(snddata)))
                    s4 += 1

                    batgrp = BatchGroup(s4)
                    stk_batch = stock_trade_pb2.StockBatchOrderReq()
                    stk_batch.policy_id = key
                    # cash = self.robot.batch_item_build(
                    #     stk_batch, stk_info, batgrp, pack, key,
                    #     tid, etf.etfcode)
                    cash = self.batch_item_new(
                        stk_batch, stk_info, batgrp, pack.volume, opr,
                        key, tid, pl)
                    totalcash += cash
                else:
                    print('%s????????????????%s' % (RED, CLEAR))

            # snddata = make_package_num(base_pb2.CMD_BATCH_ORDER_REQ,
            #                            s3, s4, stk_batch)
            # self.robot.riskmgt.send_package(snddata)
            if len(stk_batch.order_list) > 0:
                self.robot.riskmgt.make_and_send(base_pb2.CMD_BATCH_ORDER_REQ,
                                                 s3, s4, stk_batch)
                self.batchs[s4] = batgrp
                s4 += 1
                print('\033[34mkey %s mkid %d s3 %d s4 0x%x pcklen'
                      '%d count %d \033[0m\n\t%s' %
                      (key, mkid, s3, s4, stk_batch.ByteSize(),
                       len(stk_batch.order_list), batgrp))

        self.totalcash = totalcash

        if len(stk_batch.order_list) > 0:
            snddata = make_package_num(
                base_pb2.CMD_BATCH_ORDER_REQ,
                s3, s4, stk_batch)
            self.robot.riskmgt.send_package(snddata)
            self.batchs[s4] = batgrp

        print('\033[34mkey %s mkid %d s3 %d s4 0x%x pcklen'
              '%d count %d \033[0m\n\t%s' %
              (key, mkid, s3, s4, stk_batch.ByteSize(),
               len(stk_batch.order_list), batgrp))

        print('\033[34mput %s in s3 %d 0x%x pcklen %d\033[0m\n' %
              (key, s3, s4, stk_batch.ByteSize()))  # seq_opr))

        # for gid, batgrp in seq_opr.batchs.items():
        #     print('gid %d' % (gid))
        #     for bi in batgrp.stklist:
        #         print('\tcode %s qty %d' % (bi.stkcode, bi.qty))

    # ------------------------------------------------------------------------
    def basket_auto(self, pi, s3, etf, seq_opr):
        policyid = pi.pack.policy_id
        ret, seq_opr = self.check_transaction(policyid, pi)
        if error_pb2.SUCCESS != ret:
            return ret

        # 1. withdrawal
        # 2. waiting withdrawal resp
        # 3. set timer  todo 本次不实现
        # 4. basket submit
        # 5. wait 1 second go 1.
        self.robot.basket_withdrawal(policyid, seq_opr)

    # ------------------------------------------------------------------------
    def basket_submit(self, pi, s3, seq_opr):
        """ 补单
        """
        # single_order_req
        print pi.pack
        # etf  EtfBasketInfo
        # 如果存在 policy_id 用policy_id 对应报单的 qty
        key = pi.pack.policy_id
        seq_opr = self.seqclnts.get(key, None)
        if seq_opr is None:
            bp_resp = ot_pb2.BasketPolicyResp()
            bp_resp.policy_id = pi.pack.policy_id
            bp_resp.ret_code = error_pb2.ERROR_NOT_EXIST
            snddata = utils.make_package(
                base_pb2.SYS_ROBOT, base_pb2.CMD_BASKET_ORDER_RESP, pi,
                bp_resp)
            pi.sess.send_package(snddata)
            return error_pb2.SUCCESS

        if seq_opr.phase != base_pb2.OPR_WITHDRAWS:
            bp_resp = ot_pb2.BasketPolicyResp()
            bp_resp.policy_id = pi.pack.policy_id
            bp_resp.ret_code = error_pb2.ERROR_NO_WITHDRAWAL
            snddata = utils.make_package(
                base_pb2.SYS_ROBOT, base_pb2.CMD_BASKET_ORDER_RESP, seq_opr.pi,
                bp_resp)
            self.try_send(seq_opr.pi.sock, snddata)
            return error_pb2.SUCCESS

        seq_opr.status = base_pb2.OPR_BASEKET_SUBMIT
        # new price level

        s4 = 0
        for gid, batgrp in seq_opr.batchs.items():
            stk_batch = stock_trade_pb2.StockBatchOrderReq()
            stk_batch.policy_id = key
            for binfo in batgrp.stklst:
                s_order = stk_batch.order_list.add()
                s_order.code = binfo.stkcode
                s_order.market = binfo.stk_info.mkid                #
                s_order.price = int(binfo.stk_info.price[pi.pack.pl] * 10000)
                s_order.qty = binfo.remain_qty              #
                s_order.bs_flag = seq_opr.opr
                s_order.trader_id = seq_opr.pi.sess.tid           #
                s_order.policy_id = self.get_policy_id_sub(key)

            snddata = make_package_num(
                base_pb2.CMD_BATCH_ORDER_REQ, s3, s4, stk_batch)
            self.riskmgt.send_package(snddata)
            s4 += 1

        return error_pb2.SUCCESS

    def get_status(self, pi, sknock):
        status = message.PLC_STS_BASKET_PROGRESSED
        return status

    def get_percentage(self, pi, sknock):
        return 50

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

    def policy_status(self, pi, sknock):
        self.status_id += 1

        ps = ot_pb2.PolicyStatus()
        ps.policy_id = sknock.policy_id
        ps.time_stamp = int(time.time())
        err = ot_pb2.Error()
        err.code = error_pb2.SUCCESS
        ps.err.code = error_pb2.SUCCESS
        ps.status = self.get_status()
        ps.status_id = self.status_id
        ps.robot_ip = self.robot.rip
        ps.percentage = self.get_percentage()

        # print'etf policy_status remain_qty %d volume %d ps\n%s' % (
        #     self.remain_qty, self.volume, ps)

        snddata = utils.make_package(
            base_pb2.SYS_MTC,
            base_pb2.CMD_POLICY_STATUS, pi, ps)
        return snddata


# -----------------------------------------------------------------------------
class TranBasketComplete(object):
    # ------------------------------------------------------------------------
    def basket_complete(self, pi, s3, etf):
        """ 补齐
        # 查询当前股票可申购数量, 根据篮子数量  stkinfo.qty 计算缺口数量
        # 根据缺口批量下单
        """
        # etf.count += 1
        # key, policyid = self.get_policy_id(pi.pack.opr, pi.pack.code)
        # seq_opr = TranBasketComplete(self, key, pi, etf.count,
        #                              pi.pack.opr, pi.pack.opr)

        # etf_code = pi.pack.code
        # etf = self.pre_quo.etfs[etf_code]
        # s3 = self.get_seq()

        self.phase = base_pb2.CMD_QUERY_FUTURE_POSITION_REQ
        # new price level
        self.pi.pack.pl = pi.pack.pl
        # new qty
        # 查询持仓
        self.robot.set_stock_query(s3, 0, self)
        self.robot.stock_sock.query_position(s3, 0, self)

    # -------------------------------------------------------------------------
    def basket_next(self,  seq_opr, pi):
        seq_opr.knock_handle(pi)

    # -------------------------------------------------------------------------
    def batch_order_complete(self, seq_opr, pi, buys, mkid):
        totalcash = 0
        tid = seq_opr.pi.sess.tid
        count = seq_opr.count << 8
        s4 = count + 1
        s3 = self.robot.get_seq()
        pack = seq_opr.pi.pack
        opr = base_pb2.OPR_BUY
        batgrp = BatchGroup(s4)
        stk_batch = stock_trade_pb2.StockBatchOrderReq()
        for code, stkqty in buys.items():
            stk_info = stkqty[0]
            volume = stkqty[1]
            if len(stk_batch.order_list) < base_pb2.MAX_BATCH:
                cash = self.batch_item_new(
                    stk_batch, stk_info, batgrp, volume,
                    opr, seq_opr.key, tid, pack.pl)
                totalcash += cash

            elif len(stk_batch.order_list) == base_pb2.MAX_BATCH:
                snddata = make_package_num(
                    base_pb2.CMD_BATCH_ORDER_REQ, s3, s4, stk_batch)
                self.robot.riskmgt.send_package(snddata)
                seq_opr.batchs[s4] = batgrp
                print('\033[34mkey %s mkid %d s3 %d s4 0x%x pcklen'
                      '%d\033[0m\n' %
                      (seq_opr.key, mkid, s3, s4, stk_batch.ByteSize()))
                s4 += 1

                batgrp = BatchGroup(s4)
                stk_batch = stock_trade_pb2.StockBatchOrderReq()
                stk_batch.policy_id = seq_opr.key
                cash = self.batch_item_new(
                    stk_batch, stk_info, batgrp, volume,
                    opr, seq_opr.key, tid, pack.pl)
                totalcash += cash

        seq_opr.totalcash = totalcash

        seq_opr.batchs[s4] = batgrp
        snddata = make_package_num(
            base_pb2.CMD_BATCH_ORDER_REQ, pi.s3, s4, stk_batch)
        self.robot.riskmgt.send_package(snddata)

    # ---------------------------------------------------------------------
    def calc_buy(self, key, pi):
        qty = self.pi.pack.qty
        etfcode = self.pi.pack.code
        etf = self.robot.pre_quo.etfs.get(etfcode, None)
        if etf is None:
            return error_pb2.ERROR_NOT_EXIST

        stckposs = {}
        # stock position list -> dict
        for stk in pi.pack.stock_position:
            stckposs[stk.stock_id] = stk.stock_can_purchase_volume

        buys = {}
        # 遍历清单,在清单中计算股票的需要申购数
        print('calc buy %s %s' % (etf, type(etf)))
        print(type(etf))

        for mkid, stocks in etf.stcks.items():
            buys[mkid] = {}
            for stk in stocks:
                stck_pos = stckposs.get(stk.stk_code, 0)
                if stk.qty[etf.etfcode] * qty > stck_pos:
                    buys[mkid][stk.stkcode] = [
                        stk,
                        stk.qty[etf.etfcode] * qty - stck_pos]

        self.count += 1
        for mkid, blist in buys.items():
            self.batch_order_complete(self, pi, blist, mkid, key)

# # -------------------------------------------------------------------------
# if __name__ == '__main__':
#     main()

