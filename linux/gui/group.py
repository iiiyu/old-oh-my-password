#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Qiu Hailong
# 
# Author:     Qiu Hailong <qiuhailong@linuxdeepin.com>
# Maintainer: Qiu Hailong <qiuhailong@linuxdeepin.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

class Group(object):
    
    def __init__(self):
        pass
    def add(self, group_list):
        self._group_llist = group_list
        for i in group_list:
            i.connect("_changed", self.changed)
            
    def changed(self, w, b):
        
        

