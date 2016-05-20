#!/usr/bin/python
#coding=utf8

import os
import sys
import heapq
import logging

#import numpy as np

from math import cos, sin, pi

used = []
point_used = []

def near_square(node):
    return abs(node[0] - node[1]) + sum(node)

def highY(node):
    return abs(node[0] - node[1]) + node[0] + node[1] * width

def rotate(p, theta):
    return (p[0] * cos(theta) - sin(theta) * p[1], sin(theta) * p[0] + cos(theta) * p[1])

def translation(p, t):
    return (p[0] + t[0], p[1] + t[1])

def transform(lists, d):
    new_defects = []
    for e in lists:
        a = translation(rotate(e[:2], pi/2), (d, 0))
        b = translation(rotate(e[2:], pi/2), (d, 0))
        new_defects.append((int(a[0]), int(a[1]), int(b[0]), int(b[1])))
    return new_defects

def readFile(fn):
    fp = file(fn)
    content = fp.readlines()
    fp.close()
    return content

def prepare(content):
    global width, height, pieces, defects
    canvas = content[0].split()
    width = int(canvas[0])
    height = int(canvas[1])
    piece_num = int(canvas[2])
    pieces = []
    defects = []
    
    for r in content[1:piece_num+1]:
        l = [int(e) for e in r.split()]
        if len(l) == 0:
            continue
        if len(l) < 2 or len(l) > 3:
            logging.error("data is wrong at " + r)
            sys.exit()

        if len(l) == 3:
            for i in range(l[2]):
                pieces.append([l[0], l[1]])
        else:
            pieces.append(l)

    for r in content[piece_num+1:]:
        l = [int(e) for e in r.split()]
        if len(l) != 4:
            logging.error("data is wrong at " + r)
            sys.exit()
        defects.append(tuple(l))
        
def findNearestDefect(point, piece, defect_list):
    logging.debug('try find defect node from (%d %d) to (%d %d)' % (point[0], point[1], point[0] + piece[0], point[1] + piece[1]))
    
    for e in defect_list:
        logging.debug('compare to (%d %d)' % (e[0], e[1]))
        if e[0] < point[0] or e[1] < point[1]:
            continue
        
        if e[0] >= point[0] + piece[0] or e[1] >= point[1] + piece[1]:
            continue
        else:
            logging.debug('find defect at (%d %d)' % (e[0], e[1]))
            return e
    logging.debug('not find')
    return None

def checkBoundry(point, piece, cut_y):
    if point[0] + piece[0] > width or point[1] + piece[1] > height:
        return False
    for y in cut_y:
        if point[1] < y and point[1] + piece[1] > y:
            return False
    return True

def overlap(a, b):
    
    if b[0] >= a[2] or b[1] >= a[3]:
        return False
    elif a[0] >= b[2] or a[1] >= b[3]:
        return False
    return True

def canAddNode(point, piece, defect_list, cut_y, solution):
    p = (point[0], point[1], point[0] + piece[0], point[1] + piece[1])
    logging.debug('try add node from (%d %d) to (%d %d)' % p)
    
    if not checkBoundry(point, piece, cut_y):
        return False
    
    for e in solution:
        if overlap(e, p):
            return False
        
    for e in defect_list:
        logging.debug('compare to (%d %d)' % (e[0], e[1]))
        if not overlap(e, p):
            continue
        else:
            logging.debug('false at (%d %d)' % (e[0], e[1]))
            return False
    logging.debug('pass')
    return True

def pushIntoHeap(heap, start, end):
    xnode = (end[0], start[1])
    ynode = (start[0], end[1])
    
    if xnode not in point_used:
        logging.info('add tow point at ' + str(xnode))
        heapq.heappush(heap, (key(xnode), xnode))
        point_used.append(xnode)
    if ynode not in point_used:
        logging.info('add tow point at ' + str(ynode))
        heapq.heappush(heap, (key(ynode), ynode))
        point_used.append(ynode)

def greedy_cut_routine(piece_list, defect_list):
    heap = [(0, (0, 0))]

    heapq.heapify(heap)
    
    cut_y = []
    solution = []
    count = 0
    while len(heap):
        min_node = heapq.heappop(heap)
        x, y = min_node[1][0], min_node[1][1]
        logging.warn('start at (%d %d)' % (x, y))
        for i in range(len(piece_list)):
            if i in used:
                continue
            diff0 = abs(x + piece_list[i][0] - y - piece_list[i][1])
            diff1 = abs(x + piece_list[i][1] - y - piece_list[i][0])
            logging.debug('chose %d %d' % (diff0, diff1))
            
            if diff0 <= diff1:
                #print 'compare'
                if canAddNode(min_node[1], piece_list[i], defect_list, cut_y, solution):
                    end = (min_node[1][0] + piece_list[i][0], min_node[1][1] + piece_list[i][1])
                    pushIntoHeap(heap, min_node[1], end)
                    used.append(i)

                    logging.warn('solution append (%d %d %d %d)' % (min_node[1][0], min_node[1][1], end[0], end[1]))
                    solution.append((min_node[1][0], min_node[1][1], end[0], end[1]))
                    cut_y.append(end[1])
                    break
                elif canAddNode(min_node[1], piece_list[i][::-1], defect_list, cut_y, solution):
                    end = (min_node[1][0] + piece_list[i][1], min_node[1][1] + piece_list[i][0])
                    pushIntoHeap(heap, min_node[1], end)
                    used.append(i)
                    logging.warn('solution append (%d %d %d %d)' % (min_node[1][0], min_node[1][1], end[0], end[1]))
                    solution.append((min_node[1][0], min_node[1][1], end[0], end[1]))
                    cut_y.append(end[1])
                    break
            else:
                if canAddNode(min_node[1], piece_list[i][::-1], defect_list, cut_y, solution):
                    end = (min_node[1][0] + piece_list[i][1], min_node[1][1] + piece_list[i][0])
                    pushIntoHeap(heap, min_node[1], end)
                    used.append(i)
                    logging.warn('solution append (%d %d %d %d)' % (min_node[1][0], min_node[1][1], end[0], end[1]))
                    solution.append((min_node[1][0], min_node[1][1], end[0], end[1]))
                    cut_y.append(end[1])
                    break
                elif canAddNode(min_node[1], piece_list[i], defect_list, cut_y, solution):
                    end = (min_node[1][0] + piece_list[i][0], min_node[1][1] + piece_list[i][1])
                    pushIntoHeap(heap, min_node[1], end)
                    used.append(i)
                    solution.append((min_node[1][0], min_node[1][1], end[0], end[1]))
                    logging.warn('solution append (%d %d %d %d)' % (min_node[1][0], min_node[1][1], end[0], end[1]))
                    cut_y.append(end[1])
                    break
        else:
            logging.info('(%d %d) cant add' % (min_node[1][0], min_node[1][1]))
            if len(used) == len(piece_list):
                break
            
            t = len(piece_list) - 1
            while t in used:
                t -= 1
            
            if t < 0:
                logging.error('how could this be here? ' + str(used))
                
            smallest_not_used = piece_list[t]
            logging.debug('find smallest not used')
            
            nearest_defect = findNearestDefect(min_node[1], smallest_not_used, defect_list)
            
            if not nearest_defect:
                nearest_defect = findNearestDefect(min_node[1], smallest_not_used[::-1], defect_list)
                if not nearest_defect:
                    #logging.error('how could this be here? ' + str(min_node) + ' ' + str(smallest_not_used))
                    #sys.exit(-1)
                    continue
                    
            pushIntoHeap(heap, min_node[1], (nearest_defect[2], nearest_defect[3]))
            nearest_defect = list(nearest_defect)
            nearest_defect.append(1)
            solution.append(tuple(nearest_defect))
            cut_y.append(nearest_defect[3])
        
        count += 1
        if count > 100:
            break

        
    return solution

def estimate(solution):
    max_x = max(e[2] for e in solution if len(e) == 4)
    max_y = max(e[3] for e in solution if len(e) == 4)
    area = sum((e[2]-e[0])*(e[3]-e[1]) for e in solution if len(e) == 4)

    return 1.0 * area / (max_x * max_y)

def appendDefects(solution, d):
    for e in d:
        f = True
        for l in solution:
            if e[:4] == l[:4]:
                f = False
                break
        if not f:
            continue
        e = list(e)
        e.append(2)
        solution.append(tuple(e))

def main(fn):
    global used, point_used
    
    prepare(readFile(fn))
    targets = sorted(pieces, key=lambda x:min(x), reverse=True)

    used = []
    point_used = []
    solutions = []
    values = []
    x = greedy_cut_routine(targets, defects)
    solutions.append(x)
    values.append(estimate(solutions[0]))
    logging.warn(values[-1])
    appendDefects(solutions[-1], defects)
    
    new_defects = transform(defects, height)
    used = []
    point_used = []
    x = greedy_cut_routine(targets, new_defects)
    solutions.append(x)
    values.append(estimate(solutions[-1]))
    logging.warn(values[-1])
    appendDefects(solutions[-1], new_defects)
    
    new_defects = transform(new_defects, width)
    used = []
    point_used = []
    x = greedy_cut_routine(targets, new_defects)
    solutions.append(x)
    values.append(estimate(solutions[-1]))
    logging.warn(values[-1])
    appendDefects(solutions[-1], new_defects)
    
    new_defects = transform(new_defects, height)
    used = []
    point_used = []
    x = greedy_cut_routine(targets, new_defects)
    solutions.append(x)
    values.append(estimate(solutions[-1]))
    logging.warn(values[-1])
    appendDefects(solutions[-1], new_defects)
    
    i = values.index(max(values))
    return solutions[i], values[i]

key = highY


if __name__ == '__main__':

    import sys

    logger = logging.getLogger()
    level = 40

    if len(sys.argv) == 1:
        fname = raw_input('enter file name:\n')
    elif len(sys.argv) == 2:
        fname = sys.argv[1]
    elif len(sys.argv) == 3:
        fname = sys.argv[1]
        level = int(sys.argv[2]) * 10
    else:
        error_exit('error parameters, nothing can do')

    logger.setLevel(level)
    solution, v = main(fname)

    print 'clip'
    print 'xmu-yxl-lh'
    print fname, '%.3f' % v

    for e in solution:
        for l in e:
            print l,
        print

