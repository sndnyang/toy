# coding: utf-8

try:
    import numpy as np
except:
    np = None

min_h = 100000

def peripheral(m, i, j):
    if np:
        h = m.shape[0]
        w = m.shape[1]
    else:
        h = len(m)
        w = len(m[0])
    for (u, v) in [(1,0),(0,1),(-1,0),(0,-1)]:
        if i+u < 0 or j+v < 0 or i+u >= h or j+v >= w:
            continue
        if m[i+u][j+v] == 0: 
            m[i+u][j+v] = 1


def place(m, x, y, h, w):

    for i in range(x, x+h):
        for j in range(y, y+w):
            m[i][j] = 2

    peripheral(m, x, y)
    peripheral(m, x, y+w-1)
    peripheral(m, x+h-1, y)
    peripheral(m, x+h-1, y+w-1)


def can_place(m, x, y, h, w):

    if x+h+1 >= len(m) or y+w+1 >= len(m[0]):
        return False
    
    for i in range(x, x+h):
        if m[i][y] > 1: return False
        if m[i][y+w-1] > 1: return False

    for j in range(y, y+w):
        if m[x][j] > 1: return False
        if m[x+h-1][j] > 1: return False
        
    if m[x-1][y] > 1 and m[x][y-1] > 1:
        return True
    if m[x+h+1][y] > 1 and m[x+h][y-1] > 1:
        return True
    if m[x+h+1][y+w] > 1 and m[x+h][y+w+1] > 1:
        return True
    if m[x-1][y+w] > 1 and m[x][y+w+1] > 1:
        return True
    
    return False

def npAlter(r, c):
    temp = []
    for i in range(r):
        row = [0] * c
        temp.append(row)
    return temp

def copy(origin):
    if np:
        target = np.zeros(origin.shape, dtype=np.int8)
    else:
        target = npAlter(len(origin), len(origin[0]))
    for i in range(len(origin)):
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
        sorted(targets, key=lambda x:max(x))
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

    def clip_fabric(self):
        
        for i in range(len(self.targets)):
            self.used[i] = 1

            m = init_matrix(self.canvas)
            place(m, 1, 1, self.targets[i][0], self.targets[i][1])
            self.targets[i][2] = 1+self.targets[i][0]
            self.targets[i][3] = 1+self.targets[i][1]
            self.targets[i][4] = 1
            self.targets[i][5] = 1
            self.dfs(m)   
            self.targets[i][2] = 0
            self.targets[i][3] = 0

            m = init_matrix(self.canvas)
            place(m, 1, 1, self.targets[i][1], self.targets[i][0])
            self.targets[i][2] = 1+self.targets[i][1]
            self.targets[i][3] = 1+self.targets[i][0]
            self.targets[i][4] = 1
            self.targets[i][5] = 1
            self.dfs(m)
            self.targets[i][2] = 0
            self.targets[i][3] = 0

            self.used[i] = 0
        print self.min_h
        print self.solution
        commandLine(self.solution_matrix)
        print len(self.solution_matrix)
        return self.solution, self.min_h

    def height(self):
        return max(self.targets, key=lambda x:x[2])[2]-1

    def dfs(self, m):
        newh = self.height()
        if newh > self.min_h: return
        
        if sum(self.used) == len(self.targets):
            if newh < self.min_h:
                self.min_h = newh
                self.solution = []
                for e in self.targets:
                    self.solution.append(e[:])
                self.solution_matrix = copy(m)
                
        for i in range(len(self.targets)):
            if self.used[i]: continue
            self.used[i] = 1
            ele = self.targets[i]
            tempm = copy(m)
            self.placehold(tempm, ele)
            self.used[i] = 0
 
    def placehold(self, m, e):
        for i in range(len(m)):
            for j in range(len(m[0])):
                if m[i][j] != 1: continue

                if can_place(m, i, j, e[0], e[1]):
                    newm = copy(m)
                    place(newm, i, j, e[0], e[1])
                    e[2] = i + e[0]
                    e[3] = j + e[1]
                    e[4] = i
                    e[5] = j
                    self.dfs(newm)
                    e[2] = 0
                    e[3] = 0

                if can_place(m, i, j, e[1], e[0]):
                    newm = copy(m)
                    place(newm, i, j, e[1], e[0])
                    e[2] = i + e[1]
                    e[3] = j + e[0]
                    e[4] = i
                    e[5] = j
                    self.dfs(newm)
                    e[2] = 0
                    e[3] = 0


if __name__ == '__main__':
    import time
    start = time.time()
    import profile
    demo = GeniusTailor((30, 30), [(10, 10), (21, 3), (15,5), (7, 8)])
    #demo.clip_fabric()
    profile.run("demo.clip_fabric()")
    end = time.time()
    print end-start
