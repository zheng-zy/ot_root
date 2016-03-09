#!usr/bin/env python
# coding=utf-8
"""
# TODO(purpose): 打包跟报单服务的pb
"""

from pb import stock_trade_pb2, base_pb2
from common import constant


def pack_single_order(code, price, qty, bs_flag, market, policy_id, tid, tip):
    s_order = stock_trade_pb2.SingleOrderReq()
    s_order.code = code
    s_order.price = price
    s_order.qty = qty
    s_order.bs_flag = bs_flag
    s_order.market = market
    s_order.policy_id = policy_id
    s_order.trader_id = 'PH1'
    s_order.trader_ip = '192.168.15.34'
    s_order.instrument_type = constant.kInstrumentTypeFunds
    s_order.basket_amount = price * qty
    s_order.client_type = base_pb2.MANUAL_TRADE
    return s_order


def pack_single_cancel(order_no, market, policy_id, trader_id, trader_ip):
    s_cancel = stock_trade_pb2.SingleCancelReq()
    s_cancel.order_no = order_no
    s_cancel.market = market
    s_cancel.policy_id = policy_id
    s_cancel.trader_id = trader_id
    s_cancel.trader_ip = trader_ip
    return s_cancel
