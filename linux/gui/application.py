#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang Yong
# 
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
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

from menu import *
from constant import *
from titlebar import Titlebar
from draw import *
from threads import *
import gtk
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import sys

class UniqueService(dbus.service.Object):
    def __init__(self, start_callback):
        bus_name = dbus.service.BusName(APPLICATION_DBUS_NAME, bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, APPLICATION_OBJECT_NAME)
        self.start_callback = start_callback
 
    @dbus.service.method(dbus_interface=APPLICATION_SERVICE_NAME)
    def show_window(self):
        self.start_callback()

class Application(object):
    '''Application.'''
	
    def __init__(self, check_unique=True):
        '''Init application.'''
        # Init.
        self.check_unique = check_unique
        
        # Check unique when option `check_unique` is enable.
        if check_unique:
            # Init dbus. 
            DBusGMainLoop(set_as_default=True)
            bus = dbus.SessionBus()
            if bus.request_name(APPLICATION_DBUS_NAME) != dbus.bus.REQUEST_NAME_REPLY_PRIMARY_OWNER:
                # Call 'show_window` method when have exist instance.
                method = bus.get_object(APPLICATION_SERVICE_NAME, APPLICATION_OBJECT_NAME).get_dbus_method("show_window")
                method()
                
                # Exit program.
                sys.exit()
                
        # Start application.
        self.init()

    def init(self):
        '''Init.'''
        # Init gdk threads, the integrant method for multi-thread GUI application.
        gtk.gdk.threads_init()

        # Init status.
        self.cursor_type = None
        self.menu_button_callback = None
        
        # Init window.
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_decorated(False)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.add_events(gtk.gdk.KEY_RELEASE_MASK)
        self.window.add_events(gtk.gdk.POINTER_MOTION_MASK)
        self.window.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.window.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
        self.window.set_colormap(gtk.gdk.Screen().get_rgba_colormap())
        self.window.connect("size-allocate", draw_window_shape)
        self.window.connect("destroy", self.destroy)
        self.window.connect("motion-notify-event", self.motion_notify)
        self.window.connect("button-press-event", lambda w, e: resize_window(w, e, self.window, self.get_edge))
        
        # Init main box.
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
        self.frame_vbox.pack_start(self.top_line, False, False)
        self.frame_vbox.pack_start(self.frame_hbox, True, True) 
        self.frame_vbox.pack_start(self.bottom_line, False, False)
        self.frame_hbox.pack_start(self.left_line, False, False)
        self.frame_hbox.pack_start(self.main_box, True, True)
        self.frame_hbox.pack_start(self.right_line, False, False)
        self.window.add(self.frame_vbox)
        
        # Init titlebar.
        self.titlebar = Titlebar()
        self.titlebar.theme_button.connect("clicked", self.theme_callback)
        self.titlebar.menu_button.connect("clicked", self.menu_callback)
        self.titlebar.min_button.connect("clicked", self.min_callback)
        self.titlebar.max_button.connect("clicked", self.max_callback)
        self.titlebar.close_button.connect("clicked", self.close_callback)
        self.add_toggle_window_event(self.titlebar.drag_box)
        self.add_move_window_event(self.titlebar.drag_box)
        self.main_box.pack_start(self.titlebar.box, False)
        
    @post_gui
    def raise_to_top(self):
        '''Raise to top.'''
        self.window.present()
        
    def set_title(self, title):
        '''Set application title.'''
        self.window.set_title(title)

    def set_default_size(self, default_width, default_height):
        '''Set application default size.'''
        self.window.set_default_size(default_width, default_height)
        self.window.set_geometry_hints(
            None,
            default_width,       # minimum width
            default_height       # minimum height
            -1, -1, -1, -1, -1, -1, -1, -1
            )

    def set_icon(self, icon_path):
        '''Set icon.'''
        gtk.window_set_default_icon(theme.get_dynamic_pixbuf(icon_path).get_pixbuf())
        
    def set_background(self, background_path):
        '''Set background path.'''
        draw_window_background(self.window, background_path)    
    
    def destroy(self, widget, data=None):
        '''Destroy main window.'''
        gtk.main_quit()

    def run(self):
        '''Run.'''
        # Init DBus when option `check_unique` is enable.
        if self.check_unique:
            DBusGMainLoop(set_as_default=True)
            UniqueService(self.raise_to_top)
        
        # Show window.
        self.window.show_all()
        
        # Run main loop.
        gtk.main()

    def theme_callback(self, widget):
        '''Theme button callback.'''
        return False
    
    def menu_callback(self, widget):
        '''Menu button callback.'''
        if self.menu_button_callback:
            self.menu_button_callback(widget)
        
        return False
    
    def min_callback(self, widget):
        '''Min button callback.'''
        self.window.iconify()

        return False

    def max_callback(self, widget):
        '''Max button callback.'''
        self.toggle_window()
    
        return False
    
    def close_callback(self, widget):
        '''Close button callback.'''
        # Hide window immediately when user click close button,
        # user will feeling this software very quick, ;p
        self.window.hide_all()

        self.destroy(self.window)
    
        return False
    
    def double_click_window(self, widget, event):
        '''Handle double click on window.'''
        if is_double_click(event):
            self.toggle_window()
            
        return False
            
    def toggle_window(self):
        '''Toggle window.'''
        window_state = self.window.window.get_state()
        if window_state == gtk.gdk.WINDOW_STATE_MAXIMIZED:
            self.window.unmaximize()
        else:
            self.window.maximize()
        
    def add_toggle_window_event(self, widget):
        '''Add toggle window event.'''
        widget.connect("button-press-event", self.double_click_window)
    
    def add_move_window_event(self, widget):
        '''Add move window event.'''
        widget.connect('button-press-event', lambda w, e: move_window(w, e, self.window))
        
    def motion_notify(self, widget, event):
        '''Callback for motion-notify event.'''
        self.cursor_type = self.get_cursor_type(event)
        set_cursor(self.window, self.cursor_type)
        
    def get_edge(self):
        '''Get edge.'''
        if EDGE_DICT.has_key(self.cursor_type):
            return EDGE_DICT[self.cursor_type]
        else:
            return None
        
    def set_menu_callback(self, callback):
        '''Set menu callback.'''
        self.menu_button_callback = callback
        
    def get_cursor_type(self, event):
        '''Get cursor position.'''
        # Get event coordinate.
        (ex, ey) = get_event_root_coords(event)
        
        # Get window allocation.
        rect = self.window.get_allocation()
        (wx, wy) = self.window.get_position()
        ww = rect.width
        wh = rect.height
        
        # Return cursor position. 
        if wx <= ex <= wx + DRAG_OFFSET:
            if wy <= ey <= wy + DRAG_OFFSET * 2:
                return gtk.gdk.TOP_LEFT_CORNER
            elif wy + wh - (DRAG_OFFSET * 2) <= ey <= wy + wh:
                return gtk.gdk.BOTTOM_LEFT_CORNER
            elif wy + DRAG_OFFSET < ey < wy + wh - DRAG_OFFSET:
                return gtk.gdk.LEFT_SIDE
            else:
                return None
        elif wx + ww - DRAG_OFFSET <= ex <= wx + ww:
            if wy <= ey <= wy + DRAG_OFFSET * 2:
                return gtk.gdk.TOP_RIGHT_CORNER
            elif wy + wh - (DRAG_OFFSET * 2) <= ey <= wy + wh:
                return gtk.gdk.BOTTOM_RIGHT_CORNER
            elif wy + DRAG_OFFSET < ey < wy + wh - DRAG_OFFSET:
                return gtk.gdk.RIGHT_SIDE
            else:
                return None
        elif wx + DRAG_OFFSET < ex < wx + ww - DRAG_OFFSET:
            if wy <= ey <= wy + DRAG_OFFSET:
                return gtk.gdk.TOP_SIDE
            elif wy + wh - DRAG_OFFSET <= ey <= wy + wh:
                return gtk.gdk.BOTTOM_SIDE
            else: 
                return None
        else:
            return None
