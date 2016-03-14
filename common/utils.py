#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
helper function
"""

# import sys
import struct
import time
import uuid
from gevent import socket
import gevent

from dao.datatype import package_info
from pb import base_pb2, error_pb2

__author__ = 'qinjing'


# ---------------------------------------------------------------------------
def connect_server(addr):
    i = 2
    while 1:
        try:
            svr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            svr.connect(addr)
            break
        except:
            gevent.sleep(i)
            i = i * 2
            if i >= 32:
                i = 2

    return svr


# -----------------------------------------------------------------------------
def int2seq(s1, s2, s3, s4):
    ssss = '%04x%04x%04x%04x' % (s1, s2, s3, s4)
    return ssss


# --------------------------------------------------------------------------
def make_package(sysid, cmd, rid, pack):
    fmt = ">iHH16s"
    head = struct.pack(fmt, pack.ByteSize(), sysid, cmd, rid.get_bytes())
    snddata = head + pack.SerializeToString()
    return snddata

# -----------------------------------------------------------------------------
def make_package_num(sysid, cmd, s3, s4, pack):
    fmt = ">iHHiiii"
    head = struct.pack(fmt, pack.ByteSize(), sysid, cmd, 0, 0, s3, s4)
    snddata = head + pack.SerializeToString()
    return snddata


# -----------------------------------------------------------------------------
def recv_header2(sock, size):
    header = ''
    while len(header) < size:
        try:
            hpdata = sock.recv(size - len(header))
        except Exception, e:
            print('except %s' % (e))
            break
        if not hpdata:
            gevent.sleep(0)
            print 'no header'
            break
        header += hpdata

    if len(header) == size:
        fmt = '>iHH16s'
        blen, sysid, cmd, rid = struct.unpack(fmt, header)
        pi = package_info(cmd, rid)
        return error_pb2.SUCCESS, blen, pi
    else:
        return error_pb2.ERROR_DISCONNECT, 0, None


# --------------------------------------------------------------------------
def recv_header(sock, size):
    header = ''
    while len(header) < size:
        hpdata = sock.recv(size - len(header))
        if not hpdata:
            print 'no header'
            break
        header += hpdata

    if len(header) == size:
        fmt = '>iHH16s'
        blen, sysid, cmd, rid = struct.unpack(fmt, header)
        return error_pb2.SUCCESS, blen, sysid, cmd, rid
    else:
        return error_pb2.ERROR_DISCONNECT, 0, 0, 0, 0


# -----------------------------------------------------------------------------
def recv_body(sock, size):
    body = ''
    while len(body) < size:
        bpdata = sock.recv(size - len(body))
        if not bpdata:
            print 'no body'
            break
        body += bpdata

    if len(body) == size:
        return error_pb2.SUCCESS, body
    else:
        return error_pb2.ERROR_DISCONNECT, body


# -----------------------------------------------------------------------------
def get_policy_id(rid, code, count, opr):
    tm = '%.06f' % time.time()
    pidm = '%s%s%04d%02d%s' % (rid, code, count, opr,
                               tm[-12:-7])
    pid = '%s:%s%s' % (pidm, tm[-12:-7], tm[-6:])

    return pidm.encode('ascii'), pid.encode('ascii')


# -----------------------------------------------------------------------------
def get_policy_id_sub(self, key):
    tm = '%.06f' % time.time()
    pid = '%s:%s%s' % (key, tm[-12:-7], tm[-6:])

    return pid.encode('ascii')


# -----------------------------------------------------------------------------
def policy2key(self, policyid):
    key = policyid[:23]
    return key
