#!/usr/bin/env python
#-*- coding: utf-8 -*-

import cgi
import random
import logging
#import numpy as np

def hb_code():
    return cgi.escape(file(__file__.rstrip("c")).read())


def in_range(number, mu, limit):
    if mu * (1-limit) <= number and number <= mu * (1+limit):
        return True
    return False

class HongBao:
    def __init__(self):
        pass

    def allocate_money_list(self, money=100, number=10):

        avg = int(100*money) / number
        money_list = [avg] * number
        #money_list = avg * np.ones(number)
        money_list[0] += 100*money - sum(money_list)

        for i in range(number-2):
            j = random.randint(i+1, number-1)
            var = int(avg * random.random() - .5*avg)
            if in_range(money_list[i]+var, avg, .5) and \
                in_range(money_list[j]-var, avg, .5):
                    money_list[i] += var
                    money_list[j] -= var

        for i in range(number):
            money_list[i] /= 100.0
        return money_list

    def allocate_money(self, money=100, number=10, method="normal"):
        map = {"random": self.allocate_money_easy,
                "uniform": self.allocate_money_uni,
                "normal": self.allocate_money_normal}
        return map[method](money, number) if method in map else -1

    def allocate_money_easy(self, money=100, number=10):
        #avg = int(100*money) / number
        var = random.randint(number, money - number)
        return var if number != 1 else money

    def allocate_money_uni(self, money, number):
        return 0

    def allocate_money_normal(self, money, number):
        return 0


if __name__=='__main__':
    demo = HongBao()
    for i in range(3):
        money_list = demo.allocate_money()
        print money_list
