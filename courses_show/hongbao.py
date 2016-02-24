#!/usr/bin/env python
#-*- coding: utf-8 -*-

import random
import numpy as np

def in_range(number, mu, limit):
    if mu * (1-limit) <= number and number <= mu * (1+limit):
        return True
    return False

class HongBao:
    def __init__(self):
        pass

    def allocate_money(self, money=100, number=10):

        avg = int(100*money) / number
        money_list = avg * np.ones(number)
        money_list[0] += 100*money - money_list.sum()

        for i in range(number-2):
            j = random.randint(i+1, number-1)
            var = int(avg * random.random() - .5*avg)
            if in_range(money_list[i]+var, avg, .5) and \
                in_range(money_list[j]-var, avg, .5):
                    money_list[i] += var
                    money_list[j] -= var

        return money_list/100


if __name__=='__main__':
    demo = HongBao()
    for i in range(3):
        money_list = demo.allocate_money()
        print money_list
