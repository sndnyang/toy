# coding: utf-8

import cgi
import logging

debug = 0

try:
    import numpy as np
except:
    np = None

def clip_code():
    return cgi.escape(file(__file__.rstrip("c")).read())

def npAlter(r, c):
    temp = []
    for i in range(r):
        row = [0] * c
        temp.append(row)
    return temp

def copy(origin, h):
    if np:
        target = np.zeros((h, len(origin[0])), dtype=np.int8)
    else:
        target = npAlter(h, len(origin[0]))

    for i in range(h):
        for j in range(len(origin[1])):
            target[i][j] = origin[i][j]
    return target


def commandLine(m):
    for r in m:
        print ' '.join(str(e) for e in r)


def init_matrix(canvas):
    if np:
        m = np.zeros((canvas[0]+2, canvas[1]+2), dtype=np.int8)
    else:
        m = npAlter(canvas[0]+2, canvas[1]+2)
    for i in range(canvas[0]+2):
        m[i][0] = 3
        m[i][canvas[1]+1] = 3

    for j in range(canvas[1]+2):
        m[0][j] = 3
        m[canvas[0]+1][j] = 3
    return m


class GeniusTailor:

    def __init__(self, canvas, targets):
        self.canvas = canvas
        self.h = canvas[0]
        self.w = canvas[1]
        targets = sorted(targets, key=lambda x:max(x), reverse=True)
        if debug == 1:
            print targets
        self.targets = []
        for e in targets:
            e = list(e)
            e.append(e[0])
            e.append(e[1])
            e.append(0)
            e.append(0)
            self.targets.append(e[:])

        if np:
            self.used = np.zeros(len(targets), dtype=np.int8)
        else:
            self.used = [0] * len(targets)
        self.min_h = sum(max(e) for e in targets)
        self.solution = None
        self.solution_matrix = None
        self.per_node = []
        self.m = init_matrix((max(self.min_h, self.h), canvas[1]))

    def can_place(self, x, y, h, w):

        if x+h-1 > self.h or y+w-1 > self.w:
            return False

        if (self.m[x-1][y] <= 1 or self.m[x][y-1] <= 1):
            return False

        for i in range(x, x+h):
            if self.m[i][y] > 1: return False
            if self.m[i][y+w-1] > 1: return False

        for j in range(y, y+w):
            if self.m[x][j] > 1: return False
            if self.m[x+h-1][j] > 1: return False
            
        # this should be the same as above judgement
        if self.m[x-1][y] > 1 and self.m[x][y-1] > 1:
            return True
        if self.m[x+h+1][y] > 1 and self.m[x+h][y-1] > 1:
            return True
        if self.m[x+h+1][y+w] > 1 and self.m[x+h][y+w+1] > 1:
            return True
        if self.m[x-1][y+w] > 1 and self.m[x][y+w+1] > 1:
            return True
        
        return False

    def greedy(self, d):
        newh = self.height()

        if debug == 2:
            print "greedy at level ", d, len(self.targets)
        if newh > self.min_h: return
        
        if d+1 > len(self.targets):
            if debug == 2:
                print "all used and get height", newh
            if newh < self.min_h:
                self.min_h = newh
                self.solution = []
                for e in self.targets:
                    self.solution.append(e[:])
                self.solution_matrix = copy(self.m, self.min_h)
            return
         
        e = self.targets[d]
        self.per_node = sorted(self.per_node)
        plen = len(self.per_node)
        if debug == 2:
            print e, 'is to place'
            commandLine(self.m)
        for (i, j) in self.per_node:
            flag = False
            if self.m[i][j] > 1: continue
            if debug == 2:
                print (i, j), " is ok peripheral"
            if self.can_place(i, j, e[0], e[1]):
                if debug == 2:
                    print (i, j), ' can place '
                flag = True
                self.place(i, j, e[0], e[1], e)
                self.greedy(d+1)
                self.unplace(e, plen)

            if self.can_place(i, j, e[1], e[0]):
                if debug == 2:
                    print (i, j), ' can place '
                flag = True
                self.place(i, j, e[1], e[0], e)
                self.greedy(d+1)
                self.unplace(e, plen)

            if flag: break

    def clip_greedy(self, type="side"):
        if type == "area":
            sorted(self.targets, key=lambda x:x[0]*x[1], reverse=True)

        self.per_node = [(1, 1)]
        self.greedy(0)
        
        if debug == 3:
            commandLine(self.solution_matrix)
            print(self.solution)
        return self.solution, self.min_h

    def clip_fabric(self):
        
        for i in range(len(self.targets)):
            self.used[i] = 1

            self.place(1, 1, self.targets[i][0], self.targets[i][1],
                    self.targets[i])
            self.dfs()   
            self.unplace(self.targets[i], 4)

            self.place(1, 1, self.targets[i][1], self.targets[i][0],
                    self.targets[i])
            self.dfs()
            self.unplace(self.targets[i], 4)

            self.used[i] = 0

        #commandLine(self.solution_matrix)
        return self.solution, self.min_h

    def height(self):
        return max(self.targets, key=lambda x:x[2])[2]-1

    def peripheral(self, i, j):
        for (u, v) in [(1,0),(0,1),(-1,0),(0,-1)]:
            if i+u < 0 or j+v < 0 or i+u >= self.h or j+v >= self.w:
                continue
            if self.m[i+u][j+v] == 0: 
                self.m[i+u][j+v] = 1
                self.per_node.append((i+u, j+v))

    def place(self, x, y, h, w, e):

        for i in range(x, x+h):
            for j in range(y, y+w):
                self.m[i][j] = 2

        self.peripheral(x, y)
        self.peripheral(x, y+w-1)
        self.peripheral(x+h-1, y)
        self.peripheral(x+h-1, y+w-1)

        e[2] = x + h
        e[3] = y + w
        e[4] = x
        e[5] = y


    def dfs(self):
        newh = self.height()
        if newh > self.min_h: return
        
        if sum(self.used) == len(self.targets):
            if newh < self.min_h:
                self.min_h = newh
                self.solution = []
                for e in self.targets:
                    self.solution.append(e[:])
                self.solution_matrix = copy(self.m, self.h)
                
        for i in range(len(self.targets)):
            if self.used[i]: continue
            self.used[i] = 1
            ele = self.targets[i]
            self.placehold(ele)
            self.used[i] = 0
 
    def placehold(self, e):
        for (i, j) in self.per_node:
            plen = len(self.per_node)
            if self.m[i][j] > 1: continue

            if self.can_place(i, j, e[0], e[1]):
                self.place(i, j, e[0], e[1], e)
                self.dfs()
                self.unplace(e, plen)

            if self.can_place(i, j, e[1], e[0]):
                self.place(i, j, e[1], e[0], e)
                self.dfs()
                self.unplace(e, plen)

    def unplace(self, e, pnodes):
        self.per_node = self.per_node[:pnodes]
        for i in range(e[4], e[2]):
            for j in range(e[5], e[3]):
                self.m[i][j] = 0
        e[2] = 0
        e[3] = 0


if __name__ == '__main__':
    import sys
    import time

    if len(sys.argv) > 1:
        debug = int(sys.argv[1])

    start = time.time()
    print "please input your data in data.txt, like this:"
    print "200 200  clothlength width"
    print "10 10 first pieces's length and width"
    print "21 3   chinese cause messy code"
    print "15 5"
    print "7 8"

    raw_input("if ok, enter any key to continue\r\n")

    fp = file("data.txt")
    content = fp.readlines()
    canvas = content[0].split()
    x = int(canvas[0])
    y = int(canvas[1])
    pieces = []
    for r in content[1:]:
        l = [int(e) for e in r.split()]
        if len(l) != 2:
            print "data is wrong in", r
            sys.exit()
            
        pieces.append(l)

    demo = GeniusTailor((x, y), pieces)
    s, h = demo.clip_greedy()
    end = time.time()
    print 'the minimum height is ', h
    print 'use time', end-start
    fp.close()

    import profile
    #profile.run("demo.clip_greedy()")
