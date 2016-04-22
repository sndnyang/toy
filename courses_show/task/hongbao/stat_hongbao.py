#!/usr/bin/env python
#-*- coding: utf-8 -*-

import StringIO

from hongbao import *

try:
    import matplotlib.pyplot as plt
except:
    pass

def dynamic_png():

    demo = HongBao()
    result = []
    for i in range(10000):
        money_list = demo.allocate_money_list()
        result += money_list
    try:
        plt.title(u'红包算法统计结果')
        plt.hist(result, bins=40)
        plt.xlabel('money')
        plt.ylabel('number')

        buf = StringIO.StringIO()
        plt.savefig(buf, format="png")
        plt.clf()
        return buf.getvalue().encode("base64").strip()
    except:
        return u'对不起， 图未能生成'


if __name__=='__main__':

    print len(result)
    
    dynamic_png()

