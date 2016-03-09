#!/usr/bin/env python
# coding:utf-8
# Author:   --<>
# Purpose: 
# Created: 2012-1-12
# Updated: 2012-1-12

import sys
import unittest
import time
import datetime

ISOTIMEFORMAT = '%Y-%m-%d %X'


# ----------------------------------------------------------------------
def getCurentTotalMicroseconds():
    """得到总的毫秒数 str"""
    return str(int(time.time()))


# ----------------------------------------------------------------------
def getCurrentTotalMSeconds():
    """"""
    return int(time.time() * 1000)


# ----------------------------------------------------------------------
def getCurentMicroseconds():
    """得到总的毫秒数 float"""
    return time.time()


# ----------------------------------------------------------------------
def getThisTimeMicrosecondString():
    """
    Get this time micros
    """
    mscond = datetime.datetime.now().microsecond
    s = '%0.3f' % (mscond / 1000000.0)
    return s[1:]


# ----------------------------------------------------------------------
def fromSecondsToHMS(seconds):
    """from seconds to Hour:Minute:Sencond"""
    seconds = int(seconds)
    seconds_per_hour = 60 * 60
    seoncds_per_minute = 60
    hour = seconds / seconds_per_hour
    minute = (seconds % seconds_per_hour) / seoncds_per_minute
    second = seconds % seconds_per_hour % seoncds_per_minute
    return '%s:%s:%s' % (hour, minute, second)


# ----------------------------------------------------------------------
def getISODateTimeFromMicroseconds(ms):
    """"""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(ms)))


# ----------------------------------------------------------------------
def getISOTimeFromMicroseconds(ms):
    """"""
    return time.strftime("%H:%M:%S", time.localtime(float(ms)))


# ----------------------------------------------------------------------
def getISODateFromMicroseconds(ms):
    """"""
    return time.strftime("%Y%m%d", time.localtime(float(ms)))


# ----------------------------------------------------------------------
def getISOHHMMFromMSeconds(ms):
    """"""
    return time.strftime("%H:%M", time.localtime(float(ms)))


# ----------------------------------------------------------------------
def getISOHHMMSSFromMSeconds(ms):
    """"""
    return time.strftime("%H:%M:%S", time.localtime(float(ms)))


# ----------------------------------------------------------------------
def getISODate(num=0):
    """"""
    return time.strftime("%Y%m%d", time.localtime())


# ----------------------------------------------------------------------
def getISOMS(num=0):
    """"""
    return time.strftime("%M%S", time.localtime())


# ----------------------------------------------------------------------
def getCurrentTimeYMD():
    """"""
    return time.strftime("%H:%M:%S", time.localtime())


# ----------------------------------------------------------------------
def getCurrentDateYMD():
    """"""
    return time.strftime("%Y%m%d", time.localtime())


# ----------------------------------------------------------------------
def getCurrentDateTimeYMD():
    """"""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


# ----------------------------------------------------------------------
def getSecondsFromISOString(s, ISO_FORMAT):
    """"""
    return str(int(time.mktime(time.strptime(s, ISO_FORMAT))))


def iSOString2Time(s):
    '''
    convert a ISO format time to second
    from:2006-04-12 16:46:40 to:23123123
    把一个时间转化为秒
    '''
    return time.strptime(s, ISOTIMEFORMAT)


def time2ISOString(s):
    '''
    convert second to a ISO format time
    from: 23123123 to: 2006-04-12 16:46:40
    把给定的秒转化为定义的格式
    '''
    return time.strftime(ISOTIMEFORMAT, time.localtime(float(s)))


def datePlusTime(d, t):
    '''
    d=2006-04-12 16:46:40
    t=2小时
   return  2006-04-12 18:46:40
   计算一个日期相差多少秒的日期,time2sec是另外一个函数，可以处理，3天，13分钟，10小时等字符串，回头再来写这个，需要结合正则表达式。
    '''
    # return time2ISOString(time.mktime(iSOString2Time(d)) + time2sec(t))


def dateMinDate(d1, d2):
    '''
    minus to iso format date,return seconds
    计算2个时间相差多少秒
    '''
    d1 = iSOString2Time(d1)
    d2 = iSOString2Time(d2)
    return time.mktime(d1) - time.mktime(d2)


########################################################################
import datetime


# ----------------------------------------------------------------------
def getSeconds(year, month, day, hour, minute, second, ms=0):
    """
    [year, month, day, hour, minute, second] = > seconds
    """
    d = datetime.datetime(year, month, day, hour, minute, second, ms)
    return time.mktime(d.timetuple())


# ----------------------------------------------------------------------
def getCurrentYear():
    """"""
    return time.gmtime().tm_year


# ----------------------------------------------------------------------
def getCurrentMonth():
    """"""
    return time.gmtime().tm_mon


# ----------------------------------------------------------------------
def getCurrentDay():
    """"""
    return time.gmtime().tm_mday


# ----------------------------------------------------------------------
def getCurrentWDay():
    """get current day of week
    return int (1~7)"""
    return time.gmtime().tm_wday + 1


# ----------------------------------------------------------------------
def getThisDaySeconds(hour, minute=0, second=0, ms=0):
    """"""
    return getSeconds(getCurrentYear(), getCurrentMonth(), getCurrentDay(), hour, minute, second, ms)


# ----------------------------------------------------------------------
def getThisDaySecondsFromStr(HHMMSSmmm):
    """得到当前的系统时间，不带毫秒"""
    if len(HHMMSSmmm) < 9:
        print 'Time type is not HHMMSSmmm', HHMMSSmmm
        return
    h = int(HHMMSSmmm[0:2])
    m = int(HHMMSSmmm[2:4])
    s = int(HHMMSSmmm[4:6])
    ms = int(HHMMSSmmm[6:])
    # print h, m, s, ms
    return getThisDaySeconds(h, m, s, ms)


if __name__ == '__main__':
    # print getThisTimeMicrosecondString()
    st = '120147039'
    print getThisDaySecondsFromStr(st)
    st = '120148739'
    print getThisDaySecondsFromStr(st)
    st = '141948739'
    print getThisDaySecondsFromStr(st)
    print type(getThisDaySecondsFromStr(st))

    print getCurentMicroseconds()

    unittest.main()
