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
        if type == "search":
            s, h = tailor.clip_fabric()
        else:
            s, h = tailor.clip_greedy()
        logging.debug(s)

        solution = []
        for r in s:
            solution.append([r[5], r[4], r[3]-r[5], r[2]-r[4]])

        self.response.out.write(json.dumps({'solution':solution}))

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
                                'code': codes})
        self.response.out.write(response)


app = webapp2.WSGIApplication([
    ('/hongbao.html', HongBaoShowPage),
    ('/hb_stat.html', StatHongBaoPage),
    ('/qhb.html', HongBaoPage),
    ('/clip-fabric.html', ClipFabricPage),
    ('/coderepeat.html', CodeRepeatPage),
    ('/clip', ClipPage),
    ('/cmpcode', CodeCmpPage),
    ('/who-is-absent.html', AbsentPage)
], debug=True)
