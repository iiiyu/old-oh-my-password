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


from draw import *


class CheckBox(gtk.Button):
    '''Check.'''
	
    def __init__(self):
        '''Init.'''        
        gtk.Button.__init__(self)
        self._checked = False
        self._size = 20,20
        self._motion = False
        
        self.add_events(gtk.gdk.POINTER_MOTION_MASK)
        # Init checkbox width and height
        self.set_size_request(20, 20)
        self.connect("expose-event", self.expose_checkbox)
        self.connect("enter-notify-event", self.enter_notify_checkbox)
        self.connect("leave-notify-event", self.leave_notify_checkbox)
        self.connect("button-press-event", self.button_press_checkbox)
        
    def expose_checkbox(self, widget, event):
        '''Expose radio.'''
        cr = widget.window.cairo_create()
        rect = widget.allocation
        self.draw_checkbox(cr, rect.x, rect.y, rect.width, rect.height)
        return True
        
    def draw_checkbox(self, cr, x, y, w, h):    
        '''Draw checkbox.'''     
        # CheckBox linear.
        if self._motion:
            draw_vlinear(cr, x, y, w, h, theme.get_dynamic_shadow_color("hSeparator").get_color_info())
        
        # Checkbox border
        cr.set_source_rgb(0, 0.3, 0)
        draw_round_rectangle(cr, x+2, y+2, w-4, h-4, 0.5)
        cr.stroke()
            
        cr.set_source_rgb(1,1,1)
        cr.rectangle(x+3, y+3, w-6, h-6)
        cr.fill()

        #Checkbox border white background.
        #draw_vlinear(cr, x+3, y+3, w-6, h-6, theme.get_dynamic_shadow_color("progressbarLight").get_color_info())
        
        # Draw radio checked.
        if self.checked:
            #draw_radial_round(cr, x+w/2, y+h/2, w/6, theme.get_dynamic_shadow_color("progressbarForeground").get_color_info())
            cr.set_source_rgb(0,1,0)
            cr.line_to(20,20)
            cr.move_to(x+w,y+h)
            cr.stroke()
            
    def leave_notify_checkbox(self, widget, event):
        self._motion = False
        print 'leave checkbox event'

    def button_press_checkbox(self, widget, event):
        '''Press checkbox'''
        if event.button == 1:
            self.checked = (not self._checked)
            self._motion = True
            print 'clicked checkbox event %s' % self.checked

    def enter_notify_checkbox(self, widget, event):
        '''Press checkbox.'''
        self._motion = True
        print 'motion checkbox event'
        
    
    # set radio size(width, height).
    @property
    def size(self):
        return self._size    
    
    @size.setter
    def size(self, (width,height)):
        '''Set checked width and height.'''
        self._size = width, height
        self.set_size_request(width, height)
        
    @size.getter
    def size(self):
        '''Get checked width and height.'''
        return self._size
    
    @size.deleter
    def size(self):
        del self._size
    
    # Set radio checked.
    @property
    def checked(self):
        return self._checked
    
    @checked.setter
    def checked(self, radio_bool):
        '''Checked radio'''
        self._checked = radio_bool
        self.queue_draw()
        
    @checked.getter
    def checked(self):
        return self._checked

    @checked.deleter
    def checked(self):
        del self._checked
    
        
if __name__ == "__main__":
    window = gtk.Window()    
    fixed  = gtk.Fixed()
    
    checkbox = CheckBox()
    checkbox1 = CheckBox()
    checkbox2 = CheckBox()

    checkbox.size = 85, 85
    checkbox1.size = 30, 30
    checkbox2.size = 20,20
    fixed.put(checkbox,  30, 40)
    fixed.put(checkbox1, 30, 130)
    fixed.put(checkbox2, 30, 180)

    window.add(fixed)
    window.set_size_request(300, 300)
    window.connect("destroy", lambda w: gtk.main_quit())
    
    window.show_all()
    gtk.main()

        