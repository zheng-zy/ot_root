#!/usr/bin/env python
# -*- coding: utf-8 -*-


""" a robot
"""


import gevent
# from gevent import socket
import struct
import time
from net import baseclient

from dao.stock_def import EtfInfo

from pb import base_pb2
from pb import error_pb2
from pb import pq_quota_pb2
from pb import quotation_def_pb2
from pb import quota_pb2

import quotation


__author__ = 'qinjing'


RED = '\033[31m'
GREEN = '\033[32m'
BLUE = '\033[33m'
CLEAR = '\033[0m'


# -----------------------------------------------------------------------------
# class PreQuotation(object):
#     def __init__(self, app, addr):
#         self.addr = addr
#         # self.app = app
#         self.pre_quo_svr = utils.connect_server(addr)
#         self.subscibe()
#         self.etfs = {}
#
#     def subscibe(self):
#         print('subscibe')
#         submsg = pq_quota_pb2.PreQuoSubMsg()
#         submsg.sub_flag = 1
#         submsg.sub_type.append(quotation_def_pb2.LYMK_ETF_BASE_INFO)
#         # submsg.sub_type.append(quotation_def_pb2.LYMK_MARKET_OVERVIEW)
#         # submsg.sub_type.append(quotation_def_pb2.LYMK_ETF_DIFF_INFO)
#         # submsg.sub_type.append(quotation_def_pb2.LYMK_FJJJ_INFO)
#         # submsg.sub_type.append(quotation_def_pb2.LYMK_STRUCTURED_FUND_BASE)
#         # submsg.sub_type.append(quotation_def_pb2.LYMK_TRADEDAY_INFO)
#         fmt = ">iHHiiii"
#
#         headbuffer = struct.pack(fmt, submsg.ByteSize(), 0x8001,
#                                  quotation_def_pb2.LYMK_PRE_QUO_SUB, 0, 0, 0,
#                                  0)
#         sentdata = headbuffer + submsg.SerializeToString()
#         self.pre_quo_svr.send(sentdata)
#
#     def recv_data(self):
#         MAX_PACK = 1024 * 1024
#         fmt = ">iHHiiii"
#         seq = 0
#         maxpack = 1
#         while 1:
#             status, packlen, pi = utils.recv_header2(
#                 self.pre_quo_svr, base_pb2.HEADER_SIZE)
#             if error_pb2.SUCCESS != status:
#                 print('\033[31mreconnect..\033[0m')
#                 self.pre_quo_svr = utils.connect_server(self.addr)
#                 self.subscibe()
#                 continue
#
#             if packlen < 0 or packlen > MAX_PACK:
#                 print 'close connect error length', packlen
#                 self.pre_quo_svr = utils.connect_server(self.addr)
#                 self.subscibe()
#                 continue
#
#             if maxpack < packlen:
#                 maxpack = packlen
#             # 获取包体 收全包体
#             body = ''
#             status, body = utils.recv_body(self.pre_quo_svr, packlen)
#             if error_pb2.SUCCESS != status:
#                 print('\033[31mRecv %d %d\033[0m' % (packlen, len(body)))
#                 print('reconnect...')
#                 self.pre_quo_svr = utils.connect_server(self.addr)
#                 self.subscibe()
#                 continue
#
#             if quotation_def_pb2.LYMK_ETF_BASE_INFO == pi.cmd:
#                 etfbase = pq_quota_pb2.EtfBasketInfo()
#                 etfbase.ParseFromString(body)
#                 pi.pack = etfbase
#                 print etfbase
#                 self.etf_base_info_handle(pi)
#             elif quotation_def_pb2.LYMK_HEARTBEAT_REQ == pi.cmd:
#                 headbuffer = struct.pack(
#                     fmt, 0, 0x8001, quotation_def_pb2.LYMK_HEARTBEAT,
#                     1, 0, 0, 0)
#                 seq += 1
#                 self.pre_quo_svr.send(headbuffer)
#                 print('%s etfs %d maxpack %d' % (time.ctime(time.time()),
#                       len(self.etfs), maxpack))
#             else:
#                 print('unknow cmd 0x%x' % (pi.cmd))
#
#     def etf_base_info_handle(self, pi):
#         self.etfs[pi.pack.etf_code] = pi.pack
#         if pi.pack.etf_code == '159919':
#             pi.pack
# #             print('%s pi.pack.creation_limit %s pi.redemption_limit %s'
# #                   % (pi.pack.etf_code, pi.pack.creation_limit,
# #                      pi.pack.redemption_limit))
#
#         # print pi
#         # print pi.pack


# -----------------------------------------------------------------------------
class PreQuotation(baseclient.BaseClient):
    def __init__(self, app, addr):
        super(PreQuotation, self).__init__(app, addr)
        self.etfs = {}
        self.quo = self.app.quo
        self.seq = 0
        self.sublist = []
        self.log = open('etf.code', 'w+')

    def after_connect(self, err):
        submsg = pq_quota_pb2.PreQuoSubMsg()
        submsg.sub_flag = 1
        submsg.sub_type.append(quotation_def_pb2.LYMK_ETF_BASE_INFO)

        submsg.sub_type.append(quotation_def_pb2.LYMK_MARKET_OVERVIEW)
        submsg.sub_type.append(quotation_def_pb2.LYMK_ETF_DIFF_INFO)
        submsg.sub_type.append(quotation_def_pb2.LYMK_FJJJ_INFO)
        submsg.sub_type.append(quotation_def_pb2.LYMK_STRUCTURED_FUND_BASE)
        # submsg.sub_type.append(quotation_def_pb2.LYMK_TRADEDAY_INFO)
        fmt = ">iHHiiii"

        headbuffer = struct.pack(fmt, submsg.ByteSize(), 0x8001,
                                 quotation_def_pb2.LYMK_PRE_QUO_SUB, 0, 0, 0,
                                 0)
        sentdata = headbuffer + submsg.SerializeToString()
        self.svr_sock.sendall(sentdata)

    def package_handle(self, packlen, pi, body):
        # print('pre quo cmd 0x%x' % (pi.cmd))
        if quotation_def_pb2.LYMK_ETF_BASE_INFO == pi.cmd:
            # print('LYMK_ETF_BASE_INFO')
            etfbase = pq_quota_pb2.EtfBasketInfo()
            etfbase.ParseFromString(body)
            pi.pack = etfbase
            self.etf_base_info_handle(pi)
        elif ((base_pb2.CMD_HEARTBEAT_REQ == pi.cmd or
               base_pb2.CMD_HEARTBEAT_RESP == pi.cmd)):
            # print('LYMK_HEARTBEAT_REQ ')
            self.send_heartbeat(base_pb2.SYS_QUOTATION)
            # fmt = ">iHHiiii"
            # headbuffer = struct.pack(
            #     fmt, 0, 0x8001, base_pb2.CMD_HEARTBEAT_RESP, 1,
            #     0, 0, 0)
            # self.svr_sock.sendall(headbuffer)
        elif quotation_def_pb2.LYMK_STRUCTURED_FUND_BASE == pi.cmd:
            # print('LYMK_STRUCTURED_FUND_BASE')
            pack = pq_quota_pb2.StructuredFundInfo()
            pack.ParseFromString(body)
            pi.pack = pack
        elif quotation_def_pb2.LYMK_FJJJ_INFO == pi.cmd:
            # print('LYMK_FJJJ_INFO')
            pack = pq_quota_pb2.StructuredFundInfo()
            pack.ParseFromString(body)
            pi.pack = pack
        elif quotation_def_pb2.LYMK_MARKET_OVERVIEW == pi.cmd:
            # print('LYMK_MARKET_OVERVIEW')
            pack = pq_quota_pb2.MarketDaily()
            pack.ParseFromString(body)
            pi.pack = pack
            # print('quotation_def_pb2.LYMK_STRUCTURED_FUND_BASE == pi.cmd')
            # print pack
        elif quotation_def_pb2.LYMK_ETF_DIFF_INFO == pi.cmd:
            pass
        else:
            print('pre quo unknow cmd 0x%x' % (pi.cmd))

    def etf_base_info_handle(self, pi):
        etfinfo = EtfInfo(pi.pack.etf_code)
        self.etfs[pi.pack.etf_code] = etfinfo
        etfinfo.etf_base_info = pi.pack
        # print('etfcode %s' % (etfinfo.etfcode))
        # if '159919' == pi.pack.etf_code:
        #     print('%s type(pi.pack.etf_code) %s %s' %
        #           (RED, type(pi.pack.etf_code), CLEAR))
        # print('%s len(pro_quo.etfs) %d' %
        #       (time.ctime(time.time()), len(self.etfs)))
        # print pi.pack
        # print pi.pack.etf_code, pi.pack.creation_redemption_unit
        if '510050' == pi.pack.etf_code:
            # print pi.pack
            pass
        ret = self.sub_constituent_stock(etfinfo)
        if ret != 0:
            self.sublist.append(etfinfo)
        else:
            for etfinf in self.sublist:
                ret = self.sub_constituent_stock(etfinf)
                if ret != 0:
                    print('err ret %d' % (ret))
                    break
                else:
                    pass
                    # print('sub ret %d' % (ret))

    def get_etf(self, etfcode):
        return self.etfs.get(etfcode)

    def sub_constituent_stock(self, etfinfo):
        if self.quo is None:
            self.quo = self.app.quo
            print('pre quotation re set quo')
        if self.quo is None:
            print('pre quotation re set quo 1 %s' % (etfinfo.etfcode))
            return 1
        if len(self.quo.c2id) < 1:
            # print('pre quotation re set quo 2 %s' % (etfinfo.etfcode))
            return 2

        # if '159919' == etfinfo.etfcode:
        #     print('%spre %s sub stock %s' % (RED, etfinfo.etfcode, CLEAR))
        # ecode == etf_code
        # isinstance(etf, EtfInfo)
        # print ecode, etf

        # etfinfo.stcks[base_pb2.MKT_SZ] = []
        # etfinfo.stcks[base_pb2.MKT_SH] = []
        # etfinfo.stcks[base_pb2.MKT_CF] = []
        for stk_etf in etfinfo.etf_base_info.etf_list:
            # if '300251' == stk_etf.stock_id:
            #     print('%ssub 300251 %s' % (RED, CLEAR))
            self.log.write('%s    %s\n' % (etfinfo.etfcode, stk_etf.stock_id))
            if stk_etf.stock_id in self.quo.c2id:
                lst = self.quo.c2id[stk_etf.stock_id]

                lst[1].qty = stk_etf.execute_qty
                etfinfo.stcks[lst[1].mkid].append(lst[1])  # list version
                # dict ver
                # etf.stcks[pack.source][stk_etf.stock_id] = lst[1]
                #  sid = lst[0]
                md = quota_pb2.MarketDataReqByIdnum()
                md.sub_type = 1
                md.idnum.append(lst[0])
                # if stk_etf.stock_id == '000001':
                #     print '000001 in', ecode, lst[1], lst[0]
                self.quo.try_send(
                    md, quotation_def_pb2.LYMK_MARKETDATA_REQ_BY_IDNUM)

        self.log.write('\n')
        return 0

    def try_send(self, pack, cmd):
        fmt = ">iHHiiii"
        headbuffer = struct.pack(fmt, pack.ByteSize(), base_pb2.SYS_QUOTATION,
                                 cmd, base_pb2.SYS_QUOTATION, 0, 0, self.seq)
        self.seq += 1
        sentdata = headbuffer + pack.SerializeToString()
        return self.svr_sock.send(sentdata)


# -----------------------------------------------------------------------------
class RobotApp(object):
    '''
    this is a robot
    '''
    rid = '100001'
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

    def timer_proc(self):
        # one = '000001'
        while 1:
            gevent.sleep(5)
            for key, etf in self.pre_quo.etfs.items():
                assert isinstance(etf, EtfInfo)
                if len(etf.stcks[base_pb2.MKT_SZ]) > 0:
                    print etf.stcks[base_pb2.MKT_SZ][0]
                    print etf.stcks[base_pb2.MKT_SZ][0].md
            print('pre quo %s' % (time.ctime(time.time())))


# -----------------------------------------------------------------------------
def timer_proc(rapp):
    # one = '000001'
    while 1:
        gevent.sleep(5)
        for key, etf in rapp.pre_quo.etfs.items():
            assert isinstance(etf, EtfInfo)
            if len(etf.stcks[base_pb2.MKT_SZ]) > 0:
                print etf.stcks[base_pb2.MKT_SZ][0]
                print etf.stcks[base_pb2.MKT_SZ][0].md

            # if ((one in etf.stcks[base_pb2.MKT_SZ] or
            #      one in etf.stcks[base_pb2.MKT_SH] or
            #      one in etf.stcks[base_pb2.MKT_CF])):
            #     stkinfo = etf.stcks[base_pb2.MKT_SZ][one]
            #     print(stkinfo)
            #     print stkinfo.md
            # print('%d %s %s' % (len(rapp.pre_quo.etfs),
            #       key, type(etf.stcks[base_pb2.MKT_SZ])))
            # print('etf.stcks[base_pb2.MKT_SZ] %d' %
            #       (len(etf.stcks[base_pb2.MKT_SZ])))
            # print('etf.stcks[base_pb2.MKT_SH] %d' %
            #       (len(etf.stcks[base_pb2.MKT_SH])))
            # print('etf.stcks[base_pb2.MKT_CF] %d' %
            #       (len(etf.stcks[base_pb2.MKT_CF])))


# -----------------------------------------------------------------------------
def main():
    print('begin %s ' % (time.ctime(time.time())))
    rapp = RobotApp('robot.yaml')
    jobs = []

    pq_ip = rapp.cfg['pre_quo']['pqip']
    pq_port = rapp.cfg['pre_quo']['port']
    print pq_ip, pq_port
    pre_quo = PreQuotation(rapp, (pq_ip, pq_port))
    rapp.pre_quo = pre_quo
    jobs.append(gevent.spawn(pre_quo.recv_data))
    # gevent.sleep(3)

    q_ip = rapp.cfg['quo_server']['qip']
    q_port = rapp.cfg['quo_server']['port']
    print q_ip, q_port
    quota = quotation.Quotation(rapp, (q_ip, q_port))
    rapp.quo = quota

    jobs.append(gevent.spawn(quota.recv_data))
    gevent.sleep(3)
    jobs.append(gevent.spawn(rapp.timer_proc))
    gevent.joinall(jobs)

    while 1:
        print 's' * 60
        gevent.sleep(10)


if __name__ == '__main__':
    main()
