#!/usr/bin/python
#coding=utf8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import json
import urllib2
 
def get_clip_jdata(lines):
    type = lines[0].strip()
    teamname = lines[1].strip()
    fname, value = lines[2].strip().split()

    jdata = {'type': type, 'teamname': teamname, 'fname': [fname], 
            'value': value}
    data = []
    for l in lines[3:]:
        if not l:
            continue
        e = l.strip().split()
        if len(e) != 4:
            print e
            error_exit('data format wrong, 4 values per line')
        data.append(e)

    jdata['data'] = data
    return jdata

def get_repeat_jdata(lines):
    type = lines[0].strip()
    teamname = lines[1].strip()
    f1, f2, value = lines[2].strip().split()

    jdata = {'type': type, 'teamname': teamname, 'fname': [f1, f2], 
            'value': value}
    data = []
    for l in lines[3:]:
        if not l:
            continue
        e = l.strip().split()
        if len(e) != 2:
            error_exit('data format wrong, 2 values per line')
        data.append(e)

    jdata['data'] = data
    return jdata


def post(jdata):
    httpClient = None
    try:
        url = "http://localhost:9090/rank"
        jdata = json.dumps(jdata)             # 对数据进行JSON格式化编码
        req = urllib2.Request(url, jdata)       # 生成页面请求的完整数据
        response = urllib2.urlopen(req)       # 发送页面请求
        print response.read()                    # 获取服务器返回的页面信息

    except Exception, e:
        print e
    finally:
        if httpClient:
            httpClient.close()


def error_exit(info):
    print info
    raw_input('enter any key to exit')
    sys.exit()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        fname = raw_input('enter file name:\n')
    elif len(sys.argv) == 2:
        fname = sys.argv[1]
    else:
        error_exit('error parameters, nothing can do')


    fp = file(fname)
    content = fp.read()
    fp.close()

    # 下面这段 没用
   #name = r'\s*\n.*\n'
   #clip_fv = r'\w+\.\w+\s+[0-9.]+\n'
   #clip_data = r'(?:\d+\s+\d+\s+\d+\s+\d+\s+\n?)+$'
   #clip_re = r'clip' + name + clip_fv + clip_data

   #code_fv = r'\w+\.\w+\s+\w+\.\w+\s+[0-9.]+\n'
   #code_data = r'(?:\d+\s+\d+\s+\n?)+$'
   #code_re = r'coderepeat' + name + code_fv + code_data

   #re_map = {'clip': clip_re, 'coderepeat': code_re}

    function_map = {'clip': get_clip_jdata, 'coderepeat': get_repeat_jdata}


    lines = content.split('\n')
    type = lines[0].strip()
    if not type:
        error_exit('error file format, first line must be the type')
    if type not in function_map:
        error_exit('%s not define, only clip, coderepeat' % type)

   #m = re.match(re_map[type], content)

   #if not m:
   #    error_exit("content format wrong")

    jdata = function_map[type](lines)
    print jdata

    post(jdata)

