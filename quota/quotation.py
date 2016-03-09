#!/usr/bin/env python
# -*- coding: utf-8 -*-


""" a robot
"""


import struct
import gevent
# from gevent import socket
# import time
from net import baseclient

# import utils
#  import pq_quota_pb2
from pb import base_pb2
from pb import quotation_def_pb2
from pb import quota_pb2

from dao.stock_def import StockInfo

__author__ = 'qinjing'


RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
CLEAR = '\033[0m'


def get_current_function():
    import inspect
    return (inspect.stack()[1][3])


#  -------------------------------------------------------------------------
class Quotation(baseclient.BaseClient):
    def __init__(self, app, addr):
        super(Quotation, self).__init__(app, addr)
        self.c2id = {}
        self.id2c = {}
        self.pre_quo = self.app.pre_quo
        self.seq = 0

    def after_connect(self, err):
        #  订阅心跳
        fmt = "!iHHiiii"
        headbuffer = struct.pack(
            fmt, 0, base_pb2.SYS_QUOTATION, base_pb2.CMD_HEARTBEAT_REQ,
            base_pb2.SYS_QUOTATION, 0, 0, self.seq)
        self.seq += 1
        sentdata = headbuffer
        self.svr_sock.send(sentdata)

        #  请求代码列表：深证 ：上证 请求期货代码列表
        sub_mkt = [base_pb2.MKT_SZ, base_pb2.MKT_SH, base_pb2.MKT_CF]
        for sm in sub_mkt:
            self.send_codetable(sm)
            self.c2id[sm] = {}

        submktype = quota_pb2.MarketDataReqByMdType()
        submktype.sub_type = 1
        submktype.mk_type = 1012
        self.try_send(submktype,
                      quotation_def_pb2.LYMK_MARKETDATA_REQ_BY_MD_TYPE)

    def send_codetable(self, mkid):
        ctable = quota_pb2.CodeTableReq()
        ctable.exchid = mkid

        self.try_send(ctable, quotation_def_pb2.LYMK_CODETABLE_REQ)

    def package_handle(self, packlen, pi, body):
        cmd = pi.cmd
        #  返回行情数据 (盘口)
        if cmd == quotation_def_pb2.LYMK_MARKETDATA:
            md = quota_pb2.MarketData()
            md.ParseFromString(body)

            # lst = self.id2c[md.idnum]
            lst = self.id2c.get(md.idnum)
            if lst is not None:
                stkinfo = lst[1]
                stkinfo.md = md
            # else:
            #     print('None-None %d' % (md.idnum))

            # print md
        #  返回期货行情数据
        elif cmd == quotation_def_pb2.LYMK_FUTURE:
            md = quota_pb2.MarketDataFutures()
            md.ParseFromString(body)
            print self.id2c[md.idnum]
            # print md
        #  返回指数行情数据
        elif cmd == quotation_def_pb2.LYMK_INDEX:
            md = quota_pb2.IndexData()
            md.ParseFromString(body)
            print self.id2c[md.idnum]
            # print md

        #  代码列表响应
        elif cmd == quotation_def_pb2.LYMK_CODETABLE_RESP:
            md2 = quota_pb2.SecurityCodeResp()
            md2.ParseFromString(body)
            pi.pack = md2
            self.codetable_resp_handle(pi)

        #   代码清单变更
        elif cmd == quotation_def_pb2.LYMK_CODETABLE_CHANGE:
            #  请求代码列表：深证 ：上证 请求期货代码列表
            sub_mkt = [base_pb2.MKT_SZ, base_pb2.MKT_SH, base_pb2.MKT_CF]
            for sm in sub_mkt:
                self.send_codetable(sm)
        #  代码清单增加
        elif cmd == quotation_def_pb2.LYMK_CODETABLE_ADD:
            md = quota_pb2.SecurityCode()
            md.ParseFromString(body)
            pi.pack = md
            self.codetable_add_handle(pi)
        elif quotation_def_pb2.LYMK_MARKET_LIST == cmd:
            # print('LYMK_MARKET_LIST ')
            pass
        #  心跳响应
        elif ((base_pb2.CMD_HEARTBEAT_REQ == pi.cmd or
               base_pb2.CMD_HEARTBEAT_RESP == pi.cmd)):
            self.send_heartbeat(base_pb2.SYS_QUOTATION)
        else:
            print('\033[31mquotation unknow cmd 0x%x\033[0m' % (pi.cmd))

    #  ------------------------------------------------------------------------
    def codetable_add_handle(self, pi):
        scinf = pi.pack
        mkid = scinf.idnum % 100
        stkinfo = StockInfo(scinf.security_code, mkid)
        self.c2id[mkid][str(scinf.security_code)] = [scinf.idnum, stkinfo]
        self.id2c[scinf.idnum] = [scinf.security_code, stkinfo]
        #  请求行情数据（通过本日编号）
        # self.sub_constituent_stock(pi)
        print('+++++++++++ %s %s' % (scinf.security_code, scinf.idnum))

    def codetable_resp_handle(self, pi):
        scrsp = pi.pack
        mkid = scrsp.source
        for scinf in scrsp.security_code_list:
            stkinfo = StockInfo(scinf.security_code, scrsp.source)
            # if 0 == scrsp.source and scinf.security_code == '000027':
            self.c2id[mkid][str(scinf.security_code)] = [scinf.idnum, stkinfo]
            self.id2c[scinf.idnum] = [scinf.security_code, stkinfo]
            # print('c %s id %s' % (scinf.security_code, scinf.idnum))

        self.sub_constituent_stock2(pi)

    def sub_constituent_stock2(self, pi):
        if self.pre_quo is None:
            return

        etfs = self.pre_quo.etfs
        print('sub cnst stock %s len(etfs) %d' % (type(etfs), len(etfs)))
        # ecode == etf_code
        # isinstance(etf, EtfInfo)
        pack = pi.pack
        mkid = pack.source
        for ecode, etf in etfs.items():
            # print ecode, etf
            self.sub_etf_constituent(mkid, etf)

    def sub_etf_constituent(self, mkid, etf):
        etf.stcks[mkid] = []
        for stk_etf in etf.etf_base_info.etf_list:
            if stk_etf.stock_id in self.c2id[mkid]:
                lst = self.c2id[mkid][stk_etf.stock_id]
                if lst[1].mkid != mkid:
                    print('mkid <> %s %d %d' %
                          (lst[1].stkcode, lst[1].mkid, mkid))
                #  stkinf = lst[1]
                lst[1].qty[etf.etfcode] = stk_etf.execute_qty
                etf.stcks[mkid].append(lst[1])  # list version

    def try_get_id(self, scode):
        for mkid in base_pb2.market_id.values():
            try:
                sid = self.c2id[mkid].get(scode, None)
                if sid is not None:
                    return mkid, sid
            except:
                continue

        return -1, None

    def try_send(self, pack, cmd):
        fmt = ">iHHiiii"
        headbuffer = struct.pack(fmt, pack.ByteSize(), base_pb2.SYS_QUOTATION,
                                 cmd, base_pb2.SYS_QUOTATION, 0, 0, self.seq)
        self.seq += 1
        snddata = headbuffer + pack.SerializeToString()

        return self.send_package(snddata)

    # --------------------------------------------------------------------
    def update_knock_info(self, stkcode, mkid, opr, volume):
        try:
            stkinfo = self.c2id[mkid][stkcode][1]
        except Exception, e:
            print e
        else:
            if base_pb2.OPR_BUY == opr:
                stkinfo.buy += volume
            elif base_pb2.OPR_SELL == opr:
                stkinfo.sell += volume
            elif base_pb2.OPR_PURCHASE == opr:
                stkinfo.purchase += volume
            elif base_pb2.OPR_REDEEM == opr:
                stkinfo.redeem += volume
            else:
                print('unknow operatione 0x%x' % (opr))

            print('%s trns %r code %s opr 0x%x b %d s %d p %d r %d m %d%s' %
                  (BLUE, stkinfo, stkinfo.stkcode,
                   opr, stkinfo.buy, stkinfo.sell,
                   stkinfo.purchase, stkinfo.redeem, volume,
                   CLEAR))


# -----------------------------------------------------------------------------
class RobotApp(object):
    '''
    this is a robot
    '''
    # map robotapp.seq <==> (client, req_seq)

    cfg = None  # config
    quo = None  # quotation stock server
    # q_f_sock = None  # quotation future server
    pre_quo = None  # quotation pre stock server
    # q_p_f_sock = None  # quotation pre future server

    def __init__(self, conf):
        with open('robot.yaml') as f:
            import yaml
            self.cfg = yaml.load(f)


#  ----------------------------------------------------------------------------
def main():
    jobs = []
    rapp = RobotApp('robot.yaml')
    q_ip = rapp.cfg['quo_server']['qip']
    q_port = rapp.cfg['quo_server']['port']
    print q_ip, q_port
    quota = Quotation(rapp, (q_ip, q_port))
    rapp.quo = quota
    jobs.append(gevent.spawn(quota.recv_data))
    gevent.joinall(jobs)

    while 1:
        print('s' * 60)
        gevent.sleep(10)


if __name__ == '__main__':
    main()
