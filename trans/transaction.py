#!/usr/bin/env python
# -*- coding: utf-8 -*-


""" transaction implement
"""

# import tm_task
from pb import base_pb2
from pb import error_pb2
from pb import ot_pb2
import message
import time
from common import utils

__author__ = 'qinjing'

RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
CLEAR = '\033[0m'


# ----------------------------------------------------------------------------
class SeqOperation(object):
    __slots__ = ('robot', 'key', 'count', 'pi', 'task', 'phase', 's3',
                 'totalcash')

    def __init__(self, robot, key, pi, count):
        self.robot = robot
        self.count = count
        self.pi = pi
        self.task = []
        self.phase = pi.cmd
        self.s3 = 0
        self.totalcash = 0
        self.key = key
        self.robot.set_transaction(key, self)

    def __str__(self):
        return ('task: %d \n%s\npi:%s' %
                (len(self.task), self.task, self.pi))


# -----------------------------------------------------------------------------
class TransactionSingle(SeqOperation):
    __slots__ = ('remain_qty', 'order_no', 'policyid', 'opr', 'status_id',
                 'volume')

    def __init__(self, robot, key, pi, policyid, count):
        super(TransactionSingle, self).__init__(robot, key, pi, count)
        try:
            self.remain_qty = pi.pack.qty
        except:
            self.remain_qty = pi.pack.volume

        self.order_no = None
        self.policyid = policyid
        self.status_id = 0
        self.volume = pi.pack.volume

    def __str__(self):
        return ('task: %d \n%s\npi:%s' %
                (len(self.task), self.task, self.pi))

    def sub_single_next(self, sknock):
        self.remain_qty -= sknock.match_volume
        self.robot.quo.update_knock_info(
                sknock.stock_id, sknock.market, sknock.bs_flag,
                sknock.match_volume)

        return self.remain_qty

    def single_next(self, pi):
        sknock = pi.pack.stock_knock[0]
        self.remain_qty -= sknock.match_volume
        return self.remain_qty

    def single_buy_sell(self, opr):
        pi = self.pi
        pack = pi.pack
        # print('sngl_rdr_hndl: pack %s' % (pi))

        # s3 = self.robot.get_seq()
        code = pi.pack.code
        volume = pi.pack.volume
        mkid, lst = self.robot.quo.try_get_id(code)
        if lst is None:
            print 'NONE stock 0 %s' % (len(self.robot.quo[0]))
            print 'NONE stock 1 %s' % (len(self.robot.quo[1]))
            return error_pb2.ERROR_NOT_EXIST_STOCK

        if pack.HasField('price'):
            price = pi.pack.price
        else:
            price = lst[1].price(pi.pack.price_level, opr)

        if base_pb2.OPR_BUY == opr or base_pb2.OPR_SELL == opr:
            # policyid = self.get_policy_id(opr, 9999)
            # self.single_order(pi, s3, 0, seq_opr, policyid)
            self.robot.single_order2(self, self.policyid, code,
                                     volume, price, opr, mkid)
        else:
            print('so %s' % (pack))

    def policy_status(self, pi, sknock):
        self.status_id += 1
        status = message.PLC_STS_PROGRESSED
        if self.remain_qty == 0:
            status = message.PLC_STS_FINISHED

        # self.robot.send_policy_status(
        #     self.pi.sess, self.pi, sknock.policy_id,
        #     error_pb2.SUCCESS, status, self.status_id)

        ps = ot_pb2.PolicyStatus()
        ps.policy_id = sknock.policy_id
        ps.time_stamp = int(time.time())
        err = ot_pb2.Error()
        err.code = error_pb2.SUCCESS
        ps.err.code = error_pb2.SUCCESS
        ps.status = status
        ps.status_id = self.status_id
        ps.robot_ip = self.robot.rip

        print'etf policy_status remain_qty %d volume %d ps\n%s' % (
            self.remain_qty, self.volume, ps)

        snddata = utils.make_package(
                base_pb2.SYS_MTC,
                base_pb2.CMD_POLICY_STATUS, pi, ps)
        return snddata
        # sess.send_package(snddata)



