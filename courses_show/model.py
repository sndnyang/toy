#!/usr/bin/env python
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

from google.appengine.ext import ndb

class HongBaoDB(ndb.Model):
    name = ndb.StringProperty()
    money = ndb.FloatProperty(default = 0)
    number = ndb.IntegerProperty(default = 0)
    rec_num = ndb.IntegerProperty(default = 0)
    rec_list = ndb.JsonProperty()

class SubmitRecord(ndb.Model):
    enname = ndb.StringProperty()
    zhname = ndb.StringProperty()
    teamname = ndb.StringProperty()
    fname = ndb.StringProperty()
    data = ndb.JsonProperty(indexed=False, compressed=False)
    value = ndb.FloatProperty()
    stdvalue = ndb.FloatProperty()

class User(ndb.Model):
    username = ndb.StringProperty()
    last_edit = ndb.DateTimeProperty()

