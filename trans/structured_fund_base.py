#!usr/bin/env python
# coding=utf-8
# Author: zhezhiyong@163.com
# Created: 2016-03-08 08:14:29
# Python version：2.7.10

import uuid
from common.constant import OrderStatus
from pb import base_pb2, error_pb2
from common import pack_stock_pb


class TransactionBase(object):
    __slots__ = ('trans', 'request_id', 'batch_no', 'order_no', 'code', 'price', 'qty', 'market', 'cancel_qty',
                 'match_qty', 'finished', 'policy_id', 'bs_flag', 'trader_id', 'trader_ip', 'status', 'match_nos',
                 'robot', 'knocks', 'match_amount')

    def __init__(self, trans, code, price, qty, **kwargs):
        self.trans = trans
        self.robot = self.trans.robot
        # 当前订单的请求头，用来识别回报
        self.request_id = uuid.uuid1()
        # 委托批次号
        self.batch_no = None
        # 委托编号
        self.order_no = None

        self.code = code
        self.price = price
        self.qty = qty
        self.market = None
        self.cancel_qty = 0
        self.match_qty = 0
        self.match_amount = 0

        self.finished = False

        self.bs_flag = base_pb2.OPR_BUY
        self.policy_id = self.trans.policy_id
        self.trader_id = self.trans.ps.trader_id
        self.trader_ip = self.trans.ps.trader_ip

        self.status = OrderStatus.CREATE
        self.get_market_and_price()
        # 组合id，是否有组合
        self.knocks = []
        self.match_nos = []

    def get_market_and_price(self):
        """获取市场和价格"""
        mkid, lst = self.robot.quo.try_get_id(self.code)
        if mkid is -1:
            print 'stock code mkid is not exist in quota'
            self.finish(OrderStatus.FAILED)
            return
        self.market = mkid

        if lst is None:
            print 'stock code is lst not exist in quota'
            self.finish(OrderStatus.FAILED)
            return
        if self.bs_flag != base_pb2.OPR_BUY or self.bs_flag != base_pb2.OPR_SELL:
            return
        if self.price in base_pb2.policy_type.values():
            price_level = self.price
            self.price = lst[1].price(price_level, base_pb2.OPR_BUY)

    def succeed(self):
        """订单提交成功"""
        self.status = OrderStatus.ORDER_REQ_REP_RIGHT
        print 'curr order status: [%s]' % self.status

    def failed(self):
        """订单提交失败"""
        self.finish(OrderStatus.FAILED)

    def canceling(self):
        """撤单中"""
        self.status = OrderStatus.CANCELING

    def canceled(self):
        """撤单结束"""
        self.finish(OrderStatus.CANCELED)

    def cancel_submit(self):
        """撤单提交成功"""
        self.status = OrderStatus.CANCEL_SUBMITTED

    def knock(self, knock):
        """
        返回值True:表示该条knock被处理了， False表示该条Knock被忽略，用此去确认policy的相关回调不被掉错或多次调用
        """
        if knock.match_no not in self.match_nos:
            self.knocks.append(knock)
            self.match_nos.append(knock.match_no)
            self.match_qty += knock.match_volume
            self.match_amount += knock.match_amount
            print 'curr match qty: [%s]' % self.match_qty
            if self.qty == self.cancel_qty + self.match_qty:
                self.finish()
        else:
            print 'pass repeat knock'

    def finish(self, status=OrderStatus.FINISH):
        """"""
        self.finished = True
        self.status = status
        print 'order [%s] in policy [%s] finish, curr order status [%s]' % (self.order_no, self.policy_id, self.status)

    def execute(self):
        """When you execute policy immidiately, you write you code here and call it"""
        pass


class TransactionBuy(TransactionBase):
    def __init__(self, trans, code, price, qty, **kwargs):
        self.bs_flag = base_pb2.OPR_BUY
        super(TransactionBuy, self).__init__(trans, code, price, qty, **kwargs)

    def execute(self):
        if self.finished is True:
            print 'policy %s order[%s] is finished, do not execute order' % (self.policy_id, self.request_id)
            return
        if self.trans.finished is True:
            print 'policy [%s] is finished, do not execute order %s' % (self.policy_id, self.request_id)
            return
        # 组包，发送
        order = pack_stock_pb.pack_single_order(self.code, self.price, self.qty, self.bs_flag, self.market,
                                                self.policy_id, self.trader_id, self.trader_ip)
        self.robot.riskmgt.make_and_send_rid(base_pb2.CMD_SINGLE_ORDER_REQ, self.request_id, order)
        return True


class TransactionSale(TransactionBuy):
    def __init__(self, trans, code, price, qty, **kwargs):
        self.bs_flag = base_pb2.OPR_SELL
        super(TransactionSale, self).__init__(trans, code, price, qty, **kwargs)


class TransactionPurchase(TransactionBuy):
    """申购"""

    def __init__(self, trans, code, price, qty, **kwargs):
        self.bs_flag = base_pb2.OPR_PURCHASE
        super(TransactionPurchase, self).__init__(trans, code, price, qty, **kwargs)


class TransactionRedeem(TransactionBuy):
    """赎回"""

    def __init__(self, trans, code, price, qty, **kwargs):
        self.bs_flag = base_pb2.OPR_REDEEM
        super(TransactionRedeem, self).__init__(trans, code, price, qty, **kwargs)


class TransactionCombine(TransactionBuy):
    """合并"""

    def __init__(self, trans, code, price, qty, **kwargs):
        self.bs_flag = base_pb2.OPR_COMBINE
        super(TransactionCombine, self).__init__(trans, code, price, qty, **kwargs)


class TransactionSplit(TransactionBuy):
    """拆分"""

    def __init__(self, trans, code, price, qty, **kwargs):
        self.bs_flag = base_pb2.OPR_SPLIT
        super(TransactionSplit, self).__init__(trans, code, price, qty, **kwargs)


if __name__ == "__main__":
    print base_pb2.policy_type.values()
