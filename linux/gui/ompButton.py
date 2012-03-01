#!/usr/bin/python
# -*- coding: utf-8 -*-

import gtk
import cairo
import gobject
import os
from constant import *

class ompButton(gtk.Button):
    """
    oh-my-pasword linux version is myself make widget that button
    """
    
    def __init__(self, icon, name, url):
        """
        init button
        """
        super(ompButton, self).__init__()

        self._icon = icon
        self._name = name
        self._url = url

        self.connect("expose-event", self.expose_button, self._icon, self._name, self._url, id(self))
        self.set_size_request(128, 64)
        
    def expose_button(self, widget, event, icon, name, url, id):
        if icon != None:
            icon_pixbuf = gtk.gdk.pixbuf_new_from_file(icon)
        else:
            icon_pixbuf = gtk.gdk.pixbuf_new_from_file("../data/Web-icon.png")
            
        h_pixbuf = gtk.gdk.pixbuf_new_from_file("../data/button_h.png")
        p_pixbuf = gtk.gdk.pixbuf_new_from_file("../data/button_p.png")

        # select button have background
        select_id = os.environ['ompButtonselect']
        self_id = str(id)

        print 'select_id ' + select_id + ' self_id ' + self_id 
        print cmp(select_id, self_id)


	if widget.state == gtk.STATE_NORMAL:
            if cmp(select_id, self_id) == 1:
                pixbuf = None
            elif cmp(select_id, self_id) == -1:
                pixbuf = None
            else:
                pixbuf = p_pixbuf
	elif widget.state == gtk.STATE_PRELIGHT:
            if cmp(select_id, self_id):
                pixbuf = h_pixbuf
            else:
                pixbuf = p_pixbuf
	elif widget.state == gtk.STATE_ACTIVE:
            pixbuf = p_pixbuf
            os.environ['ompButtonselect'] = self_id

	cr = widget.window.cairo_create()

        x, y = widget.allocation.x, widget.allocation.y

        if pixbuf != None:
	    cr.set_source_pixbuf(pixbuf, x, y)
	    cr.paint()

        cr.set_source_pixbuf(icon_pixbuf.scale_simple(56, 56, gtk.gdk.INTERP_BILINEAR), x, y)
	cr.paint()

	font_size = 26
	color = "#000000"
	x_font = x + 72
	y_font = y + 28

        txt = self._name

	self.draw_font(cr, txt, font_size, color, x_font, y_font)


	font_size =12
	color = "#000000"
	x_font = x + 64
	y_font = y + 46

        txt = self._url

	self.draw_font(cr, txt, font_size, color, x_font, y_font)

	#if widget.get_child() != None:
        #    widget.propagate_expose(widget.get_child(), event)

	return True

    def draw_font(self, cr, txt, font_size, color, x, y):

	cr.set_source_rgb(*self.select_color(color))
	cr.select_font_face(DEFAULT_FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
	cr.set_font_size(font_size)
	cr.move_to(x, y)
	cr.show_text(txt)

    def select_color(self, color):

	if color[0] == '#':
	    color = color[1:]
	(r, g, b) = (int(color[:2], 16),
		     int(color[2:4], 16),
		     int(color[4:], 16))
	return (r / 255.0, g / 255.0, b / 255.0)
        
gobject.type_register(ompButton)



class ompSmallButton(gtk.Button):
    """
    add button
    """
    
    def __init__(self, icon):
        """
        init add button
        """
        super(ompSmallButton, self).__init__()

        self._icon = icon


        self.connect("expose-event", self.expose_button, self._icon)
        self.set_size_request(36, 36)
        
    def expose_button(self, widget, event, icon):
        if icon != None:
            icon_pixbuf = gtk.gdk.pixbuf_new_from_file(icon)
        else:
            icon_pixbuf = gtk.gdk.pixbuf_new_from_file("../data/Web-icon.png")
            
        h_pixbuf = gtk.gdk.pixbuf_new_from_file("../data/button_h.png")
        p_pixbuf = gtk.gdk.pixbuf_new_from_file("../data/button_p.png")
        
	if widget.state == gtk.STATE_NORMAL:
            pixbuf = None
	elif widget.state == gtk.STATE_PRELIGHT:
            pixbuf = h_pixbuf
	elif widget.state == gtk.STATE_ACTIVE:
            pixbuf = p_pixbuf


	cr = widget.window.cairo_create()

        x, y = widget.allocation.x, widget.allocation.y

        # if pixbuf != None:
	#    cr.set_source_pixbuf(pixbuf, x, y)
	#    cr.paint()


        cr.set_source_pixbuf(icon_pixbuf.scale_simple(32, 32, gtk.gdk.INTERP_BILINEAR), x, y)
	cr.paint()

        return True

        
gobject.type_register(ompSmallButton)
        
        


if __name__ == "__main__":
    
    def max_signal(w):
        if window_is_max(w):
            win.unmaximize()
            print "min"
        else:
            win.maximize()
            print "max"


    
    vbox = gtk.VBox()
    vvbox = gtk.VBox()
    hbox = gtk.HBox()
    
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.connect("destroy", gtk.main_quit)
    
    mb = ompButton(None, '1aaaaaaaaa','bbbbbbbbb')
    mb2 = ompButton(None, '2aaaaaaaaa','bbbbbbbbb')
    mb3 = ompButton(None, '3aaaaaaaaa','bbbbbbbbb')
    
    sb = ompSmallButton("../data/add.png")
    sb1 = ompSmallButton("../data/delete.png")
    sb2 = ompSmallButton("../data/settings.png")

    
    vbox.pack_start(mb, False, False)
    vbox.pack_start(mb2, False, False)
    vbox.pack_start(mb3, False, False)


    
    #win.add(vbox)

     # create a new scrolled window.  
    scrolled_window = gtk.ScrolledWindow()  
    #scrolled_window.set_border_width(10)  
  
        # the policy is one of POLICY AUTOMATIC, or POLICY_ALWAYS.  
        # POLICY_AUTOMATIC will automatically decide whether you need  
        # scrollbars, whereas POLICY_ALWAYS will always leave the scrollbars  
        # there. The first one is the horizontal scrollbar, the second, the  
        # vertical.  
    scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)  
  
        # The dialog window is created with a vbox packed into it.  
        #vbox.pack_start(scrolled_window, True, True, 0)  
        #scrolled_window.show()  

    scrolled_window.add_with_viewport(vbox)
    scrolled_window.set_size_request(160, 600)

    #vbox.pack_start(scrolled_window, False, False)
    
    hbox.pack_start(sb, False, False)
    hbox.pack_start(sb1, False, False)
    hbox.pack_start(sb2, False, False)

    vvbox.pack_start(scrolled_window, False, False)
    vvbox.pack_start(hbox, False, False)


    win.add(vvbox)
    print 't'
    win.show_all()
    
    gtk.main()

        
        
