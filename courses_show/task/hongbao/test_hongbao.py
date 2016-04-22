#!/usr/bin/env python
#-*- coding: utf-8 -*-

from hongbao import *

import unittest

from colortest import ColorTestRunner

class HongBaoTest(unittest.TestCase):
    def testPass(self):
        demo = HongBao()
        money_list = demo.allocate_money()
        print money_list
        self.assertEqual(10, len(money_list))

    def testFail(self):
        demo = HongBao()
        money_list = demo.allocate_money()
        print money_list
        self.assertEqual(True, abs(100.0-sum(money_list))<0.01)

if __name__=='__main__':
    unittest.main(testRunner = ColorTestRunner())
