#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" global data type define
"""

__author__ = 'qinjing'
import uuid


class package_info(object):
    __slots__ = ('cmd', 'rid', 'pack', 'sess', 'opr', 'sock')

    def __str__(self):
        return ('cmd:0x%x uuid:%s sock:%s sess %s\npack:%s' %
                (self.cmd, self.rid, self.sess, self.sess, self.pack))

    def __init__(self, cmd, rid, pack=None, sess=None):
        self.cmd = cmd
        self.rid = uuid.UUID(bytes=rid)
        self.opr = 0
        self.pack = pack
        if sess is not None:
            assert isinstance(sess, Sesstion)
            self.sess = sess
        if (sess is not None):
            self.sock = sess.sock


class Sesstion(object):
    # tid 交易员id：trade_id
    # sock 通信实例
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
