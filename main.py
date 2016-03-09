#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" main entry
"""

import gevent

from core import robot
# import rserver
from quota import pre_quotation, quotation
# import riskmgt
# import quota_pb2
# import pq_quota_pb2
# import time


from net import riskmgt

# import stock_def


__author__ = 'qinjing'


# -----------------------------------------------------------------------------
def timer_proc():
    while 1:
        gevent.sleep(1)
        # print('timer proc %s ' % (time.ctime(time.time())))


# -----------------------------------------------------------------------------
def main():
    print 'robot ver. %s' % robot.ROBOT_VER
    rapp = robot.RobotApp('robot.yaml')
    jobs = []

    pq_ip = rapp.cfg['pre_quo']['pqip']
    pq_port = rapp.cfg['pre_quo']['port']
    print pq_ip, pq_port
    pre_quo = pre_quotation.PreQuotation(rapp, (pq_ip, pq_port))
    rapp.pre_quo = pre_quo

    q_ip = rapp.cfg['quo_server']['qip']
    q_port = rapp.cfg['quo_server']['port']
    print q_ip, q_port
    quota = quotation.Quotation(rapp, (q_ip, q_port))
    rapp.quo = quota

    # stock_ip = rapp.cfg['stocksvr']['sip']
    # stock_port = rapp.cfg['stocksvr']['port']
    # print stock_ip, stock_port
    # stock_svr = stock_conn.StackConn(rapp, (stock_ip, stock_port),
    #                                  rapp.stock_handler)
    # rapp.stock_sock = stock_svr

    riskip = rapp.cfg['risksvr']['rip']
    riskport = rapp.cfg['risksvr']['rport']
    rskmgt = riskmgt.RiskMgt(rapp, (riskip, riskport), rapp.risk_handle)
    rapp.riskmgt = rskmgt

    jobs.append(gevent.spawn(rapp.svr.serve_forever, rapp))

    jobs.append(gevent.spawn(rapp.riskmgt.recv_data))

    jobs.append(gevent.spawn(pre_quo.recv_data))
    jobs.append(gevent.spawn(quota.recv_data))
    # jobs.append(gevent.spawn(stock_svr.recv_data))
    jobs.append(gevent.spawn(timer_proc))
    gevent.joinall(jobs)


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    main()
