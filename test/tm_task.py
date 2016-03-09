#!/usr/bin/env python
# -*- coding: utf-8 -*-


""" a timer task class
"""

import gevent
import time


__author__ = 'qinjing'

__all__ = ['TimerProc']


class TimerTask(object):
    def __init__(self, handler, time_out, data):
        self.tm_handler = handler
        self.crtime = time.time()
        self.time_out = time_out
        self.data = data


class TimerProc(object):
    def __init__(self):
        self.timer_tasks = []
        self.running = 1

    def add_task(self, handler, timeout, data):
        task = TimerTask(handler, timeout, data)
        self.timer_tasks.append(task)

    def timer_handle(self):
        while self.running:
            gevent.sleep(0.5)
            now = time.time()
            i = 0
            for task in self.timer_tasks:
                if now - task.crtime > task.time_out:
                    if not task.tm_handler(task.data):
                        del self.timer_tasks[i]
                i += 1
