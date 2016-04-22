# -*- coding:utf-8 -*-

import re
import cgi
from collections import defaultdict

IS_MULTI_COMMENT = False

def repeat_code():
    return cgi.escape(file(__file__.rstrip("c")).read())

def equal(s1, s2):
    if s1 == s2:
        return 1
    else:
        return 0
    
def similar(s1, s2):
    if s1 == s2:
        score = 1 if len(s1) > 1 else 0.1
        return score

    set1 = s1.lower().split()
    set2 = s2.lower().split()
    count = 0
    for e in set1:
        if e in set2:
            count += 1
            set2.remove(e)
    
    return 1.0 * count/(len(set1) + len(set2))


def cosine(s1, s2):
    return similar(s1, s2)

def print_lcs(m, i, j, s1, s2, cmp_func):
    if not i or not j:
        return []
    if m[i][j] == m[i-1][j-1] + cmp_func(s1[i-1], s2[j-1]):
        l = print_lcs(m, i-1, j-1, s1, s2, cmp_func)
        l.append((i, j))
        return l
    elif m[i][j] == m[i][j-1]:
        l = print_lcs(m, i, j-1, s1, s2, cmp_func)
        l.append((0, j))
        return l
    elif m[i][j] == m[i-1][j]:
        l = print_lcs(m, i-1, j, s1, s2, cmp_func)
        l.append((i, 0))
        return l


def dynamic_programming(s1, s2, cmp_func):
    matrix = [[0] * (len(s2)+1)]
    
    i = 1
    for e1 in s1:
        matrix.append([0])
        
        j = 1
        for e2 in s2:
            score = cmp_func(e1, e2)
            choice = max(matrix[i-1][j-1]+score, matrix[i-1][j], matrix[i][j-1])
            matrix[i].append(choice)
            j+=1
        i+=1
    return matrix

def deal_comment(line, comment):
    global IS_MULTI_COMMENT
    parts = re.split('//', line)
    if len(parts) > 1:
        comment.append(parts[1])
        if len(parts[0]):
            line = parts[0]
            return line
        else:
            return None
    
    parts = re.split('/\*\*?', line)
    if len(parts) > 1:
        # 存在一些人单行注释也用 /* */
        nparts = re.split('\*/', parts[1])
        if len(nparts) > 1:
            IS_MULTI_COMMENT = False
            comment.append(nparts[0])
        else:
            comment.append(parts[1])
            IS_MULTI_COMMENT = True
        return None
        
    if IS_MULTI_COMMENT:
        parts = re.split('\*/', line)
        if len(parts) > 1:
            IS_MULTI_COMMENT = False
            comment[-1] += parts[0]
        else:
            comment[-1] += line.replace('*', '')
        return None
    return line

def print_comment_set():
    for c in comment:
        print comment.index(c), c


def filter_comment_variable(content):
    new_content = []
    lineno = 0
    olineno = 0
    comments = []
    new_line_map = {}
    assign_pattern = r'\w+(?:\[\d*\])?\s*(?:=\s*[^,;]+)?[),;]'
    assign_var = r'(\w+)(?:\[\d*\])?\s*(?:=\s*[^,;]+)?[),;]'
    variables = defaultdict(list)
    for line in content:
        olineno += 1
        if not line:
            continue

        line = deal_comment(line, comments)
        if not line:
            continue

        l = re.findall(assign_var, line)

        if l:
            for e in l:
                sub_pattern = r"\b%s\b" % e
                line =  re.sub(sub_pattern, 'var', line)
                variables[e].append(olineno)

        line = line.strip()
        if not line:
            continue
        lineno += 1
        new_line_map[lineno] = olineno
        new_content.append(line)
    
    return new_content, comments, variables, new_line_map


def filter_variable(content, var):
    new_content = []
    for line in content:
        assert line
        for k in var.keys():
            if k not in line:
                continue
            sub_pattern = r"\b%s\b" % k
            line =  re.sub(sub_pattern, 'var', line)
        new_content.append(line)
    return new_content

def filter_content(fcontent):
    first_content, comment, vs, line_map = filter_comment_variable(fcontent)
    second_content = filter_variable(first_content, vs)
    return second_content, comment, vs, line_map

def convert_lcs(l, pairmap):
    s1 = []
    e1 = 0
    s2 = []
    e2 = 0
    for i1, i2 in l:
        if i1:
            o_no1 = pairmap[0][i1]
        else:
            o_no1 = -1
        if i2:
            o_no2 = pairmap[1][i2]
        else:
            o_no2 = -1
        s1.append(pairmap[0][i1] if i1 else -1)
        s2.append(pairmap[1][i2] if i2 else -1)
        
    return [s1, s2]


def readLines(fname):
    fp = file(fname)
    fcontent = fp.readlines()
    fp.close()
    return fcontent

def compare_by_lines(content1, content2, cmpfunc):
    a_content, a_comment, a_vars, a_line_map = filter_content(content1)
    b_content, b_comment, b_vars, b_line_map = filter_content(content2)

    m = dynamic_programming(a_content, b_content, cmpfunc)
    l = print_lcs(m, len(a_content), len(b_content), a_content, b_content,
            cmpfunc)

    comment = (a_comment, b_comment, 0)
    variables = (a_vars, b_vars, 0)
    code = convert_lcs(l, (a_line_map, b_line_map))
    code.append(1.0*m[len(a_content)][len(b_content)])
    return comment, variables, code

def compare_files(f1, f2, cmpfunc):
    content1 = readLines(f1)
    content2 = readLines(f2)
    return compare_by_lines(content1, content2, cmpfunc)

if __name__ == "__main__":
    import sys
    print len(sys.argv)
    if len(sys.argv) < 3:
        aname = "G:/project/dataset/codeplagiarism/A1/3-3/1.java"
        bname = "G:/project/dataset/codeplagiarism/A1/3-3/2.java"
    else:
        aname = sys.argv[1]
        bname = sys.argv[2]

    comments, vs, code = compare_files(aname, bname, equal)
    print code[0]
    print code[1]
    print code[2]
