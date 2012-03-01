#! /usr/bin/env python
# -*- coding: utf-8 -*-


from application import Application
from constant import *
from menu import *
from navigatebar import *
from statusbar import *
from categorybar import *
from scrolledWindow import *
from box import *
from button import *
from listview import *
from tooltip import *
from popupWindow import *
from ompButton import *



if __name__ == "__main__":
    # Init application.
    application = Application()
    
    # Set application default size.
    application.set_default_size(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
    
    # Set application icon.
    application.set_icon("icon.ico")
    
    # Draw application background.
    application.set_background(BACKGROUND_IMAGE)
    button = gtk.Button()
    button.set_size_request(200,300)
    # Init menu callback.
    menu = Menu(
        [("menu/menuItem1.png", "测试测试测试1", lambda :PopupWindow(application.window)),
         ("menu/menuItem2.png", "测试测试测试2", None),
         ("menu/menuItem3.png", "测试测试测试3", None),
         None,
         (None, "测试测试测试", None),
         (None, "测试测试测试", None),
         None,
         ("menu/menuItem6.png", "测试测试测试4", None),
         ("menu/menuItem7.png", "测试测试测试5", None),
         ("menu/menuItem8.png", "测试测试测试6", None),
         ])
    application.set_menu_callback(lambda button: menu.show(get_widget_root_coordinate(button)))
    
    
    # Add body box.
    body_box = gtk.HBox()
    application.main_box.pack_start(body_box, True, True)
    os.environ['ompButtonselect'] = '0'
    
    category_box = gtk.HBox()
    body_box.add(category_box)

    vbox = gtk.VBox()
    vvbox = gtk.VBox()
    hbox = gtk.HBox()
    
    mb = ompButton(None, '1aaaaaaaaaasdfasdfasdf','bbbbbbbbb')
    mb2 = ompButton(None, '2aaaaaaaaa','bbbbbbbbb')
    mb3 = ompButton(None, '3aaaaaaaaa','bbbbbbbbb')
    
    sb = ompSmallButton("../data/add.png")
    sb1 = ompSmallButton("../data/delete.png")
    sb2 = ompSmallButton("../data/settings.png")

    
    vbox.pack_start(mb, False, False)
    vbox.pack_start(mb2, False, False)
    vbox.pack_start(mb3, False, False)

    hbox.pack_start(sb, False, False)
    hbox.pack_start(sb1, False, False)
    hbox.pack_start(sb2, False, False)

    for i in range(10):
        testmb = ompButton(None, 'aa', 'bb')
        vbox.pack_start(testmb, False, False)
        print i
        

    # Add scrolled window.
    scrolled_window = ScrolledWindow()
    category_box.pack_start(vvbox, False, False)
    vvbox.pack_start(scrolled_window, False, False)
    vvbox.pack_start(hbox, False, False)

    scrolled_window.add_child(vbox)

    scrolled_window.set_size_request(160, 540)
    

    
    # Add statusbar.
    statusbar = Statusbar(36)
    application.main_box.pack_start(statusbar.status_event_box, False)
    application.add_move_window_event(statusbar.status_event_box)
    application.add_toggle_window_event(statusbar.status_event_box)
    
    # Run.
    application.run()

