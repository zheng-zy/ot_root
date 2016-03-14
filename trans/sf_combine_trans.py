#!usr/bin/env python
# coding=utf-8
# Author: zhezhiyong@163.com
# Created: 2016-03-08 08:14:29
# Python version：2.7.10
"""
# TODO(purpose): 分级基金组合策略
"""
import transaction
from pb import base_pb2, ot_pb2, stock_trade_pb2, trade_db_model_pb2, error_pb2
from common import timeUtils, constant
import message
import uuid
from common import pack_stock_pb
from structured_fund_base import *
from structured_fund_trans import *


class TranStructureFundLinkBuy(TranStructureFund):
    LOG_TAG = "TranStructureFundLinkBuy"

    def __init__(self, robot, policy_id, pi, **kwargs):
        super(TranStructureFundLinkBuy, self).__init__(robot, policy_id, pi, **kwargs)
        self.params = kwargs
        self.code_a = self.pi.pack.code_a
        self.code_b = self.pi.pack.code_b
        self.qty_a = self.pi.pack.volume_a
        self.qty_b = self.pi.pack.volume_b
        self.price = self.pi.pack.price
        self.price_level = self.pi.pack.price_level
        self.link_direction = self.pi.pack.link_direction

    def execute(self, stage=1):
        if stage == 1:
            if None in [self.code_a, self.code_b, self.qty_a, self.qty_b, self.price, self.price_level,
                        self.link_direction]:
                print 'param is not right, pi.pack: %s' % self.pi.pack

            if self.link_direction == 0:
                # a联动b
                self.buy(self.code_a, self.price, self.qty_a)
                self.buy(self.code_b, self.price_level, self.qty_b)
            elif self.link_direction == 1:
                # b联动a
                self.buy(self.code_a, self.price_level, self.qty_a)
                self.buy(self.code_b, self.price, self.qty_b)


class TranStructureFundLinkSale(TranStructureFundLinkBuy):
    LOG_TAG = "TranStructureFundLinkSale"

    def __init__(self, robot, policy_id, pi, **kwargs):
        super(TranStructureFundLinkSale, self).__init__(robot, policy_id, pi, **kwargs)

    def execute(self, stage=1):
        if stage == 1:
            if None in [self.code_a, self.code_b, self.qty_a, self.qty_b, self.price, self.price_level,
                        self.link_direction]:
                print 'param is not right, pi.pack: %s' % self.pi.pack

            if self.link_direction == 0:
                # a联动b
                self.sell(self.code_a, self.price, self.qty_a)
                self.sell(self.code_b, self.price_level, self.qty_b)
            elif self.link_direction == 1:
                # b联动a
                self.sell(self.code_a, self.price_level, self.qty_a)
                self.sell(self.code_b, self.price, self.qty_b)


class TranStructureFundABBuy(TranStructureFund):
    LOG_TAG = "TranStructureFundABBuy"

    def __init__(self, robot, policy_id, pi, **kwargs):
        super(TranStructureFundABBuy, self).__init__(robot, policy_id, pi, **kwargs)
        self.params = kwargs
        self.code = self.pi.pack.code
        self.qty = self.pi.pack.volume
        # 基数100000，如2%则price_ratio为2000
        self.price_ratio = self.pi.pack.price_ratio / 100000
        self.structured_fund_info = None

    def execute(self, stage=1):
        """"""
        if stage == 1:
            if None in [self.code, self.qty, self.price_ratio]:
                print 'Param is not right, pi.pack: %s' % self.pi.pack

            self.structured_fund_info = self.get_sf_info(self.code)
            print self.code
            print self.structured_fund_info
            if self.structured_fund_info is not None:
                # a+b买卖
                self.buy(self.structured_fund_info.a_stk_id, self.price_ratio,
                         self.qty * self.structured_fund_info.a_ratio / (
                             self.structured_fund_info.a_ratio + self.structured_fund_info.b_ratio))
                self.buy(self.structured_fund_info.b_stk_id, self.price_ratio,
                         self.qty * self.structured_fund_info.b_ratio / (
                             self.structured_fund_info.a_ratio + self.structured_fund_info.b_ratio))


class TranStructureFundABSale(TranStructureFundABBuy):
    LOG_TAG = "TranStructureFundABSale"

    def __init__(self, robot, policy_id, pi, **kwargs):
        super(TranStructureFundABSale, self).__init__(robot, policy_id, pi, **kwargs)

    def execute(self, stage=1):
        """"""
        if stage == 1:
            if None in [self.code, self.qty, self.price_ratio]:
                print 'param is not right, pi.pack: %s' % self.pi.pack

            self.structured_fund_info = self.get_sf_info(self.code)

            if self.structured_fund_info is not None:
                self.sell(self.structured_fund_info.a_stk_id, self.price_ratio,
                          self.qty * self.structured_fund_info.a_ratio / (
                              self.structured_fund_info.a_ratio + self.structured_fund_info.b_ratio))
                self.sell(self.structured_fund_info.b_stk_id, self.price_ratio,
                          self.qty * self.structured_fund_info.b_ratio / (
                              self.structured_fund_info.a_ratio + self.structured_fund_info.b_ratio))


class TranStructureFundBuyAndMerging(TranStructureFund):
    LOG_TAG = "TranStructureFundBuyAndMerging"

    def __init__(self, robot, policy_id, pi, **kwargs):
        super(TranStructureFundBuyAndMerging, self).__init__(robot, policy_id, pi, **kwargs)
        self.params = kwargs
        # 母基金代码
        self.code = self.pi.pack.code
        self.qty = self.pi.pack.volume
        # 基数100000，如2%则price_ratio为2000
        self.price_ratio = self.pi.pack.price_ratio

        self.code_a = None
        self.code_b = None
        self.price_a = None
        self.price_b = None

        self.set_stage(curr_stage=1, stage_lst=[1, 2])

    # ----------------------------------------------------------------------
    def execute(self, stage=1):
        """"""
        if stage == 1:
            if None in [self.code, self.qty, self.price_ratio]:
                print ('param is not right, pi.pack: %s' % self.pi.pack)
            # a+b买卖
            self.buy(self.code_a, self.price_ratio, self.qty)
            self.buy(self.code_b, self.price_ratio, self.qty)
        if stage == 2:
            self.combine(self.code, 0, self.qty)


class TranStructureFundSplittingAndSale(TranStructureFundBuyAndMerging):
    LOG_TAG = "TranStructureFundSplittingAndSale"

    def __init__(self, robot, policy_id, pi, **kwargs):
        super(TranStructureFundSplittingAndSale, self).__init__(robot, policy_id, pi, **kwargs)

    # ----------------------------------------------------------------------
    def execute(self, stage=1):
        """"""
        if stage == 1:
            if None in [self.code, self.qty, self.price_ratio]:
                print ('param is not right, pi.pack: %s' % self.pi.pack)
            self.split(self.code, 0, self.qty)
        if stage == 2:
            self.sell(self.code_a, self.price_ratio, self.qty)
            self.sell(self.code_b, self.price_ratio, self.qty)


class TranStructureFundQuickMerging(TranStructureFund):
    LOG_TAG = "TranStructureFundQuickMerging"

    def __init__(self, robot, policy_id, pi, **kwargs):
        super(TranStructureFundQuickMerging, self).__init__(robot, policy_id, pi, **kwargs)

        self.params = kwargs
        # 母基金代码
        self.code = self.pi.pack.code
        self.qty = self.pi.pack.volume
        # 基数100000，如2%则price_ratio为2000
        self.price_ratio = self.pi.pack.price_ratio / 100000
        # 子基金
        self.ab_price_ratio = self.pi.pack.ab_price_ratio / 100000

        self.code_a = None
        self.code_b = None
        self.price_a = None
        self.price_b = None

        self.set_stage(curr_stage=1, stage_lst=[1, 2, 3])

    def execute(self, stage=1):
        """"""
        if stage == 1:
            if None in [self.code, self.qty, self.price_ratio]:
                print ('param is not right, pi.pack: %s' % self.pi.pack)
            # 买入ab基金
            self.buy(self.code, self.ab_price_ratio, self.qty)
            self.buy(self.code, self.ab_price_ratio, self.qty)
        # 合并成母基金
        if stage == 2:
            self.combine(self.code, 0, self.qty)
        # 卖出母基金
        if stage == 3:
            self.sell(self.code, self.price_ratio, self.qty)


class TranStructureFundQuickSplitting(TranStructureFundQuickMerging):
    LOG_TAG = "TranStructureFundQuickSplitting"

    def __init__(self, robot, policy_id, pi, **kwargs):
        super(TranStructureFundQuickSplitting, self).__init__(robot, policy_id, pi, **kwargs)

    def execute(self, stage=1):
        if stage == 1:
            if None in [self.code, self.qty, self.price_ratio]:
                print ('param is not right, pi.pack: %s' % self.pi.pack)
            # 买入母基金
            self.buy(self.code, self.price_ratio, self.qty)
        if stage == 2:
            # 拆分成子基金
            self.split(self.code, 0, self.qty)
        if stage == 3:
            # 卖出子基金
            self.sell(self.code, self.ab_price_ratio, self.qty)
            self.sell(self.code, self.ab_price_ratio, self.qty)
