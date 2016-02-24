#!/usr/bin/env python
#-*- coding: utf-8 -*-

from hongbao import *

import matplotlib.pyplot as plt

if __name__=='__main__':

    demo = HongBao()

    result = np.array([])
    for i in range(10000):
        money_list = demo.allocate_money()
        result = np.append(result, money_list)

    print len(result)
    plt.hist(result, bins=40)
    plt.xlabel('money')
    plt.ylabel('number')
    plt.show()

