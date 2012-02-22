#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 QiuHailong
# 
# Author:     QiuHailong <qiuhailong@linuxdeepin.com>
# Maintainer: QiuHailong <qiuhailong@linuxdeepin.com>
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

import gtk
import cairo
from utils import *
from draw import *
from titlebar import *
from scrolledWindow import *

class PopupWindow(object):
    '''PopupWindow.'''
	
    def __init__(self, parent_widget=None, widget=None, x=None, y=None):
        '''Init PopupWindow.'''        
        
        # Init Window.
        self.popup_window = gtk.Window(gtk.WINDOW_TOPLEVEL)        
        self.popup_window.set_position(gtk.WIN_POS_MOUSE)
        self.popup_window.set_modal(True)
        self.popup_window.set_decorated(False)
        self.popup_window.set_size_request(200,300)
        
        self.main_box = gtk.VBox()
        self.title_bar = Titlebar(self.popup_window.destroy)
        self.scrolled_align  = gtk.Alignment()
        self.scrolled_align.set(0.0, 0.0, 1.0, 1.0)
        self.scrolled_window = ScrolledWindow(gtk.POLICY_NEVER)
        self.scrolled_align.add(self.scrolled_window)
        self.scrolled_align.set_padding(10, 10, 10, 10)
        
        if widget:
            self.scrolled_window.add_child(widget)
        else:
            self.buffer = gtk.TextBuffer()
            self.text_view = gtk.TextView(self.buffer)
            self.buffer.set_text("Linux Deepin")
            self.scrolled_window.add_child(self.text_view)
            
        if x and y:
            self.popup_window.move(x, y)
            
        self.popup_window.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        
        self.title_bar.drag_box.connect("button-press-event", lambda w,e:self.move_window(w,e))
        self.popup_window.connect("size-allocate", draw_window_shape)
        if parent_widget:
            self.popup_window.connect("show", lambda w:self.show_window(w, parent_widget))
            
        draw_window_background(self.popup_window, BACKGROUND_IMAGE)    
        
        self.frame_vbox = gtk.VBox()
        self.frame_hbox = gtk.HBox()
        self.top_line = gtk.HBox()
        self.top_line.set_size_request(-1, 1)
        self.bottom_line = gtk.HBox()
        self.bottom_line.set_size_request(-1, 1)
        self.left_line = gtk.VBox()
        self.left_line.set_size_request(1, -1)
        self.right_line = gtk.VBox()
        self.right_line.set_size_request(1, -1)
        
        self.main_box = gtk.VBox()
        self.main_box.pack_start(self.title_bar.box, False, False)
        self.main_box.pack_start(self.scrolled_align, True, True)

        self.frame_vbox.pack_start(self.top_line, False, False)
        self.frame_vbox.pack_start(self.frame_hbox, True, True)
        self.frame_vbox.pack_start(self.bottom_line, False, False)
        self.frame_hbox.pack_start(self.left_line, False, False)
        self.frame_hbox.pack_start(self.main_box, True, True)
        self.frame_hbox.pack_start(self.right_line, False, False)
        
        self.popup_window.add(self.frame_vbox)
        
        self.popup_window.show_all()

    def move_window(self, widget, event):
        '''Move window'''
        if event.button == 1:
            self.popup_window.begin_move_drag(event.button, 
                                              int(event.x_root), 
                                              int(event.y_root), 
                                              event.time)
    
    def show_window(self, widget, parent_widget):
        '''Show window'''
        parent_rect = parent_widget.get_toplevel().get_allocation()
        print parent_rect.x
        widget.move(parent_rect.x + parent_rect.width/2, parent_rect.y + parent_rect.height/2)
        

