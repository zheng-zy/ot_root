#!usr/bin/env python
# coding=utf-8
# Author: zhezhiyong@163.com
# Created: 2016年02月19日 19:10:38
# 编辑器：pycharm5.0.2，python版本：2.7.10
"""
# TODO(purpose): 
"""

import transaction
from pb import base_pb2, ot_pb2, stock_trade_pb2, trade_db_model_pb2, error_pb2
from common import timeUtils, constant
import message
import uuid
from common import pack_stock_pb
from structured_fund_base import *


class TranStructureFund(object):
    LOG_TAG = "TranStructureFund"
    __slots__ = ('robot', 'key', 'policy_id', 'etfcode', 'pr_remain_qty',
                 'bs_remain_qty', 'order_no', 'count', 'pi',
                 'task', 'opr', 's3', 'pr_volume',
                 'bs_volume', 'status_id',
                 'ps', 'base_param', 'finished', 'buy_stocks_table', 'sell_stocks_table', 'all_order_table',
                 'all_order_resp_table', 'estimated_amt', 'knock_amt', 'stage_lst', 'curr_stage')

    def __init__(self, robot, policy_id, pi, **kwargs):
        self.robot = robot
        self.policy_id = policy_id
        self.pi = pi
        self.base_param = self.pi.pack.base_param
        self.finished = False

        self.ps = ot_pb2.PolicyStatus()
        self.init_policy_status()

        # policy所有涉及订单存储参数
        self.buy_stocks_table = {}
        self.sell_stocks_table = {}
        # 所有订单,未收到确认
        self.all_order_table = {}
        # 所有订单,收到确认
        self.all_order_resp_table = {}

        # 预估金额
        self.estimated_amt = 0.0
        # 成交金额
        self.knock_amt = 0.0

        # 组合使用
        self.curr_stage = 1
        self.stage_lst = [1]

        self.robot.set_transaction(policy_id, self)

    def set_stage(self, curr_stage, stage_lst):
        self.curr_stage = curr_stage
        self.stage_lst = stage_lst

    def next_stage(self):
        self.curr_stage += 1

    def init_policy_status(self):
        self.ps.policy_id = self.policy_id
        self.ps.type = base_pb2.STOCK_SINGLE_ORDER
        self.ps.time_stamp = timeUtils.getCurrentTotalMSeconds()

        self.ps.err.time_stamp = timeUtils.getCurrentTotalMSeconds()
        self.ps.err.code = 0
        self.ps.err.reason = ''

        self.ps.status = message.PLC_STS_CREATE
        self.ps.status_id = 1
        self.ps.percentage = 0  # 进度百分比0.0-1.0
        self.ps.start_time = timeUtils.getCurrentTotalMSeconds()
        self.ps.end_time = 0
        self.ps.b_s_amount = 0
        self.ps.s_s_amount = 0
        self.ps.match_volume = 0  # 单品种交易总成交量
        self.ps.logic_type = 'LogicTypeManual'  # logic_center策略类型。手动客户端会使用LogicTypeManual。
        self.ps.robot_ip = self.robot.cfg['robot_listen']['rip']
        self.ps.trader_id = self.pi.pack.base_param.trader_id
        self.ps.trader_ip = self.pi.pack.base_param.trader_ip
        self.ps.direction = self.pi.pack.base_param.direction
        self.pack_and_send()

    def get_sf_info(self, code):
        # 获取市场和价格
        mkid, lst = self.robot.quo.try_get_id(code)
        if lst is None:
            print 'stock code is lst not exist in quota'
            return
        # self.structured_fund_info = quota_data.QuotaData.get_structured_fund_info(self.code)
        return lst[1].md

    def _calculate_percentage(self):
        estimated_amt = 0.0
        match_amt = 0.0
        for order_no, order in self.all_order_resp_table.items():
            estimated_amt += order.estimated_amount
            match_amt += order.match_amount
        if estimated_amt != 0:
            self.ps.percentage = match_amt / estimated_amt
        pass

    def update_policy_status(self):
        """根据订单回报，更新策略状态"""
        before = self.ps.status
        order_status = 100
        for order_no, order in self.all_order_resp_table.items():
            order_status = min(order_status, order.status)
        if 20 > order_status > 10:
            self.ps.status = message.PLC_STS_PROGRESSED
        elif 40 > order_status > 30:
            self.ps.status = message.PLC_STS_PROGRESSED
        elif 50 > order_status > 40:
            self.ps.status = message.PLC_STS_CANCELLED
        elif order_status > 50:
            self.next_stage()
            if self.curr_stage in self.stage_lst:
                self.execute(self.curr_stage)
                self.ps.status = message.PLC_STS_PROGRESSED
            else:
                self.ps.status = message.PLC_STS_FINISHED

        elif 0 > order_status:
            self.ps.status = message.PLC_STS_FAILED
            pass
        print 'policy_id: [%s] update policy_status [%s] to [%s]' % (self.policy_id, before, self.ps.status)
        self._calculate_percentage()
        self.pack_and_send()

    def succeed(self, pi):
        """订单提交成功"""
        order = self.all_order_table.get(pi.rid)
        if order is None:
            return
        order.order_no = pi.pack.order_no
        self.all_order_resp_table[order.order_no] = order
        print '[%s] policy [%s] receive succeed, request_id [%s] order_no [%s]' % (
            self.LOG_TAG, self.policy_id, order.request_id, order.order_no)
        order.succeed()
        self.update_policy_status()
        return self.ps

    def failed(self, pi):
        """订单提交失败"""
        order = self.all_order_table.get(pi.rid)
        if order is None:
            return
        order.order_no = pi.pack.order_no
        print '[%s] policy [%s] receive failed, request_id [%s] ret_code [%s] ret_message [%s]' % (
            self.LOG_TAG, self.policy_id, order.request_id, pi.pack.ret_code, pi.pack.ret_message)
        order.failed()
        self.update_policy_status()
        return self.ps

    def cancel(self):
        """撤单操作,防止重复撤单"""
        # self.status = OrderStatus.CANCELING
        for order_no, order in self.all_order_resp_table.items():
            order.cancel()

    def cancel_submit(self, pi):
        """撤单提交成功"""
        order = self.all_order_resp_table.get(pi.pack.order_no)
        if order is None:
            return
        print '[%s] policy [%s] receive cancel_submit, request_id [%s] order_no [%s]' % (
            self.LOG_TAG, self.policy_id, order.request_id, order.order_no)
        order.cancel_submit()
        self.update_policy_status()
        return self.ps

    # def canceled(self, pi):
    #     """撤单回报，合并到成交回报处理"""
    #     stock_knocks = pi.pack.stock_knock
    #     for knock in stock_knocks:
    #         order = self.all_order_resp_table.get(knock.order_no)
    #         if order is None:
    #             return
    #         print '[%s] policy [%s] receive canceled, request_id [%s] order_no [%s]' % (
    #             self.LOG_TAG, self.policy_id, order.request_id, order.order_no)
    #         order.canceled()
    #     self.update_policy_status()
    #     return self.ps

    def knock(self, pi):
        """成交回报处理"""
        stock_knocks = pi.pack.stock_knock
        for knock in stock_knocks:
            order = self.all_order_resp_table.get(knock.order_no)
            if order is None:
                return
            print '[%s] policy [%s] receive knock, request_id [%s] order_no [%s]' % (
                self.LOG_TAG, self.policy_id, order.request_id, order.order_no)
            order.knock(knock)
        self.update_policy_status()
        return self.ps

    def pack_and_send(self):
        """发送状态"""
        sess = self.robot.sessions.get(self.ps.trader_id)
        if sess is not None:
            self.ps.time_stamp = timeUtils.getCurrentTotalMSeconds()
            # print "**********************ps**************************"
            # print self.ps
            # print "************************************************"
            snddata = utils.make_package(base_pb2.SYS_ROBOT, base_pb2.CMD_POLICY_STATUS, self.pi.rid, self.ps)
            sess.sock.send(snddata)
            # for sess_pm in self.robot.sub_sessions:
            #     print sess_pm
            #     sess_pm.sock.send(snddata)


    def execute(self, stage=1):
        """When you execute policy immidiately, you write you code here and call it"""

    def buy(self, code, price, qty, **kwargs):
        print 'policy [%s] buy code: [%s], price: [%s], qty: [%s]' % (self.policy_id, code, price, qty)
        order = TransactionBuy(self, code, price, qty, **kwargs)
        order.execute()
        self.all_order_table[order.request_id] = order

    def sell(self, code, price, qty, **kwargs):
        print 'policy [%s] sale code: [%s], price: [%s], qty: [%s]' % (self.policy_id, code, price, qty)
        order = TransactionSale(self, code, price, qty, **kwargs)
        order.execute()
        self.all_order_table[order.request_id] = order

    def purchase(self, code, price, qty, **kwargs):
        print 'policy [%s] purchase code: [%s], price: [%s], qty: [%s]' % (self.policy_id, code, price, qty)
        order = TransactionPurchase(self, code, price, qty, **kwargs)
        order.execute()
        self.all_order_table[order.request_id] = order

    def redeem(self, code, price, qty, **kwargs):
        print 'policy [%s] redeem code: [%s], price: [%s], qty: [%s]' % (self.policy_id, code, price, qty)
        order = TransactionRedeem(self, code, price, qty, **kwargs)
        order.execute()
        self.all_order_table[order.request_id] = order

    def split(self, code, price, qty, **kwargs):
        print 'policy [%s] split code: [%s], price: [%s], qty: [%s]' % (self.policy_id, code, price, qty)
        order = TransactionSplit(self, code, price, qty, **kwargs)
        order.execute()
        self.all_order_table[order.request_id] = order

    def combine(self, code, price, qty, **kwargs):
        print 'policy [%s] combine code: [%s], price: [%s], qty: [%s]' % (self.policy_id, code, price, qty)
        order = TransactionCombine(self, code, price, qty, **kwargs)
        order.execute()
        self.all_order_table[order.request_id] = order


class TranStructureFundBuy(TranStructureFund):
    LOG_TAG = "TranStructureFundBuy"

    def __init__(self, robot, policy_id, pi, **kwargs):
        super(TranStructureFundBuy, self).__init__(robot, policy_id, pi, **kwargs)
        self.params = kwargs
        self.code = self.pi.pack.code
        self.qty = self.pi.pack.volume
        self.price_type = self.pi.pack.__getattribute__(self.pi.pack.WhichOneof('price_type'))
        self.reorder_interval = 0
        if self.pi.pack.HasField('reorder_interval'):
            self.reorder_interval = self.pi.pack.reorder_interval

    def execute(self, stage=1):
        if stage == 1:
            if None in [self.code, self.qty, self.price_type]:
                print 'Param is not right, pi.pack: %s' % self.pi.pack
            if self.base_param.direction not in [0, 1]:
                print 'Param is not right, direction: [%s]' % self.base_param.direction
            self.buy(self.code, self.price_type, self.qty)


class TranStructureFundSale(TranStructureFundBuy):
    LOG_TAG = "TranStructureFundSale"

    def __init__(self, robot, policy_id, pi, **kwargs):
        super(TranStructureFundSale, self).__init__(robot, policy_id, pi, **kwargs)

    def execute(self, stage=1):
        if stage == 1:
            if None in [self.code, self.qty, self.price_type]:
                print 'Param is not right, pi.pack: %s' % self.pi.pack
            if self.base_param.direction not in [0, 1]:
                print 'Param is not right, direction: [%s]' % self.base_param.direction
            self.sell(self.code, self.price_type, self.qty)


class TranStructureFundPurchase(TranStructureFund):
    LOG_TAG = "TranStructureFundPurchase"

    def __init__(self, robot, policy_id, pi, **kwargs):
        super(TranStructureFundPurchase, self).__init__(robot, policy_id, pi, **kwargs)
        self.code = self.pi.pack.code
        self.qty = self.pi.pack.volume

    def execute(self, stage=1):
        if stage == 1:
            if None in [self.code, self.qty]:
                print 'Param is not right, pi.pack: %s' % self.pi.pack
            self.qty = int(self.qty)
            self.purchase(self.code, 0, self.qty)


class TranStructureFundRedeem(TranStructureFundPurchase):
    LOG_TAG = "TranStructureFundRedeem"

    def __init__(self, robot, policy_id, pi, **kwargs):
        super(TranStructureFundRedeem, self).__init__(robot, policy_id, pi, **kwargs)

    def execute(self, stage=1):
        if stage == 1:
            if None in [self.code, self.qty]:
                print 'Param is not right, pi.pack: %s' % self.pi.pack
            self.qty = int(self.qty)
            self.redeem(self.code, 0, self.qty)


class TranStructureFundSplit(TranStructureFundPurchase):
    LOG_TAG = "TranStructureFundSplit"

    def __init__(self, robot, policy_id, pi, **kwargs):
        super(TranStructureFundSplit, self).__init__(robot, policy_id, pi, **kwargs)

    def execute(self, stage=1):
        if stage == 1:
            if None in [self.code, self.qty]:
                print 'Param is not right, pi.pack: %s' % self.pi.pack
            self.qty = int(self.qty)
            self.split(self.code, 0, self.qty)


class TranStructureFundCombine(TranStructureFundPurchase):
    LOG_TAG = "TranStructureFundCombine"

    def __init__(self, robot, policy_id, pi, **kwargs):
        super(TranStructureFundCombine, self).__init__(robot, policy_id, pi, **kwargs)

    def execute(self, stage=1):
        if stage == 1:
            if None in [self.code, self.qty]:
                print 'Param is not right, pi.pack: %s' % self.pi.pack
            self.qty = int(self.qty)
            self.combine(self.code, 0, self.qty)


import yaml
import uuid
from dao import datatype
import struct
from common import utils


class Robot:
    def __init__(self, conf):
        self.seqclnts = {}
        with open(conf) as f:
            self.cfg = yaml.load(f)
        pass

    def set_transaction(self, key, trans):
        self.seqclnts[key] = trans
        return trans


def simulate_client_get_pi():
    tid = '10001'
    cmd = base_pb2.CMD_STOCK_POLICY
    key = uuid.uuid1()
    print key
    # print uuid.UUID(bytes=key.get_bytes())
    s = struct.pack('16s', key.get_bytes())
    s1, s2, s3, s4 = struct.unpack('iiii', s)
    pack = ot_pb2.StockPolicy()
    pack.base_param.trader_id = tid
    pack.base_param.trader_ip = '127.0.0.1'
    pack.volume = 1000
    sess = datatype.Sesstion(tid, None)
    pi = datatype.package_info(cmd, s1, s2, s3, s4, pack, sess)
    return pi


if __name__ == "__main__":
    robot = Robot('robot.yaml')
    key = timeUtils.getCurentTotalMicroseconds()
    fund = TranStructureFund(robot, key, simulate_client_get_pi())
    print fund.ps

    fund.execute()
