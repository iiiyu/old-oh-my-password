#!/usr/bin/python
# -*- coding: utf-8 -*-

import gtk
import cairo
import gobject



class ompButton(gtk.Button):
    """
    """
    
    def __init__(self):
        """
        """
        super(ompButton, self).__init__()

        icon = 'test'
        name = 'testname'
        url = 'testurl'

        self.connect("expose-event", self.expose_button, icon, name, url)
        self.set_size_request(128, 64)
        

    def expose_button(self, widget, event, icon, name, url):
        
	icon_pixbuf = gtk.gdk.pixbuf_new_from_file("Web-icon.png")
        h_pixbuf = gtk.gdk.pixbuf_new_from_file("button_h.png")
        p_pixbuf = gtk.gdk.pixbuf_new_from_file("button_p.png")
        
	if widget.state == gtk.STATE_NORMAL:
            print 'a'
            pixbuf = None
	elif widget.state == gtk.STATE_PRELIGHT:
            pixbuf = h_pixbuf
            print 'b'
	elif widget.state == gtk.STATE_ACTIVE:
            pixbuf = p_pixbuf
            print 'c'



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

        txt = 'tdfgdsfgdsfgdsfgsdfgsdfgest'

	self.draw_font(cr, txt, font_size, color, x_font, y_font)


	font_size =12
	color = "#000000"
	x_font = x + 64
	y_font = y + 46

        txt = 'aaaaaaaaaaaaaa'

	self.draw_font(cr, txt, font_size, color, x_font, y_font)

	#if widget.get_child() != None:
	#    widget.propagate_expose(widget.get_child(), event)

	return True

    def draw_font(self, cr, txt, font_size, color, x, y):

	cr.set_source_rgb(*self.select_color(color))
	cr.select_font_face("Purisa", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
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


if __name__ == "__main__":
    
    def max_signal(w):    
        if window_is_max(w):
            win.unmaximize()
            print "min"
        else:
            win.maximize()
            print "max"


    vbox = gtk.VBox()
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.connect("destroy", gtk.main_quit)
    mb = ompButton()
    mb2 = ompButton()
    mb3 = ompButton()
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

    win.add(scrolled_window)

   
    win.show_all()
    
    gtk.main()

        
        
