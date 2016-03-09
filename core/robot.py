#!/usr/bin/env python
# -*- coding: utf-8 -*-


""" global data
申赎只支持510050、159901

"""


import struct
import time
import gevent
from gevent.server import StreamServer
import yaml

from common import utils

# import riskmgt
# import pre_quotation
# import quotation
# import stock_conn

from dao.datatype import BInfo, package_info, Sesstion, BatchGroup
from trans.transaction import TransactionSingle, SeqOperation
from trans.basket import TranBasket, TranBasketComplete
from trans.etftrans import TranETF, TranBuyPurchase, TranFastPurchase
from trans.etftrans import TranRedeemSell, TranFastRedeem

from pb import base_pb2
from pb import error_pb2
from pb import ot_pb2
from pb import stock_trade_pb2
from pb import trade_db_model_pb2


__author__ = 'qinjing'

RED = '\033[31m'
GREEN = '\033[32m'
BLUE = '\033[33m'
CLEAR = '\033[0m'

VERSION = base_pb2.MAJOR << 16 or base_pb2.MINOR

ROBOT_VER = '0.0.1a'


# -----------------------------------------------------------------------------
def make_package_num(cmd, s3, s4, pack):
    snddata = utils.make_package_num(
        base_pb2.SYS_STOCK, cmd, s3, s4, pack)
    return snddata


# -----------------------------------------------------------------------------
class RobotApp(object):
    '''
    this is a robot
    '''
    # map robotapp.seq <==> (client, req_seq)

    cfg = None  # config
    quo = None  # quotation stock server
    q_f_sock = None  # quotation future server
    pre_quo = None  # quotation pre stock server
    q_p_f_sock = None  # quotation pre future server
    svr = None  # locale listen server
    riskmgt = None  # riskmgt.RiskMgt(self)  # connection of riskmgt
    stock_sock = None  # connection of stock server
    future_sock = None  # connection of future server
    seq = 0  # send package seq
    seqclnts = {}  # dict of SeqOperation key == self.seq
    # etfs = {}    # dict of EtfInfo key == etf_code
    # stocks = {}  # dict of StockInfo key == stock_code
    clients = {}  # dict of client sessions
    sessions = {}
    stock_query = {}
    running = 1

    def __init__(self, conf):
        with open(conf) as f:
            self.cfg = yaml.load(f)

        self.rid = self.cfg['robotid']
        rip = self.cfg['robot_listen']['rip']
        rport = self.cfg['robot_listen']['rport']
        self.svr = StreamServer((rip, rport), self.new_session)
        self.code_count = {}
        self.rip = rip

    def get_seq(self):
        self.seq += 1
        # print 'self.seq %d' % self.seq
        return self.seq

    def get_policy_id(self, opr, code):
        count = self.code_count.get(code, 0)
        tm = '%.06f' % time.time()
        pidm = '%s%s%04d%02d%s' % (self.rid, code, count, opr,
                                   tm[-12:-7])
        pid = '%s:%s%s' % (pidm, tm[-12:-7], tm[-6:])
        count += 1
        self.code_count[code] = count

        return pidm.encode('ascii'), pid.encode('ascii')

    def get_policy_id_sub(self, key):
        tm = '%.06f' % time.time()
        pid = '%s:%s%s' % (key, tm[-12:-7], tm[-6:])

        return pid.encode('ascii')

    def policy2key(self, policyid):
        key = policyid[:23]
        return key

    def print_seqs(self):
        print('seqs >>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        for k, v in self.seqclnts.items():
            print k, v
        print('seqs <<<<<<<<<<<<<<<<<<<<<<<<<<<<')

    def seqclnt_put(self, k, sc):
        self.seqclnts[k] = sc

    def get_groupid(self, etf_code):
        return '%s%d' % (etf_code, 1234567)

    def get_stock_query(self, key):
        seq_opr = self.stock_query.get(key, None)
        return seq_opr

    def get_transaction(self, key):
        seq_opr = self.seqclnts.get(str(key), None)
        return seq_opr

    def set_stock_query(self, s3, s4, value):

        self.stock_query[s3] = value
        print('set sq key %s v %s' % (s3, value))

    def set_transaction(self, key, trans):
        self.seqclnts[key] = trans
        return trans

    def notify_sessions(self, pi):
        snddata = utils.make_package(base_pb2.SYS_ROBOT, pi.cmd, pi, pi.pack)
        for (tid, sess) in self.sessions.items():
            # print tid, sess
            sess.send_package(snddata)

    def notify_policy_status(self, snddata):
        for (tid, sess) in self.sessions.items():
            # print tid, sess
            sess.send_package(snddata)

    # -------------------------------------------------------------------------
    def single_withdrawal_handle(self, pi):
        policyid = pi.pack.policy_id
        key = self.policy2key(policyid)
        seq_opr = self.get_transaction(key)
        print('single_withdrawal', policyid)
        if seq_opr is None:
            # cannot find pre seq_opr
            # withdrawal to riskmgt
            print('nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn %s' % (policyid))
            print(self.seqclnts)
            print('%ssw pack %s pid %s tran: \n%s' % (RED, pi.pack,
                  pi.pack.policy_id, CLEAR))
            print('nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn')
            seq_opr = SeqOperation(self, key, pi, 9900)
            seq_opr.s3 = self.get_seq()
            # self.riskmgt.make_and_send(
            #     base_pb2.CMD_SINGLE_WITHDRAWAL_REQ, s3,
            #     base_pb2.CMD_SINGLE_WITHDRAWAL_REQ, pi.pack)

            # response client
            wthdrw_resp = stock_trade_pb2.SingleOrderResp()
            wthdrw_resp.ret_code = error_pb2.ERROR_NOT_EXIST
            snddata = utils.make_package(
                base_pb2.SYS_ROBOT, base_pb2.CMD_SINGLE_WITHDRAWAL_RESP,
                pi, wthdrw_resp)
            self.try_send(pi.sock, snddata)

        # find pre seq_opr
        pi.pack.policy_id = self.get_policy_id_sub(key)
        seq_opr.task.append((pi.pack.policy_id,
                            base_pb2.CMD_SINGLE_WITHDRAWAL_REQ))
        print('%ssw s3 %s pid %s tran: \n%s%s' % (RED, seq_opr.pi.s3,
              pi.pack.policy_id, seq_opr, CLEAR))
        self.riskmgt.make_and_send(
            base_pb2.CMD_SINGLE_WITHDRAWAL_REQ, seq_opr.s3,
            base_pb2.CMD_SINGLE_WITHDRAWAL_REQ, pi.pack)
        return error_pb2.SUCCESS

    # -------------------------------------------------------------------------
    def single_withdrawal_resp_handle(self, pi):
        """ single order withdrawal stock, etf : buy, sell
        """
        pack = pi.pack
        key = self.policy2key(pi.pack.policy_id)
        print('\033[31m''pi.pack.policy_id %s''\033[0m' % (pi.pack.policy_id))
        seq_opr = self.get_transaction(key)
        if error_pb2.SUCCESS == pack.ret_code:
            print('SWSP SUCCESS')
        else:
            print('%sSWSP err %s%s' % (RED, pi.pack.ret_message.encode('utf8'),
                  CLEAR))

        if seq_opr is None:
            print('xxxxxxxxxxxxpi %s seq_opr %s' % (pi, seq_opr))
            print('%sSWSP\nkey %s \nlen(trans) %d\n %s%s' % (RED,
                  pi.pack.policy_id, len(self.seqclnts), self.seqclnts, CLEAR))
            snddata = utils.make_package(
                base_pb2.SYS_MTC, base_pb2.CMD_SINGLE_WITHDRAWAL_RESP, pi,
                pack)
        else:
            snddata = utils.make_package(
                base_pb2.SYS_MTC, base_pb2.CMD_SINGLE_WITHDRAWAL_RESP,
                seq_opr.pi, pack)
            self.try_send(seq_opr.pi.sock, snddata)

        self.notify_sessions(pi)

        return error_pb2.SUCCESS

    # -------------------------------------------------------------------------
    def basket_complete(self, pi, s3, etf):
        """ 补齐
        # 查询当前股票可申购数量, 根据篮子数量  stkinfo.qty 计算缺口数量
        # 根据缺口批量下单
        """
        etf.count += 1
        key, policyid = self.get_policy_id(pi.pack.opr, pi.pack.code)
        seq_opr = TranBasketComplete(self, key, pi, etf.count,
                                     pi.pack.opr, pi.pack.opr)
        seq_opr.basket_complete()

    # -------------------------------------------------------------------------
    def basket_req_handle(self, pi):
        # message StockBasketPolicy
        # {
        #     required    PolicyBaseParam base_param             = 1; //基本参数
        #     optional    string     code                        = 2; //ETF代码（统一填二级市场代码）
        #     required    uint32     volume                      = 3; //篮子数
        #     required    uint32     price_level                 = 4; //价格档位
        #     repeated    CustomBasketItem custom_items          = 5; //自定义篮子列表。当code不设置的时候，使用该参数。
        #     required    bool       expert_mode                 = 6; //专家模式。专门为篮子买卖界面设计，开启后支持替代补足、未完成篮子明细相关处理。
        # }
        # print '<<<<<<<<<<<<<<<<<<<<<<<<'
        print pi
        if pi.pack.code is not None:
            print '[%s]' % (pi.pack.code)
        # print '>>>>>>>>>>>>>>>>>>>>>>>>>'
        pack = pi.pack
        if pack.HasField('code'):
            etf_code = pack.code
            etf = self.pre_quo.get_etf(etf_code)
            if etf is None:
                print('None ETF %s\n%s' % (etf_code, len(self.pre_quo.etfs)))
                bskresp = ot_pb2.BasketPolicyResp()
                bskresp.ret_code = error_pb2.ERROR_NOT_EXIST
                snddata = utils.make_package(
                    base_pb2.SYS_ROBOT, base_pb2.CMD_BASKET_ORDER_RESP, pi,
                    bskresp)
                self.try_send(pi.sock, snddata)
                return error_pb2.SUCCESS

            s3 = self.get_seq()
            opr = base_pb2.OPR_SELL
            if base_pb2.POLICY_DIRECTION_POSITIVE == pi.pack.base_param.direction:
                opr = base_pb2.OPR_BUY
                etf.count += 1
                key, policyid = self.get_policy_id(opr, pi.pack.code)
                seq_opr = TranBasket(self, key, pi, etf_code,
                                     etf.count, opr, opr)
                # print('basket seq_opr %r' % seq_opr)
                seq_opr.basket_buy_sell(s3, 0, etf, key, opr)
            # elif base_pb2.OPR_BASEKET_SUBMIT == pack.opr:
            #     etf.count += 1
            #     # seq_opr = self.seqclnts.get(pi.pack.policy_id, None)
            #     self.basket_submit(pi, s3)
            # elif base_pb2.OPR_BASEKET_COMPLETE == pack.opr:
            #     self.basket_complete(pi, s3, etf)
            # elif base_pb2.OPR_BASEKET_AUTO == pack.opr:
            #     self.basket_auto(pi, s3, etf, seq_opr)
            # else:
            #     print('basket unknow operation 0x%x' % pi.cmd)
        else:
            pass
            # custom basket

        return error_pb2.SUCCESS

    # # -------------------------------------------------------------------------
    # def basket_withdrawal_req_handle(self, pi):
    #     policyid = pi.pack.policy_id
    #     seq_opr = self.get_transaction(policyid)
    #     if seq_opr is None:
    #         wthdrw_resp = ot_pb2.BasketWithdrawalResp()
    #         wthdrw_resp.ret_code = error_pb2.ERROR_NOT_EXIST
    #         snddata = utils.make_package(
    #             base_pb2.SYS_ROBOT, base_pb2.CMD_BASKET_WITHDRAWAL_RESP,
    #             pi, wthdrw_resp)

    #         self.try_send(pi.sock, snddata)
    #         return error_pb2.SUCCESS

    #     self.basket_withdrawal(policyid, seq_opr)

    # -------------------------------------------------------------------------
    def batch_item_build(self, stkbtch, stkinf, btgrp, pack, key, tid, ecode):
        s_order = stkbtch.order_list.add()
        s_order.code = stkinf.stkcode
        s_order.market = stkinf.mkid                #
        s_order.price = int(stkinf.price(pack.pl, pack.opr) * 10000)
        s_order.qty = stkinf.qty[ecode] * pack.qty              #
        s_order.bs_flag = pack.opr
        s_order.trader_id = tid           #
        s_order.policy_id = self.get_policy_id_sub(key)
        bi = BInfo(s_order.code, s_order.qty, s_order.policy_id, stkinf)
        btgrp.stklist.append(bi)
        cash = s_order.price * s_order.qty
        return cash

    # -------------------------------------------------------------------------
    def batch_item_new(self, s_btch, stkinf, btgrp, qty, opr, key, tid, pl):
        s_order = s_btch.order_list.add()
        s_order.code = stkinf.stkcode
        s_order.market = stkinf.mkid                #
        s_order.price = int(stkinf.price(pl, opr) * 10000)
        s_order.qty = qty              #
        s_order.bs_flag = opr
        s_order.trader_id = tid           #
        s_order.policy_id = self.get_policy_id_sub(key)
        bi = BInfo(s_order.code, s_order.qty, s_order.policy_id, stkinf)
        btgrp.stklist.append(bi)
        cash = s_order.price * s_order.qty
        return cash

    # ------------------------------------------------------------------------
    def batch_order_resp(self, pi):
        policyid = pi.pack.policy_id
        seq_opr = self.get_transaction(policyid)
        print('bor key %s s3 %d s4 0x%x \npi: =='
              % (policyid, pi.s3, pi.s4))
        if pi.pack.HasField('ret_message'):
            print('ret mssge %d %d %s' %
                  (pi.s3, pi.s4, pi.pack.ret_message.encode('utf8')))
        else:
            print 'no ret message'
        if seq_opr is None:
            print '----------------------------------'
            return error_pb2.SUCCESS

        seq_opr.recv_grp += 1
        seq_opr.phase = base_pb2.CMD_BATCH_ORDER_RESP
        batch = seq_opr.batchs.get(pi.s4, None)
        if batch is None:
            print('batch is None')
            return error_pb2.SUCCESS

        batch.bno = pi.pack.batch_no
        i = 0
        print 'hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh %s' % type('aaa')
        for single in pi.pack.order_resp_list:
            batch.stklist[i].order_no = single.order_no
            print ('pid %s rno %s p_id[%s] mess %s' % (
                batch.stklist[i].policyid, single.order_no.encode('utf8'),
                single.policy_id,
                single.ret_message.encode('utf8')))

            if single.HasField('policy_id'):
                # assert batch.stklist[i].policyid == single.policy_id
                print ('pid %s pid %s[%s]' %
                       (batch.stklist[i].policyid, single.policy_id,
                        single.ret_message.encode('utf8')))
            i += 1

        # bp_resp = ot_pb2.BasketPolicyResp()
        # bp_resp.ret_code = error_pb2.SUCCESS
        # bp_resp.policy_id = policyid
        # bp_resp.rate = seq_opr.recv_grp
        # bp_resp.ksh_count = len(seq_opr.batchs)
        # bp_resp.yg_cost = 0
        # snddata = utils.make_package(
        #     base_pb2.SYS_ROBOT, base_pb2.CMD_BASKET_ORDER_RESP, seq_opr.pi,
        #     bp_resp)

        # self.try_send(seq_opr.pi.sock, snddata)

        # print 'batch_order_resp'
        # print self.seqclnts

        return error_pb2.SUCCESS

    # ---------------------------------------------------------------
    def batch_withdrawal_handle(self, pi):
        key = pi.pack.policy_id
        seq_opr = self.get_transaction(key)
        if seq_opr is None:
            return error_pb2.SUCCESS

        seq_opr.withdrawal += 1
        batgrp = seq_opr.batchs.get(pi.s4)
        if batgrp is None:
            print('bt wthdrl error')
            return error_pb2.SUCCESS

        batgrp.bg_phase = base_pb2.CMD_BATCH_WITHDRAWAL_RESP
        # maybe batchs == withdrawal     with with with with???
        if len(seq_opr.batchs) == seq_opr.withdrawal:
            bwresp = ot_pb2.BasketWithdrawalResp()
            bwresp.ret_code = error_pb2.SUCCESS
            bwresp.policy_id = key
            snddata = utils.make_package(
                base_pb2.SYS_ROBOT, base_pb2.CMD_BASKET_WITHDRAWAL_RESP,
                seq_opr.pi, bwresp)
            seq_opr.pi.sess.send_package(snddata)
            # return error_pb2.SUCCESS

            if ((base_pb2.OPR_BASEKET_AUTO == seq_opr.opr and
                 base_pb2.OPR_WITHDRAWS == seq_opr.phase)):
                self.basket_submit()
                seq_opr.auto(1, data=key)

        return error_pb2.SUCCESS

    # ------------------------------------------------------------------------
    def check_transaction(self, key, pi):
        seq_opr = self.get_transaction(key)
        if seq_opr is None:
            wthdrw_resp = ot_pb2.BasketWithdrawalResp()
            wthdrw_resp.ret_code = error_pb2.ERROR_NOT_EXIST
            snddata = utils.make_package(
                base_pb2.SYS_ROBOT, base_pb2.CMD_BASKET_WITHDRAWAL_RESP,
                pi, wthdrw_resp)

            pi.sess.send_package(snddata)
            return error_pb2.ERROR_NOT_EXIST, None

        return error_pb2.SUCCESS, seq_opr

    # ------------------------------------------------------------------------
    def client_package_handle(self, cmd, s1, s2, s3, s4, body, sess):
        print('client 0x%x' % (cmd))
        status = error_pb2.SUCCESS
        # 创建单笔现货报单策略
        if base_pb2.CMD_STOCK_POLICY == cmd:
            print('\033[31mCMD_STOCK_POLICY\033[0m')
            # message StockPolicy
            pack = ot_pb2.StockPolicy()
            pack.ParseFromString(body)
            pi = package_info(cmd, s1, s2, s3, s4, pack, sess)
            status = self.single_order_handle(pi)
            pass
        # 创建单笔期货报单策略
        # elif base_pb2.CMD_FUTURE_POLICY == cmd:
        #     pass
        # 创建篮子买卖策略
        elif base_pb2.CMD_STOCK_BASKET_POLICY == cmd:
            pack = ot_pb2.StockBasketPolicy()
            pack.ParseFromString(body)
            pi = package_info(cmd, s1, s2, s3, s4, pack, sess)
            status = self.basket_req_handle(pi)
            pass
        # 创建股票申赎策略
        elif base_pb2.CMD_STOCK_CREATE_OR_REDEEM_POLICY == cmd:
            print('\033[31mCMD_STOCK_CREATE_OR_REDEEM_POLICY\033[0m')
            pack = ot_pb2.StockCreateOrRedeemPolicy()
            pack.ParseFromString(body)
            pi = package_info(cmd, s1, s2, s3, s4, pack, sess)
            status = self.etf_purchase_redeem_req_handle(pi)
            pass
        elif base_pb2.CMD_ETF_BS_OR_RS_POLICY == cmd:
            pack = ot_pb2.ETFBCOrRSPolicy()
            pack.ParseFromString(body)
            pi = package_info(cmd, s1, s2, s3, s4, pack, sess)
            status = self.etf_buy_purchase_redeem_sell_req_handle(pi)
        # 篮子撤单??
        elif base_pb2.CMD_PAUSE_POLICY == cmd:
            pack = ot_pb2.PausePolicy()
            pack.ParseFromString(body)
            pi = package_info(cmd, s1, s2, s3, s4, pack, sess)
            status = self.pause_policy_req_handle(pi)
            pass
        elif base_pb2.CMD_SUBSCRIBE_POLICY_REQ == cmd:
            print('\033[31mcmd_suscribe_policy_req\033[0m')

            pass

        # --------------------------------------------------
        # old message define
        elif base_pb2.CMD_SINGLE_ORDER_REQ == cmd:
            print('\033[31mCMD_SINGLE_ORDER_REQ\033[0m')
            sngl_order = stock_trade_pb2.SingleOrderReq()
            sngl_order.ParseFromString(body)
            pi = package_info(cmd, s1, s2, s3, s4, sngl_order, sess)
            status = self.single_order_handle(pi)
        elif base_pb2.CMD_ETF_ORDER_REQ == cmd:
            # print('\033[31mCMD_SINGLE_ORDER_REQ\033[0m')
            sngl_order = stock_trade_pb2.SingleOrderReq()
            sngl_order.ParseFromString(body)
            pi = package_info(cmd, s1, s2, s3, s4, sngl_order, sess)
            status = self.etf_order_handle(pi)
        elif base_pb2.CMD_SINGLE_WITHDRAWAL_REQ == cmd:
            # print('\033[31mCMD_SINGLE_WITHDRAWAL_REQ\033[0m')
            s_withdrawal = stock_trade_pb2.SingleCancelReq()
            s_withdrawal .ParseFromString(body)
            pi = package_info(cmd, s1, s2, s3, s4, s_withdrawal, sess)
            status = self.single_withdrawal_handle(pi)

        elif base_pb2.CMD_BASKET_ORDER_REQ == cmd:
            print('\033[31mCMD_BASKET_ORDER_REQ\033[0m')
            basket = ot_pb2.BasketPolicyReq()
            basket.ParseFromString(body)
            pi = package_info(cmd, s1, s2, s3, s4, basket, sess)
            status = self.basket_req_handle(pi)
        elif base_pb2.CMD_BASKET_WITHDRAWAL_REQ == cmd:
            pack = ot_pb2.BasketWithdrawalReq()
            pack.ParseFromString(body)
            pi = package_info(cmd, s1, s2, s3, s4, pack, sess)
            status = self.basket_withdrawal_req_handle(pi)

        # etf operation
        elif base_pb2.CMD_ETF_CREATE_OR_REDEEM_POLICY == cmd:
            pack = ot_pb2.ETFCreateOrRedeemPolicy()
            pack.ParseFromString(body)
            pi = package_info(cmd, s1, s2, s3, s4, pack, sess)
            status = self.etf_purchase_redeem_req_handle(pi)
        elif base_pb2.CMD_ETF_QUICK_POLICY == cmd:
            pack = ot_pb2.ETFQuickPolicy()
            pack.ParseFromString(body)
            pi = package_info(cmd, s1, s2, s3, s4, pack, sess)
            status = self.etf_fast_req_handle(pi)

        elif base_pb2.CMD_FUND_ORDER_REQ == cmd:
            # print('\033[31mCMD_FUND_ORDER_REQ\033[0m')
            fund_req = stock_trade_pb2.SingleOrderReq()
            fund_req.ParseFromString(body)
            pi = package_info(cmd, s1, s2, s3, s4, fund_req, sess)
            status = self.fund_req_handle(pi)
        elif base_pb2.CMD_GRADED_FUND_REQ == cmd:
            pack = ot_pb2.GradingFundReq()
            pack.ParseFromString(body)
            pi = package_info(cmd, s1, s2, s3, s4, pack, sess)
            status = self.graded_fund_req_handle(pi)
        else:
            print('unknow cmd %x' % cmd)
            return error_pb2.ERROR_RELOGIN
        return status

    # ------------------------------------------------------------------------
    def etf_bp_rs_next(self, seq_opr, pi, sknock):
        seq_opr.sub_knock_handle(pi, sknock)

    # ------------------------------------------------------------------------
    def etf_buy_purchase_redeem_sell_req_handle(self, pi):
        if base_pb2.POLICY_DIRECTION_POSITIVE == pi.pack.base_param.direction:
            etf = self.pre_quo.etfs[pi.pack.code]
            key, policyid = self.get_policy_id(base_pb2.OPR_BUY_PURCHASE,
                                               pi.pack.code)
            seq_opr = TranBuyPurchase(self, key, pi, etf, etf.count)
            seq_opr.etf_buy_purchase()
        else:
            etf = self.robot.pre_quo.etfs[pi.pack.code]
            key, policyid = self.robot.get_policy_id()
            seq_opr = TranRedeemSell(self, key, pi, etf.count)
            seq_opr.etf_redeem_sell()

    # ------------------------------------------------------------------------
    def etf_fast_next(self, seq_opr, pi):
        seq_opr.knock_handle(pi)

    # ------------------------------------------------------------------------
    def etf_fast_req_handle(self, pi):
        if base_pb2.POLICY_DIRECTION_POSITIVE == pi.pack.base_param.direction:
            etf = self.robot.pre_quo.etfs[pi.pack.code]
            etf.count += 1
            key, policyid = self.get_policy_id()
            seq_opr = TranFastPurchase(self, key, pi, etf.count)
            seq_opr.etf_fast_purchase()
        else:
            etf = self.pre_quo.etfs[pi.pack.code]
            etf.count += 1
            key, policyid = self.get_policy_id()
            seq_opr = TranFastRedeem(self, key, pi, etf.count)
            seq_opr.etf_fast_redeem()
        pass

    # ------------------------------------------------------------------------
    def etf_order_resp_handle(self, pi):
        print 'etf resp hdl'
        print pi
        print('%serh %s%s' % (RED, pi.pack.ret_message.encode('utf8'), CLEAR))

        return error_pb2.SUCCESS

    # ------------------------------------------------------------------------
    def etf_pr_next(self, seq_opr, pi, sknock):
        """handle  etf purchase redeem order knock """
        seq_opr.knock_handle(pi, sknock)
        # if seq_opr.remain_qty <= 0:
        #     key = self.policy2key(pi.pack.policy_id)
        #     self.seqclnts.pop(key)
        #     print('%sSN remove %s %s%s' % (GREEN, pi.pack.policy_id, seq_opr,
        #           CLEAR))

    # ------------------------------------------------------------------------
    def etf_purchase_redeem_req_handle(self, pi):
        print('eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
        opr = base_pb2.OPR_REDEEM
        if ((base_pb2.POLICY_DIRECTION_POSITIVE ==
             pi.pack.base_param.direction)):
            opr = base_pb2.OPR_PURCHASE

        key, policyid = self.get_policy_id(opr, pi.pack.code)
        seq_opr = TranETF(self, key, pi, policyid, opr, pi.pack.code,
                          pi.pack.volume)
        etf = self.pre_quo.etfs[pi.pack.code]
        seq_opr.etf_purchase_redeem(pi.pack.volume, opr, policyid, etf)

        return error_pb2.SUCCESS

    # ------------------------------------------------------------------
    def login_handle(self, clnt_s, pi):
        pack = pi.pack
        sess = Sesstion(pack.trader_id, clnt_s)
        self.sessions[pack.trader_id] = sess
        login_resp = base_pb2.LoginResp()
        if pack.version >= VERSION:
            login_resp.result = error_pb2.SUCCESS
            sess.login = error_pb2.SUCCESS
            pi.sess = sess
        else:
            login_resp.result = error_pb2.ERROR_UPDATE
            login_resp.version = VERSION

        snddata = utils.make_package(
            base_pb2.SYS_ROBOT, base_pb2.CMD_LOGIN_RESP, pi, login_resp)
        sess.send_package(snddata)
        return sess
        # socket.send(snddata)

    # -------------------------------------------------------------------------
    def login_resp_handle(self, pi):
        """ login resp
        """
        # pack = pi.pack
        pass

    # ------------------------------------------------------------------------
    def new_session(self, clnt_s, address):
        # print 'x2' * 30
        # print(self.cfg)
        # print ''
        print('New connection from %s:%s' % address)
        MAX_PACK = 1024 * 1024
        login_flag = -1
        # alive = True

        while True:
            status, packlen, sysid, cmd, s1, s2, s3, s4 = utils.recv_header(
                clnt_s, base_pb2.HEADER_SIZE)

            if error_pb2.SUCCESS != status:
                break
            if packlen < 0 or packlen > MAX_PACK:
                print 'close connect error length', packlen
                break

            # 获取包体 收全包体
            print('new session len %d' % packlen)
            body = ''
            while len(body) < packlen:
                bpdata = clnt_s.recv(packlen - len(body))
                if not bpdata:
                    print 'no body'
                    break
                # print 'recv body'
                body += bpdata

            if len(body) != packlen:
                break
            # print('\033[0m') # print '=' * 40
            # print 'sysid 0x%x cmd 0x%x' % (sysid, cmd)
            if base_pb2.SYS_ROBOT == sysid:
                if base_pb2.CMD_LOGIN_REQ == cmd:
                    lgn = base_pb2.LoginReq()
                    lgn.ParseFromString(body)
                    pi = package_info(cmd, s1, s2, s3, s4, lgn)
                    sess = self.login_handle(clnt_s, pi)
                    login_flag = sess.login
                elif error_pb2.SUCCESS == login_flag:
                    status = self.client_package_handle(
                        cmd, s1, s2, s3, s4, body, sess)
                else:
                    print 'login first'
            else:
                break

        if sess is not None:
            sess.close()
        print ('disconnect close socket remain sesses %d' % len(self.sessions))
        self.sessions.pop(sess.tid)

    # ---------------------------------------------------------------------

    # ---------------------------------------------------------------------
    def try_send(self, sock, snddata):
        try:
            sock.send(snddata)
        except Exception, e:
            print('\033[31mclient something wrong!!!!%s\033[0m' % (e))

    # ---------------------------------------------------------------------
    def risk_handle(self, packlen, pi, body):
        cmd = pi.cmd
        if base_pb2.CMD_LOGIN_RESP == cmd:
            login_resp = base_pb2.LoginResp()
            login_resp.ParseFromString(body)
            pi.pack = login_resp
            self.login_resp_handle(pi)
            print('\033[32mrisk CMD_LOGIN_RESP \n%s\033[0m' % (login_resp))
        elif base_pb2.CMD_SINGLE_ORDER_RESP == cmd:
            print('\033[32mCMD_SINGLE_ORDER_RESP\033[0m')
            so_resp = stock_trade_pb2.SingleOrderResp()
            so_resp.ParseFromString(body)
            pi.pack = so_resp
            self.single_order_resp_handle(pi)
        elif base_pb2.CMD_SINGLE_WITHDRAWAL_RESP == cmd:
            print('\033[32mCMD_SINGLE_WITHDRAWAL_RESP\033[0m')
            sw_resp = stock_trade_pb2.SingleOrderResp()
            sw_resp.ParseFromString(body)
            pi.pack = sw_resp
            self.single_withdrawal_resp_handle(pi)
        elif base_pb2.CMD_BATCH_ORDER_RESP == cmd:
            print('\033[32mCMD_BATCH_ORDER_RESP\033[0m')
            bo_resp = stock_trade_pb2.StockBatchOrderResp()
            bo_resp.ParseFromString(body)
            pi.pack = bo_resp
            self.batch_order_resp(pi)
        elif base_pb2.CMD_STOCK_KNOCK_REQ == cmd:
            print('\033[32mCMD_STOCK_KNOCK_REQ   \033[0m')
            pack = trade_db_model_pb2.StockKnock()
            pack.ParseFromString(body)
            pi.pack = pack
            self.stock_knock_handle(pi)
        elif base_pb2.CMD_SUB_STOCK_KNOCK_REQ == cmd:
            print('\033[32mCMD_SUB_STOCK_KNOCK_REQ  \033[0m')
            # pack = stock_trade_pb2.QueryStockKnockResponse()
            # pack.ParseFromString(body)
            # pi.pack = pack
            # self.sub_stock_knock_handle(pi)
        elif base_pb2.CMD_STOCK_ORDER_REQ == cmd:
            print('\033[32mCMD_STOCK_ORDER_REQ\033[0m')
            pack = trade_db_model_pb2.StockOrder()
            pack.ParseFromString(body)
            pi.pack = pack
            self.stock_order_handle(pi)

        elif base_pb2.CMD_ETF_ORDER_RESP == cmd:
            so_resp = stock_trade_pb2.SingleOrderResp()
            so_resp.ParseFromString(body)
            pi.pack = so_resp
            self.etf_order_resp_handle(pi)

        elif base_pb2.CMD_ERROR_REQ == cmd:
            err = stock_trade_pb2.ErrResp()
            err.ParseFromString(body)
            print('risk handle %s %s' % (err.ret_code, err.ret_message))
        elif base_pb2.CMD_SUB_ASSET_REQ == cmd:
            # print('risk  CMD_SUB_ASSET_REQ :')
            pass
            # print pi.pack
        elif base_pb2.CMD_SUB_STOCK_POSITION_REQ == cmd:
            pack = stock_trade_pb2.QueryPositionResponse()
            pack.ParseFromString(body)
            pi.pack = pack
            # print('risk   CMD_SUB_STOCK_POSITION_REQ : ')
            # print((pack))
            # print pi.pack
        elif base_pb2.CMD_SUB_STOCK_ORDER_REQ == cmd:
            print(' risk  CMD_SUB_STOCK_ORDER_REQ :')
            pass
        elif base_pb2.CMD_HEARTBEAT_REQ == pi.cmd:
            fmt = ">iHHiiii"
            headbuffer = struct.pack(
                fmt, 0, base_pb2.SYS_STOCK, base_pb2.CMD_HEARTBEAT_RESP, 1,
                0, 0, 0)
            self.riskmgt.svr_sock.sendall(headbuffer)
        else:
            print('\033[32mrisk_handle unknow cmd 0x%x \033[0m' % (cmd))
            print('%srisk cmd 0x%x%s' % (RED, cmd, CLEAR))
        return error_pb2.SUCCESS

    # -------------------------------------------------------------------------
    def single_order2(self, seq_opr, policyid, code, volume, price, opr, mkid):
        # self.quo.c2id[pi.pack.code]
        order = stock_trade_pb2.SingleOrderReq()

        order.code = code        #
        order.price = price
        order.qty = volume              #
        order.bs_flag = opr
        order.policy_id = policyid
        order.trader_id = seq_opr.pi.sess.tid           #
        order.market = mkid
        order.instrument_type = 0x25

        s3 = self.get_seq()
        seq_opr.task.append((policyid, base_pb2.CMD_SINGLE_ORDER_REQ))
        seq_opr.s3 = s3
        print('so package 2 s3 %d: %s' % (s3, order))

        self.riskmgt.make_and_send(base_pb2.CMD_SINGLE_ORDER_REQ, s3,
                                   base_pb2.CMD_SINGLE_ORDER_REQ, order)

        return error_pb2.SUCCESS

    # -------------------------------------------------------------------------
    def single_order_handle(self, pi):
        """ 单笔现货报单 """
        # message StockPolicy
        # {
        #     required    PolicyBaseParam base_param             = 1; //基本参数
        #     required    string     code                        = 2; //证券代码
        #     required    uint32     volume                      = 3; //数量
        #     oneof price_type {
        #       uint32 price_level = 4; //价格档位。在不同的策略中，价格可能表示不同地方使用
        #       int64 price = 5; //价格(扩大10000倍后的值)
        #     }
        #     optional    uint32     reorder_interval            = 6; //撤补间隔(现货定时买卖时填写，期货每笔都填，默认为客户端直接填写1000，0表示不启用)。目前没用，先保留。
        # }
        opr = base_pb2.OPR_SELL
        if base_pb2.POLICY_DIRECTION_POSITIVE == pi.pack.base_param.direction:
            opr = base_pb2.OPR_BUY

        key, policyid = self.get_policy_id(opr, pi.pack.code)
        seq_opr = TransactionSingle(self, key, pi, policyid, 9999)
        seq_opr.single_buy_sell(opr)
        # print 'single order hdl', pi

        return error_pb2.SUCCESS

    # -------------------------------------------------------------------------
    def single_order_resp_handle(self, pi):
        pack = pi.pack

        policyid = pi.pack.policy_id
        key = self.policy2key(policyid)

        seq_opr = self.get_transaction(key)

        if seq_opr is None:
            print('so resp no policy [%s] ret %d %s' % (policyid,
                  pack.ret_code, pack.ret_message))
            return error_pb2.SUCCESS

        seq_opr.order_no = pack.order_no

        # print('single_resp %s' % (pack))
        snddata = utils.make_package(
            base_pb2.SYS_ROBOT, base_pb2.CMD_SINGLE_ORDER_RESP, seq_opr.pi,
            pack)
        seq_opr.pi.sess.send_package(snddata)
        return error_pb2.SUCCESS

    # -------------------------------------------------------------------------
    # def stock_knock_handle(self, pi):
    #     """  成交回报
    #     """
    #     pack = pi.pack
    #     key = self.policy2key(pi.pack.policy_id)
    #     seq_opr = self.get_transaction(key)
    #     print('%sknock %s \ntran\n%s%s' % (BLUE, pack, seq_opr, CLEAR))
    #     if seq_opr is None:
    #         # TODO try  from pack.policy_id get seq_opr
    #         return error_pb2.SUCCESS

    #     case = {
    #         base_pb2.CMD_STOCK_POLICY: self.single_next,
    #         base_pb2.CMD_STOCK_CREATE_OR_REDEEM_POLICY: self.etf_pr_next,
    #         # base_pb2.CMD_SINGLE_WITHDRAWAL_REQ: self.single_withrawal_next,

    #         base_pb2.CMD_STOCK_BASKET_POLICY: self.basket_next,
    #         # base_pb2.CMD_BASKET_WITHDRAWAL_REQ : self.basket_withdrawal_next,
    #         base_pb2.CMD_ETF_BS_OR_RS_POLICY: self.etf_bp_rs_next,
    #         base_pb2.CMD_ETF_QUICK_POLICY: self.etf_fast_next,
    #         base_pb2.CMD_FUND_ORDER_REQ: self.fund_next,
    #         base_pb2.CMD_GRADED_FUND_REQ: self.graded_next,
    #         # base_pb2.CMD_BUY_PURCHASE_REQ: self.fund_bp_next,
    #     }
    #     next_handler = case.get(seq_opr.pi.cmd, self.unknow_next)
    #     next_handler(seq_opr, pi)

    #     # snddata = utils.make_package(
    #     #     base_pb2.SYS_ROBOT, base_pb2.CMD_STOCK_KNOCK_REQ, seq_opr.pi,
    #     #     pack)
    #     # self.try_send(seq_opr.pi.sock, snddata)

    #     # 单笔买卖 etf申购 合并 拆分 全部成交

    # ------------------------------------------------------------------------
    def stock_order_handle(self, pi):
        """  委托回报
        """
        # 如果是自动撤补可以撤单下单了
        seq_opr = self.get_transaction(pi.pack.policy_id)
        if seq_opr is None:
            # snddata = utils.make_package_num(
            #     base_pb2.SYS_MTC, base_pb2.CMD_STOCK_ORDER_REQ, pi, pi.pack)
            # self.try_send()
            print('stock order not found seq_opr')
            return error_pb2.SUCCESS

        if base_pb2.CMD_BATCH_ORDER_REQ == seq_opr.pi.cmd:
            pass

    # ------------------------------------------------------------------------
    def sub_stock_knock_handle(self, pi):
        """  成交回报
            stock_trade_pb2.QueryStockKnockResponse()
        """
        for sknock in pi.pack.stock_knock:
            policyid = sknock.policy_id
            key = self.policy2key(policyid)
            seq_opr = self.get_transaction(key)
            print('%sknock key %s len(kk) %d len(trans) %d tran \n%s%s' %
                  (BLUE, policyid, len(pi.pack.stock_knock),
                   len(self.seqclnts), seq_opr, CLEAR))
            if seq_opr is None:
                # TODO try  from pack.policy_id get seq_opr
                print 'NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN'
                print self.seqclnts
                print self.seqclnts[key]
                print 'NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN'
                continue

            # print('%scmd 0x%x %s' % (RED, seq_opr.pi.cmd, CLEAR))
            case = {
                base_pb2.CMD_STOCK_POLICY: self.sub_single_next,
                base_pb2.CMD_STOCK_CREATE_OR_REDEEM_POLICY: self.etf_pr_next,
                base_pb2.CMD_STOCK_BASKET_POLICY: self.sub_basket_next,
                base_pb2.CMD_ETF_BS_OR_RS_POLICY: self.etf_bp_rs_next,

                base_pb2.CMD_SINGLE_ORDER_REQ: self.sub_single_next,
                base_pb2.CMD_ETF_ORDER_REQ: self.sub_single_next,
                base_pb2.CMD_BASKET_ORDER_REQ: self.sub_basket_next,
                base_pb2.CMD_FUND_ORDER_REQ: self.sub_fund_next,
                base_pb2.CMD_GRADED_FUND_REQ: self.sub_graded_next,
            }
            next_handler = case.get(seq_opr.pi.cmd, self.sub_unknow_next)
            print next_handler
            next_handler(seq_opr, pi, sknock)
            snddata = seq_opr.policy_status(pi, sknock)
            self.notify_policy_status(snddata)

        self.notify_sessions(pi)

        seq_opr.status_id += 1
        self.send_policy_status(seq_opr.pi.sess, pi, policyid,
                                error_pb2.SUCCESS,
                                'progressed', seq_opr.status_id)
        return error_pb2.SUCCESS
        # 单笔买卖 etf申购 合并 拆分 全部成交
    # ------------------------------------------------------------------------

    def sub_basket_next(self, seq_opr, pi, sknock):
        seq_opr.sub_knock_handle(pi, sknock)

    def sub_fund_next(self, seq_opr, pi, sknock):
        pass

    def sub_graded_next(self, seq_opr, pi, sknock):
        pass

    # ------------------------------------------------------------------------
    def sub_single_next(self, seq_opr, pi, sknock):
        remain_qty = seq_opr.sub_single_next(sknock)
        if remain_qty <= 0:
            pass
            # key = self.policy2key(sknock.policy_id)
            # self.seqclnts.pop(key)
            # print('%sSubSN remove pid %s tran %s%s' % (GREEN,
            #       sknock.policy_id, self, CLEAR))
        else:
            pass
            print('%sSubSN remaind pid %s tran %s\nmatch %d%s' % (GREEN,
                  sknock.policy_id, self, sknock.match_volume, CLEAR))

    def sub_unknow_next(self, seq_opr, pi, sknock):
        print 'sub unknow next pi.cmd 0x%x\ntran %s' % (pi.cmd, seq_opr)
        print 'type(seq_opr) %s' % type(seq_opr)
        print 'sub unknow next tran %s\n' % (seq_opr.pi)
        # print 'sub unknow next pi.cmd 0x%x\n%s' % (pi.cmd, sknock)
        pass
        # --------------------------------------------------

    # ------------------------------------------------------------------------
    def pause_policy_req_handle(self, pi):
        policyid = pi.pack.policy_id
        key = self.policy2key(policyid)
        seq_opr = self.get_transaction(key)
        if not isinstance(seq_opr, TranBasket):
            self.send_policy_status(pi.sess, pi, policyid,
                                    error_pb2.ERROR_NOT_BASKET_POLICY,
                                    'failed', 0)
            return error_pb2.ERROR_NOT_BASKET_POLICY

        seq_opr.basket_withdrawal(key)

    # ------------------------------------------------------------------------
    def query_stock_position_resp_handle(self, pi):
        seq_opr = self.get_stock_query(pi.s3)
        if seq_opr is None:
            print('none stock_query %s' % (pi.s3))
            return error_pb2.SUCCESS
        if ((base_pb2.CMD_BASKET_ORDER_REQ == seq_opr.pi.cmd and
             base_pb2.CMD_QUERY_FUTURE_POSITION_REQ == seq_opr.phase)):
            print pi
            # self.calc_buy(seq_opr, pi)
            seq_opr.calc_buy(pi)
            # 补齐篮子继续操作
            # 批量下单
            # # 应答
        else:
            print('wwwwwwwwwwwwwwww 0x%x' % (seq_opr.pi.cmd))
            pass

    def send_policy_status(self, sess, pi, policyid,
                           error, status, status_id):
        # message PolicyStatus
        # {
        #     optional    bytes      policy_id                   = 1; //策略id号
        #     optional    policy_type type                       = 2; //策略类型。这里直接显示策略的名称。TODO：采取字符串的方式对客户端不太友好，需要考虑是否替换。
        #     required    uint64     time_stamp                  = 3; //时间戳。从1970.1.1到现在的毫秒数。
        #     optional    Error      err                         = 4; //错误信息。
        #     required    string     status                      = 5; //状态："failed","created","progressed","paused","finished", "cancelled"
        #     required    uint32     status_id                   = 6; //状态id，一个policy session期内不断递增
        #     optional    double     percentage                  = 7; //进度百分比。取值为：0.0->1.0
        #     optional    uint64     start_time                  = 8; //起始时间。从1970.1.1到现在的毫秒数。
        #     optional    uint64     end_time                    = 9; //结束时间。从1970.1.1到现在的毫秒数。
        #     optional    uint64     b_s_amount                  = 10; //买入现货金额
        #     optional    uint64     s_s_amount                  = 11; //卖出现货金额
        #     optional    uint64     b_f_amount                  = 12; //买入期货金额
        #     optional    uint64     s_f_amount                  = 13; //卖出期货金额
        #     optional    uint64     match_volume                = 14; //单品种交易时的总成交量
        #     repeated    Parameter  parameters                  = 15; //附加参数。例如在篮子中，它包含了"ExpectedAmount（预估金额）", "PV（已成净值）", "Code（篮子ETF代码） or CustomBasket(自定义篮子项目：Code,Volume循环显示)", "Volume（篮子数）", "ExpertMode（专家模式标志）", "ReplaceFillableItems（可替代补足列表项,Code,Volume循环显示）"
        #     optional    string     logic_type                  = 16; //logic_center策略类型。手动客户端会使用LogicTypeManual。
        #     required    string     robot_ip                    = 17; //robot的IP地址
        #     optional    string     trader_id                   = 18; //交易员id。
        #     optional    string     trader_ip                   = 19; //交易员ip。
        #     optional    policy_direction direction             = 20; //买卖方向
        # }
        ps = ot_pb2.PolicyStatus()
        ps.policy_id = policyid
        ps.time_stamp = int(time.time())
        err = ot_pb2.Error()
        err.code = error
        ps.err.code = error
        ps.status = status
        ps.status_id = status_id
        ps.robot_ip = self.rip

        snddata = utils.make_package(
            base_pb2.SYS_MTC,
            base_pb2.CMD_POLICY_STATUS, pi, ps)
        sess.send_package(snddata)

        pass

    def single_next(self, seq_opr, pi, sknock):
        """handle single order knock """
        print 'ssssssssssssssss'
        # if seq_opr.remain_qty >= pi.pack.match_volume:
        seq_opr.remain_qty -= sknock.match_volume
        if seq_opr.remain_qty <= 0:
            key = self.policy2key(sknock.policy_id)
            self.seqclnts.pop(key)
            # print('%sSN remove %s %s%s' % (GREEN, sknock.policy_id, seq_opr,
            #       CLEAR))

    def stock_handler(self, packlen, pi, body):
        if base_pb2.CMD_QUERY_STOCK_POSITION_RESP == pi.cmd:
            print('%s CMD_QUERY_STOCK_POSITION_RESP %s' % (RED, CLEAR))
            pack = stock_trade_pb2.QueryPositionResponse()
            pack.ParseFromString(body)
            pi.pack = pack
            self.query_stock_position_resp_handle(pi)
        elif base_pb2.CMD_HEARTBEAT_REQ == pi.cmd:
            fmt = ">iHHiiii"
            headbuffer = struct.pack(
                fmt, 0, base_pb2.SYS_STOCK, base_pb2.CMD_HEARTBEAT_RESP, 1,
                0, 0, 0)
            self.stock_sock.svr_sock.sendall(headbuffer)
            # print('%s ' % (time.ctime(time.time())))
        elif base_pb2.CMD_SUB_ASSET_REQ == pi.cmd:
            pass
            print('  CMD_SUB_ASSET_REQ :')
            # pack = trade_db_model_pb2.StockAsset()
            # pack.ParseFromString(body)
            # print pi.pack
        elif base_pb2.CMD_SUB_STOCK_POSITION_REQ == pi.cmd:
            pass
            # print('  CMD_SUB_STOCK_POSITION_REQ :')
            # pack = trade_db_model_pb2.StockPosition()
            # pack.ParseFromString(body)
            # print pi.pack
        elif base_pb2.CMD_SUB_STOCK_ORDER_REQ == pi.cmd:
            pass
            print('CMD_SUB_STOCK_ORDER_REQ')
        elif base_pb2.CMD_SUB_STOCK_KNOCK_REQ == pi.cmd:
            print('\033[32mCMD_SUB_STOCK_KNOCK_REQ  \033[0m')
            pack = stock_trade_pb2.QueryStockKnockResponse()
            pack.ParseFromString(body)
            pi.pack = pack
            self.sub_stock_knock_handle(pi)
        elif base_pb2.CMD_SUBSCRIBE_TRADE_RESP == pi.cmd:
            pass
        elif base_pb2.CMD_LOGIN_RESP == pi.cmd:
            pack = base_pb2.LoginResp()
            pack.ParseFromString(body)
            print 'stock login result %d ver. %d' % (pack.result, pack.version)
        else:
            print('unknow stock svr cmd 0x%x' % (pi.cmd))
            print('%sstock_handle cmd 0x%x%s' % (RED, pi.cmd, CLEAR))

    # ------------------------------------------------------------------------
    def unknow_next(self, seq_opr, pi):
        print('unkonw next 0x%x' % (pi.cmd))
        pass
