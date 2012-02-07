#!/usr/bin/env python
# -*- coding:utf-8 -*-

import gtk
import pygtk


class MainWindow:
    """docstring for MainWindow"""
    def __init__(self):
        self.window = self.initWindow()
        #self.window.connect("destroy", self.destroy)
        #self.window.connect("size-allocate", self.size_allocate_event)

        self.mainbox  = gtk.HBox()
        self.leftbox  = gtk.VBox()
        self.rightbox = gtk.VBox()


        self.mainbox.pack_start(self.leftbox)
        self.mainbox.pack_start(self.rightbox)

        self.window.add(self.mainbox)

        self.window.show()

        gtk.main()

    def initWindow(self):
        '''init main Window'''
        window = gtk.Window()
        window.set_position(gtk.WIN_POS_CENTER_ALWAYS)

        #设置无边框
        window.set_decorated(False)
        window.set_resizable(False)
        window.set_size_request(600, 400)
        window.set_app_paintable(True)


        #程序logo
        window.set_icon_from_file(ICON + "logo.png")

        #启用RGBA透明支持
        screen   = window.get_screen()
        colormap = screen.get_rgba_colormap()
        if colormap:
            gtk.widget_set_default_colormap(colormap)

        #伸缩
        window.set_geometry_hints(None, 600, 400)
        return window



class CategoryBox(gtk.ScrolledWindow):
    """docstring for CategoryBox"""

    def __init__(self):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.set_shadow_type(gtk.SHADOW_NONE)


if __name__ == '__main__':
    MainWindow()