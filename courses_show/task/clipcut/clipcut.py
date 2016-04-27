# coding: utf-8

import os
import cgi
import heapq
import logging

debug = 0

try:
    import numpy as np
except:
    np = None

def clip_code():
    return cgi.escape(file(__file__.rstrip("c")).read())

def overlap(a, b):
    
    if b[0] >= a[2] or b[1] >= a[3]:
        return False
    elif a[0] >= b[2] or a[1] >= b[3]:
        return False
    return True


def check_clip(data, fname):
    fn = os.path.join("competition/clip", fname)
    fp = file(fn)
    content = fp.readlines()
    fp.close()

    cw, cl, n = [int(e) for e in content[0].strip().split()]
    for i in range(len(data)):
        for j in range(len(data[i])):
            data[i][j] = int(data[i][j])

    defects = [e.split() for e in content[n+1:]]
    for i in range(len(defects)):
        for j in range(len(defects[i])):
            defects[i][j] = int(defects[i][j])

    i = 1
    for e in data:

        for other in data[i:]:
            if overlap(e, other):
                logging.debug(e)
                logging.debug(other)
                return -1
       #for b in defects:
       #    if e[:4] != b and overlap(e, b):
       #        logging.debug(e)
       #        logging.debug(b)
       #        print e, b
       #        return -1

        i+=1
    l = min(e[0] for e in data if len(e) == 4)
    r = max(e[2] for e in data if len(e) == 4)
    b = min(e[1] for e in data if len(e) == 4)
    u = max(e[3] for e in data if len(e) == 4)
    area = sum((e[2]-e[0])*(e[3]-e[1]) for e in data if len(e) == 4)
    return 1.0*area/((u-b)*(r-l))


def npAlter(r, c):
    temp = []
    for i in range(r):
        row = [0] * c
        temp.append(row)
    return temp

def copy(origin, h):
    if np:
        targets = np.zeros((h, len(origin[0])), dtype=np.int8)
    else:
        targets = npAlter(h, len(origin[0]))

    for i in range(h):
        for j in range(len(origin[1])):
            targets[i][j] = origin[i][j]
    return targets


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

    def __init__(self, canvas, targets, defects):
        self.canvas = canvas
        self.h = canvas[0]
        self.w = canvas[1]

        self.defects = defects

        targets = sorted(targets, key=lambda x:max(x), reverse=True)
        if debug == 1:
            print targets

        self.targets = []
        for e in targets:
            self.targets.append(e[:])

        if np:
            self.used = np.zeros(len(targets), dtype=np.int8)
        else:
            self.used = [0] * len(targets)

        self.solution = None
        self.per_node = []
        self.used = []

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

    def clip_cut_greedy(self, type="side"):
        if type == "area":
            sorted(self.targets, key=lambda x:x[0]*x[1], reverse=True)

        self.per_node = [(0, (0, 0))]
        heapq.heapify(self.per_node)
        i = 0
        while len(self.per_node):
            min_node = heapq.heappop(self.per_node)
            x, y = min_node[1][0], min_node[1][1]
            nearest_defect = self.find_near_defect(x, y)

            diff0 = abs(x + self.targets[i][0] - y - self.targets[i][1])
            diff1 = abs(x + self.targets[i][1] - y - self.targets[i][0])

            if diff0 <= diff1:
                if self.canAddNode(min_node[1], self.targets[i]):
                    break
                elif self.canAddNode(min_node[1], self.targets[i][::-1]):
                    break
                else:
                    nodes = self.pass_defects()




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
    piece_num = int(canvas[2])
    pieces = []
    defects = []

    for r in content[1:piece_num+1]:
        l = [int(e) for e in r.split()]
        if len(l) < 2 or len(l) > 3:
            print "data is wrong in", r
            sys.exit()

        if len(l) == 3:
            for i in range(l[2]):
                pieces.append([l[0], l[1]])
        else:
            pieces.append(l)

    for r in content[piece_num+1:]:
        l = [int(e) for e in r.split()]
        if len(l) != 4:
            print "data is wrong in", r
            sys.exit()
        defects.append(l)

    demo = GeniusTailor((x, y), pieces, defects)
    #s, h = demo.clip_greedy()
    s, h = demo.clip_cut_greedy()
    end = time.time()
    print 'the minimum height is ', h
    print 'use time', end-start
    fp.close()

    import profile
    #profile.run("demo.clip_greedy()")
