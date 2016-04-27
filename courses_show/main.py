#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import sys
if sys.getdefaultencoding() != 'utf8':
    reload(sys)
    sys.setdefaultencoding('utf8')

import os
import json
import jinja2
import webapp2

import logging
logging.getLogger().setLevel(logging.DEBUG)

from datetime import datetime

from task import *

from model import *

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
        autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

class HongBaoShowPage(Handler):
    def get(self):
        self.render("hongbao.html")

    def post(self):
        from task import HongBao
        money = float(self.request.get("money"))
        number = int(self.request.get("number"))
        if money and number:
            demo = HongBao()
            hb_list = demo.allocate_money_list(money, number)
            self.render("hongbao.html", hb_list=hb_list)
        else:
            error = "please enter a money and number"
            self.render("hongbao.html", error=error)


class HongBaoPage(Handler):
    def get(self):
        self.render("qhb.html")

    def post(self):
        name = self.request.get("name")
        hoster = self.request.get("sendname", "default")
        qry = HongBaoDB.query(HongBaoDB.name == hoster)
        demo = HongBao()
        money = demo.allocate_money(qry.money, qry.number-qry.rec_num)
        if name:
            self.render("qhb.html", name=name, money=money)
        else:
            error = "please enter your name"
            self.render("qhb.html", error=error)

def source_code(name):
    name_file = {"hongbao": hb_code(),
            "clip": clip_code(),
            "repeat": repeat_code()}
    return name_file[name] if name in name_file else ""


class StatHongBaoPage(Handler):
    def get(self):
        self.render("hb_stat.html", png=dynamic_png(), source =\
        source_code("hongbao"))


class AbsentPage(Handler):
    def get(self):
        self.render("who-is-absent.html")

class ClipFabricPage(Handler):
    def get(self):
        self.render("clip-fabric.html", source = source_code("clip"))

class ClipPage(Handler):
    def post(self):
        data = json.loads(self.request.body)
        canvas = data.get('canvas')
        pieces = data.get('pieces')
        types = data.get('type')

        canvas[0] = int(canvas[0])
        canvas[1] = int(canvas[1])

        pdata = [int(e) for e in pieces.split()]
        pieces = [[]]

        if len(pdata)%2:
            self.response.out.write(u"布料大小不成对")

        count = 0
        for i in range(len(pdata)):
            pieces[count].append(pdata[i])
            if i % 2:
                count += 1
                pieces.append([])

        pieces.pop()

        tailor = GeniusTailor(canvas, pieces)
       #if type == "search":
       #    s, h = tailor.clip_fabric()
       #else:
       #    s, h = tailor.clip_greedy()

        solution = [[1, 2, 20, 30]]
       #for r in s:
       #    solution.append([r[5], r[4], r[3]-r[5], r[2]-r[4]])

        self.response.out.write(json.dumps({'solution':solution},
            ensure_ascii=False))


class GetSolution(Handler):
    def get(self):
        name = self.request.get('name', '')
        team = self.request.get('team', '')
        fname = self.request.get('fname', '')

        response = {'code': False}
        testdatas = []
        try:
            current = ''
            for fn in fname.split():
                current = fn
                fn = os.path.join("competition", name, fn)
                fp = file(fn)
                content = fp.read()
                fp.close()
                testdatas.append(content)
        except:
            response['info'] = '%s file not exist' % current
            self.response.out.write(json.dumps(response,
                ensure_ascii=False))
            return

        response['data'] = testdatas
        q = SubmitRecord.query().filter(SubmitRecord.teamname == team, 
                SubmitRecord.enname == name, SubmitRecord.fname == fname)
        record = None
        for e in q:
            record = e
        if not record:
            code = False
            solution = ''
            stdvalue = False
            value = False
        else:
            code = True
            solution = record.data
            stdvalue = record.stdvalue
            value = record.value

        response['solution'] = solution
        response['code'] = code
        response['value'] = value
        response['stdvalue'] = stdvalue

        self.response.out.write(json.dumps(response,
            ensure_ascii=False))

class ShowSolutionPage(Handler):
    def get(self):
        name = self.request.get('name', '')
        team = self.request.get('team', '')
        fname = self.request.get('fname', '')
        if name == '' or team == '':
            self.render("index.html")
        if name == 'clip':
            self.render("clip-fabric.html", source='')
        elif name == 'coderepeat':
            self.render("coderepeat.html", source='')



class RankPage(Handler):
    def post(self):
        data = json.loads(self.request.body)
        type = data.get('type')
        response = {'info': 'success'}
        en_zh = {'clip': u'布料裁剪', 'coderepeat': u'代码判重'}
        if type not in en_zh:
            response['info'] = '%s not in %s' % (type, ['clip', 'coderepeat'])
            self.response.out.write(json.dumps(response))
            return

        team = data.get('teamname')

        if not team.startswith('xmu'):
            response['info'] = 'you do not have the authority'
            self.response.out.write(json.dumps(response))
            return

        q = User.query().filter(User.username == team)
        user = None
        for e in q:
            user = e

        if user:
            last_time = user.last_edit
            if last_time:
                now = datetime.now()
                differ = (now - last_time).seconds
                if differ >= 3:
                    user.last_edit = now
                    user.put()
                else:
                    response['info'] = "submit too quick one time per minute"
                    self.response.out.write(json.dumps(response))
                    return
        else:
            now = datetime.now()
            newuser = User(username = team, last_edit = now)
            newuser.put()
            user = newuser


        fname = ' '.join(data.get('fname'))
        result = data.get('data')
        check_routine = {'clip': check_clip, 'coderepeat': check_repeat}
        try:
            stdvalue = check_routine[type](result, fname)
            stdvalue = float("%.3f" % stdvalue)
        except Exception, e:
            response['info'] = "%s, please contact administrator" % e

            self.response.out.write(json.dumps(response))
            return

        if stdvalue == -1:
            response['info'] = 'your answer not pass the check'
            self.response.out.write(json.dumps(response))
            return

        value = float(data.get('value'))

        q = SubmitRecord.query().filter(SubmitRecord.teamname == team, 
                SubmitRecord.enname == type, SubmitRecord.fname == fname)
        record = None
        for e in q:
            record = e

        if not record:
            rkey = ndb.Key(SubmitRecord, team+' '+ fname)
            record = SubmitRecord(
                    key = rkey,
                    enname = type,
                    zhname = en_zh[type],
                    teamname = team,
                    fname = fname,
                    data = result,
                    value = value,
                    stdvalue = stdvalue
                )
        else:
            record.fname = fname
            record.data = result
            record.value = value
            record.stdvalue = stdvalue

        user.last_edit = datetime.now()
        record.put()

        self.response.out.write(response)


class LeaderBoardPage(Handler):
    def get(self):
        c = self.request.get('type', 'clip')
        en_zh = {'coderepeat': u'代码判重', 'clip': u'布料裁剪'}
        title = en_zh[c]
        base_dir = os.path.join(os.path.dirname(__file__), "competition", c)

        if not os.path.isdir(base_dir):
            competition = {'title': title, 'files': []}
            teams = []
        else:
            flists = []
            for root, dirs, files in os.walk(base_dir):
                for f in files:
                    flists.append(f)

            competition = {'title': title, 'files': flists}
            q = SubmitRecord.query().filter(SubmitRecord.enname == c)
            teams_fset = {}
            for e in q:
                name = e.teamname
                if name not in teams_fset:
                    if c == 'clip':
                        teams_fset[name] = [False] * len(flists)
                    else:
                        teams_fset[name] = []

                fname = e.fname
                if c == 'coderepeat':
                    teams_fset[name].append((e.stdvalue, e.value, fname))
                elif c == 'clip': 
                    teams_fset[name][flists.index(fname)] = (e.stdvalue, 
                            e.value, fname)

            teams = sorted(teams_fset.iteritems(), key=lambda d:d[1], 
                    reverse = True)

        self.render("leaderboard.html", title=u"琅琊算法榜", en=c,
                competition = competition, teams=teams)

class CodeRepeatPage(Handler):
    def get(self):
        self.render("coderepeat.html", source = source_code("repeat"))

class CodeCmpPage(Handler):
    def post(self):
        data = json.loads(self.request.body)
        code1 = data.get('code1').split('\n')
        code2 = data.get('code2').split('\n')
        method = data.get('method')

        cmp_funs = {'equal': equal, 'similar': similar, 'cos': cosine}
        if method in cmp_funs:
            cmpfunc = cmp_funs[method]
        else:
            cmpfunc = equal

        cs, vs, codes = compare_by_lines(code1, code2, cmpfunc)
        response = json.dumps({'comment': cs,
                                'variable': vs,
                                'code': codes},
            ensure_ascii=False)
        self.response.out.write(response)


app = webapp2.WSGIApplication([
    ('/hongbao.html', HongBaoShowPage),
    ('/hb_stat.html', StatHongBaoPage),
    ('/qhb.html', HongBaoPage),
    ('/clip-fabric.html', ClipFabricPage),
    ('/leaderboard.html', LeaderBoardPage),
    ('/showSolution.html', ShowSolutionPage),
    ('/coderepeat.html', CodeRepeatPage),
    ('/clip', ClipPage),
    ('/rank', RankPage),
    ('/cmpcode', CodeCmpPage),
    ('/getsolution', GetSolution),
    ('/who-is-absent.html', AbsentPage)
], debug=True)
