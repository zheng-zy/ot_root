#!usr/bin/env python
# coding=utf-8
# Author: zhezhiyong@163.com
# Created: 2016-03-09 09:11:10
# Python version：2.7.10
"""
# TODO(purpose): 
"""

import uuid
import time

# 操作 etf代码  成份股代码
print uuid.uuid1(01510300000001)
print uuid.uuid1(01510300000001)
print uuid.uuid1(01510300000001)


# 10 1000 5 1000 6 1000
# 9.5 900 4.9 1000 5.8 1000

class A(object):
    def __init__(self):
        self.stage_lst = [1, 2, 3]
        self.curr_stage = 1

    def excute(self, stage=1):
        if stage == 1:
            print 'stage 1'
        if stage == 2:
            print 'stage 2'
        if stage == 3:
            print 'stage 3'
        self.next_stage()

    def next_stage(self):
        self.curr_stage += 1
        self.is_finish()

    def is_finish(self):
        if self.curr_stage not in self.stage_lst:
            print 'finish'

print list([1])
if __name__ == "__main__":
    a = A()
    a.excute(a.curr_stage)
    a.excute(a.curr_stage)
    a.excute(a.curr_stage)
    # a.excute(a.curr_stage)
    # a.excute(a.curr_stage)

    # print (9.5 * 900 + 4.9 * 1000 + 5.8 * 1000) / (10 * 1000 + 5 * 1000 + 6 * 1000)
    # print ((9.5 * 900) / (10 * 1000) + (4.9 * 1000) / (5 * 1000) + (5.8 * 1000) / (6 * 1000)) / 3
    pass
