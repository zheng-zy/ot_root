#!/usr/bin/env python
# -*- coding: utf-8 -*-


""" global data
"""

import struct
import time
import gevent
from gevent.server import StreamServer
import yaml
from common import utils
from dao.datatype import package_info, Sesstion
from pb import base_pb2, ot_pb2, stock_trade_pb2, trade_db_model_pb2, error_pb2
from common import timeUtils
import uuid
from trans.structured_fund_trans import *
from trans.sf_combine_trans import *
from common import constant

VERSION = base_pb2.MAJOR << 16 or base_pb2.MINOR

RED = '\033[31m'
GREEN = '\033[32m'
BLUE = '\033[33m'
CLEAR = '\033[0m'

ROBOT_VER = '0.0.1a'


# -----------------------------------------------------------------------------
class RobotApp(object):
    '''
    this is a robot
    '''
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
    clients = {}  # dict of client sessions
    sessions = {}
    sub_sessions = []
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

    # ------------------------------------------------------------------------
    def client_package_handle(self, cmd, rid, body, sess):
        print '%sclient request,cmd: [0x%x] rid: [%s]%s ' % (BLUE, cmd, uuid.UUID(bytes=rid), CLEAR)
        if base_pb2.CMD_SUBSCRIBE_POLICY_REQ == cmd:
            print '%sCMD_SUBSCRIBE_POLICY_REQ%s' % (GREEN, CLEAR)
            pack = ot_pb2.SubscribePolicyRequest()
            pack.ParseFromString(body)
            pi = package_info(cmd, rid, pack, sess)
            self.cmd_subscribe_policy_req(pi)
        elif base_pb2.CMD_STOCK_POLICY == cmd:
            print '%sCMD_STOCK_POLICY%s' % (GREEN, CLEAR)
            pack = ot_pb2.StockPolicy()
            pack.ParseFromString(body)
            pi = package_info(cmd, rid, pack, sess)
            self.cmd_stock_policy(pi)
        elif base_pb2.CMD_STOP_POLICY == cmd:
            print '%sCMD_STOP_POLICY%s' % (GREEN, CLEAR)
            pack = ot_pb2.StopPolicy()
            pack.ParseFromString(body)
            pi = package_info(cmd, rid, pack, sess)
            self.cmd_stop_policy(pi)
        elif base_pb2.CMD_STOCK_CREATE_OR_REDEEM_POLICY == cmd:
            print '%sCMD_STOCK_CREATE_OR_REDEEM_POLICY%s' % (GREEN, CLEAR)
            c_or_r_policy = ot_pb2.StockCreateOrRedeemPolicy()
            c_or_r_policy.ParseFromString(body)
            pi = package_info(cmd, rid, c_or_r_policy, sess)
            self.cmd_stock_create_or_redeem_policy(pi)
        elif base_pb2.CMD_STRUCTURED_FUND_SPLIT_OR_MERGE_POLICY == cmd:
            print '%sCMD_STRUCTURED_FUND_SPLIT_OR_MERGE_POLICY%s' % (GREEN, CLEAR)
            s_or_m_policy = ot_pb2.StructuredFundSplitOrMergePolicy()
            s_or_m_policy.ParseFromString(body)
            pi = package_info(cmd, rid, s_or_m_policy, sess)
            self.cmd_structured_fund_split_or_merge_policy(pi)
        elif base_pb2.CMD_STRUCTURED_FUND_LINK_POLICY == cmd:
            print '%sCMD_STRUCTURED_FUND_LINK_POLICY%s' % (GREEN, CLEAR)
            policy = ot_pb2.StructuredFundLinkPolicy()
            policy.ParseFromString(body)
            pi = package_info(cmd, rid, policy, sess)
            self.cmd_structured_fund_link_policy(pi)
            # if policy.base_param.direction == 0:
            #     policy_pb = self.pool.execPolicy('StructuredFundLinkBuyPolicy', pi)
            # elif policy.base_param.direction == 1:
            #     policy_pb = self.pool.execPolicy('StructuredFundLinkSalePolicy', pi)
            # print 'robot deal policy StructuredFundLinkPolicy result: [%s]' % policy_pb
            # policy_pb.time_stamp = timeUtils.getCurrentTotalMSeconds()
            # snddata = utils.make_package(base_pb2.SYS_ROBOT, base_pb2.CMD_POLICY_STATUS, pi.rid, policy_pb)
            # session = self.sessions.get(policy_pb.trader_id)
            # session.sock.send(snddata)
        elif base_pb2.CMD_STRUCTURED_FUND_AB_POLICY == cmd:
            print 'CMD_STRUCTURED_FUND_AB_POLICY'
            policy = ot_pb2.StructuredFundABPolicy()
            policy.ParseFromString(body)
            pi = package_info(cmd, rid, policy, sess)
            self.cmd_structured_fund_ab_policy(pi)
            # if policy.base_param.direction == 0:
            #     policy_pb = self.pool.execPolicy('StructuredFundABBuyPolicy', pi)
            # elif policy.base_param.direction == 1:
            #     policy_pb = self.pool.execPolicy('StructuredFundABSalePolicy', pi)
            # print 'robot deal policy StructuredFundABPolicy result: [%s]' % policy_pb
            # policy_pb.time_stamp = timeUtils.getCurrentTotalMSeconds()
            # snddata = utils.make_package(base_pb2.SYS_ROBOT, base_pb2.CMD_POLICY_STATUS, pi.rid, policy_pb)
            # session = self.sessions.get(policy_pb.trader_id)
            # session.sock.send(snddata)
        else:
            print('unknow cmd %x' % cmd)

    # ------------------------------------------------------------------------
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
                base_pb2.SYS_ROBOT, base_pb2.CMD_LOGIN_RESP, pi.rid, login_resp)
        sess.send_package(snddata)
        return sess
        # socket.send(snddata)

    # -------------------------------------------------------------------------
    def login_resp_handle(self, login_resp):
        """ login resp
        """
        print 'login risk success, login_resp: [%s]' % login_resp
        pass

    # ------------------------------------------------------------------------
    def new_session(self, clnt_s, address):
        print('New connection from %s:%s' % address)
        sess = None
        MAX_PACK = 1024 * 1024
        login_flag = -1
        while True:
            status, packlen, sysid, cmd, rid = utils.recv_header(
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
                body += bpdata
            if len(body) != packlen:
                break
            if base_pb2.SYS_ROBOT == sysid:
                if base_pb2.CMD_LOGIN_REQ == cmd:
                    lgn = base_pb2.LoginReq()
                    lgn.ParseFromString(body)
                    pi = package_info(cmd, rid, lgn)
                    sess = self.login_handle(clnt_s, pi)
                    login_flag = sess.login
                elif error_pb2.SUCCESS == login_flag:
                    status = self.client_package_handle(cmd, rid, body, sess)
                else:
                    print 'login first'
            else:
                break

        if sess is not None:
            sess.close()
        print ('disconnect close socket remain sesses %d' % len(self.sessions))
        self.sessions.pop(sess.tid)

    # ---------------------------------------------------------------------
    def risk_handle(self, packlen, pi, body):
        cmd = pi.cmd
        if base_pb2.CMD_LOGIN_RESP == cmd:
            print'\033[32mCMD_LOGIN_RESP \033[0m'
            login_resp = base_pb2.LoginResp()
            login_resp.ParseFromString(body)
            pi.pack = login_resp
            self.login_resp_handle(login_resp)
        elif base_pb2.CMD_SUBSCRIBE_TRADE_RESP == cmd:
            print'\033[32mCMD_SUBSCRIBE_TRADE_RESP \033[0m'
            sub_resp = stock_trade_pb2.SubTradeMsgResponse()
            sub_resp.ParseFromString(body)
            print 'sub risksvr success, sub_resp: [%s]' % sub_resp
        elif base_pb2.CMD_SINGLE_ORDER_RESP == cmd:
            print('\033[32mCMD_SINGLE_ORDER_RESP\033[0m')
            pack = stock_trade_pb2.SingleOrderResp()
            pack.ParseFromString(body)
            pi.pack = pack
            self.cmd_single_order_resp(pi)
        elif base_pb2.CMD_SINGLE_WITHDRAWAL_RESP == cmd:
            print('\033[32mCMD_SINGLE_WITHDRAWAL_RESP\033[0m')
            pack = stock_trade_pb2.SingleOrderResp()
            pack.ParseFromString(body)
            pi.pack = pack
            self.cmd_single_withdrawal_resp(pi)
            # policy_pb = self.pool.onCancelSubmitSuccess(pi)
            # policy_pb.time_stamp = timeUtils.getCurrentTotalMSeconds()
            # snddata = utils.make_package(base_pb2.SYS_ROBOT, base_pb2.CMD_POLICY_STATUS, pi.rid, policy_pb)
            # session = self.sessions.get(policy_pb.trader_id)
            # session.sock.send(snddata)
            # print sw_resp
        elif base_pb2.CMD_SUB_STOCK_KNOCK_REQ == cmd:
            print('\033[32mCMD_SUB_STOCK_KNOCK_REQ  \033[0m')
            pack = stock_trade_pb2.QueryStockKnockResponse()
            pack.ParseFromString(body)
            # print 'pack: [%s]' % pack
            pi.pack = pack
            self.cmd_sub_stock_knock_req(pi)
        elif base_pb2.CMD_ERROR_REQ == cmd:
            err = stock_trade_pb2.ErrResp()
            err.ParseFromString(body)
            print('risk handle %s %s' % (err.ret_code, err.ret_message))
        elif base_pb2.CMD_SUB_ASSET_REQ == cmd:
            pass
        elif base_pb2.CMD_SUB_STOCK_POSITION_REQ == cmd:
            pack = stock_trade_pb2.QueryPositionResponse()
            pack.ParseFromString(body)
            pi.pack = pack
        elif base_pb2.CMD_SUB_STOCK_ORDER_REQ == cmd:
            print(' risk  CMD_SUB_STOCK_ORDER_REQ :')
            pass
        elif base_pb2.CMD_HEARTBEAT_REQ == pi.cmd:
            fmt = ">iHHiiii"
            headbuffer = struct.pack(
                    fmt, 0, base_pb2.SYS_RISK, base_pb2.CMD_HEARTBEAT_RESP, 1,
                    0, 0, 0)
            self.riskmgt.svr_sock.sendall(headbuffer)
        else:
            print('\033[32mrisk_handle unknow cmd 0x%x \033[0m' % (cmd))
        return error_pb2.SUCCESS

    def cmd_subscribe_policy_req(self, pi):
        pack = ot_pb2.SubscribePolicyResponse()
        pack.result.time_stamp = timeUtils.getCurrentTotalMSeconds()
        pack.result.code = 0
        pack.result.reason = ''
        snddata = utils.make_package(base_pb2.SYS_ROBOT, base_pb2.CMD_SUBSCRIBE_POLICY_RESP, pi.rid, pack)
        pi.sess.send_package(snddata)
        self.sub_sessions.append(pi.sess)

    def cmd_stock_policy(self, pi):
        if pi.pack.base_param.direction is 0:
            # pidm, pid = self.get_policy_id(pack.base_param.direction, pi.pack.code)
            pid = str(uuid.uuid1(self.get_seq()))
            ts = TranStructureFundBuy(self, pid, pi)
            ts.execute()
        elif pi.pack.base_param.direction is 1:
            pid = str(uuid.uuid1(self.get_seq()))
            ts = TranStructureFundSale(self, pid, pi)
            ts.execute()
            pass

    def cmd_stock_create_or_redeem_policy(self, pi):
        if pi.pack.base_param.direction is 0:
            pid = str(uuid.uuid1(self.get_seq()))
            ts = TranStructureFundPurchase(self, pid, pi)
            ts.execute()
        elif pi.pack.base_param.direction is 1:
            pid = str(uuid.uuid1(self.get_seq()))
            ts = TranStructureFundRedeem(self, pid, pi)
            ts.execute()

    def cmd_structured_fund_split_or_merge_policy(self, pi):
        if pi.pack.base_param.direction is 0:
            pid = str(uuid.uuid1(self.get_seq()))
            ts = TranStructureFundCombine(self, pid, pi)
            ts.execute()
        elif pi.pack.base_param.direction is 1:
            pid = str(uuid.uuid1(self.get_seq()))
            ts = TranStructureFundSplit(self, pid, pi)
            ts.execute()

    def cmd_structured_fund_link_policy(self, pi):
        if pi.pack.base_param.direction is 0:
            pid = str(uuid.uuid1(self.get_seq()))
            ts = TranStructureFundLinkBuy(self, pid, pi)
            ts.execute()
        elif pi.pack.base_param.direction is 1:
            pid = str(uuid.uuid1(self.get_seq()))
            ts = TranStructureFundSale(self, pid, pi)
            ts.execute()

    def cmd_structured_fund_ab_policy(self, pi):
        if pi.pack.base_param.direction is 0:
            pid = str(uuid.uuid1(self.get_seq()))
            ts = TranStructureFundABBuy(self, pid, pi)
            ts.execute()
        elif pi.pack.base_param.direction is 1:
            pid = str(uuid.uuid1(self.get_seq()))
            ts = TranStructureFundABSale(self, pid, pi)
            ts.execute()

    def cmd_stop_policy(self, pi):
        ts = self.get_transaction(pi.pack.policy_id)
        ts.cancel()

    def cmd_single_order_resp(self, pi):
        ts = self.get_transaction(pi.pack.policy_id)
        if ts is None:
            print 'cannot find trans in seqclnts dict.'
        if pi.pack.ret_code is 0:
            ps = ts.succeed(pi)
        else:
            ps = ts.failed(pi)

    def cmd_single_withdrawal_resp(self, pi):
        ts = self.get_transaction(pi.pack.policy_id)
        if ts is None:
            print 'cannot find trans in seqclnts dict.'
        if pi.pack.ret_code is 0:
            ps = ts.cancel_submit(pi)

    def cmd_sub_stock_knock_req(self, pi):
        """订阅的成交回报处理"""
        if pi.pack.ret_code is not 0 and len(pi.pack.stock_knock) > 0:
            print 'cmd_sub_stock_knock_req error ret_code: [%s] ret_message: [%s]' % (
                pi.pack.ret_code, pi.pack.ret_message)
            return
        policy_id = pi.pack.stock_knock[0].policy_id
        ts = self.get_transaction(policy_id)
        if ts is None:
            return
        ts.knock(pi)
