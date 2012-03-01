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

import gtk
import cairo
import pangocairo
import os
import threading as td
from constant import *
import time

def tree_view_get_toplevel_node_count(treeview):
    '''Get toplevel node count.'''
    model = treeview.get_model()
    if model != None:
        return model.iter_n_children(None)
    else:
        return 0
    
def tree_view_get_selected_path(treeview):
    '''Get selected path.'''
    selection = treeview.get_selection()
    (_, tree_paths) = selection.get_selected_rows()
    if len(tree_paths) != 0:
        return (tree_paths[0])[0]
    else:
        return None
 
def tree_view_focus_first_toplevel_node(treeview):
    '''Focus first toplevel node.'''
    treeview.set_cursor((0))
    
def tree_view_focus_last_toplevel_node(treeview):
    '''Focus last toplevel node.'''
    node_count = tree_view_get_toplevel_node_count(treeview)
    if node_count > 0:
        path = (node_count - 1)
    else:
        path = (0)
    treeview.set_cursor(path)
    
def tree_view_scroll_vertical(treeview, scroll_up=True):
    '''Scroll tree view vertical.'''
    # Init.
    scroll_num = 9
    candidate_count = tree_view_get_toplevel_node_count(treeview)
    cursor = treeview.get_cursor()
    (path, column) = cursor
    max_candidate = candidate_count - 1
    
    # Get candidate at cursor.
    if path == None:
        current_candidate = max_candidate
    else:
        (current_candidate,) = path
        
    # Set cursor to new candidate.
    if scroll_up:
        new_candidate = max(0, current_candidate - scroll_num)
    else:
        new_candidate = min(current_candidate + scroll_num, max_candidate)
        
    treeview.set_cursor((new_candidate))
    
def tree_view_focus_next_toplevel_node(treeview):
    '''Focus next toplevel node.'''
    selected_path = tree_view_get_selected_path(treeview)
    if selected_path != None:
        node_count = tree_view_get_toplevel_node_count(treeview)
        if selected_path < node_count - 1:
            treeview.set_cursor((selected_path + 1))

def tree_view_focus_prev_toplevel_node(treeview):
    '''Focus previous toplevel node.'''
    selected_path = tree_view_get_selected_path(treeview)
    if selected_path != None:
        if selected_path > 0:
            treeview.set_cursor((selected_path - 1))

def get_entry_text(entry):
    '''Get entry text.'''
    return entry.get_text().split(" ")[0]

def set_cursor(widget, cursor_type=None):
    '''Set cursor.'''
    if cursor_type == None:
        widget.window.set_cursor(None)
    else:
        widget.window.set_cursor(gtk.gdk.Cursor(cursor_type))
    
    return False

def get_widget_root_coordinate(widget, pos_type=WIDGET_POS_BOTTOM_CENTER):
    '''Get widget's root coordinate.'''
    # Get coordinate.
    (wx, wy) = widget.window.get_origin()
    toplevel_window = widget.get_toplevel()
    if toplevel_window:
        (x, y) = widget.translate_coordinates(toplevel_window, wx, wy)
    else:
        (x, y) = (wx, wy)
        
    # Get offset.
    rect = widget.allocation
    if pos_type == WIDGET_POS_TOP_LEFT:
        offset_x = 0
        offset_y = 0
    elif pos_type == WIDGET_POS_TOP_RIGHT:
        offset_x = rect.width
        offset_y = 0
    elif pos_type == WIDGET_POS_TOP_CENTER:
        offset_x = rect.width / 2
        offset_y = 0
    elif pos_type == WIDGET_POS_BOTTOM_LEFT:
        offset_x = 0
        offset_y = rect.height
    elif pos_type == WIDGET_POS_BOTTOM_RIGHT:
        offset_x = rect.width
        offset_y = rect.height
    elif pos_type == WIDGET_POS_BOTTOM_CENTER:
        offset_x = rect.width / 2
        offset_y = rect.height
    elif pos_type == WIDGET_POS_LEFT_CENTER:
        offset_x = 0
        offset_y = rect.height / 2
    elif pos_type == WIDGET_POS_RIGHT_CENTER:
        offset_x = rect.width
        offset_y = rect.height / 2
        
    return (x + offset_x, y + offset_y)

def get_event_root_coords(event):
    '''Get event root coordinates.'''
    (rx, ry) = event.get_root_coords()
    return (int(rx), int(ry))

def get_event_coords(event):
    '''Get event coordinates.'''
    (rx, ry) = event.get_coords()
    return (int(rx), int(ry))

def propagate_expose(widget, event):
    '''Propagate expose to children.'''
    if "get_child" in dir(widget) and widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)
        
def move_window(widget, event, window):
    '''Move window.'''
    window.begin_move_drag(
        event.button, 
        int(event.x_root), 
        int(event.y_root), 
        event.time)
    
    return False
    
def resize_window(widget, event, window, get_edge):
    '''Resize window.'''
    edge = get_edge()
    if edge:
        window.begin_resize_drag(
            edge,
            event.button,
            int(event.x_root),
            int(event.y_root),
            event.time)
        
    return False

def add_in_scrolled_window(scrolled_window, widget, shadow_type=gtk.SHADOW_NONE):
    '''Like add_with_viewport in ScrolledWindow, with shadow type.'''
    scrolled_window.add_with_viewport(widget)
    viewport = scrolled_window.get_child()
    if viewport != None:
        viewport.set_shadow_type(shadow_type)
    else:
        print "add_in_scrolled_window: Impossible, no viewport widget in ScrolledWindow!"

def is_double_click(event):
    '''Whether an event is double click?'''
    return event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS

def container_remove_all(container):
    '''Remove all child widgets from container.'''
    container.foreach(lambda widget: container.remove(widget))
    
def get_screen_size(widget):
    '''Get widget's screen size.'''
    screen = widget.get_screen()
    width = screen.get_width()
    height = screen.get_height()
    return (width, height)

def is_in_rect((cx, cy), (x, y, w, h)):
    '''Whether coordinate in rectangle.'''
    return (cx >= x and cx <= x + w and cy >= y and cy <= y + h)

def scroll_to_top(scrolled_window):
    '''Scroll scrolled window to top.'''
    scrolled_window.get_vadjustment().set_value(0)

def get_font_y_coordinate(y, height, font_size):
    '''Get font y coordinate.'''
    return y + (height + font_size) / 2 - int(font_size / 8)

def get_content_size(content, font_size):
    '''Get content size.'''
    if content:
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1000, 1000) # 1000 should be enough 
        cr = cairo.Context(surface)
        if DEFAULT_FONT in get_font_families():
            cr.select_font_face(DEFAULT_FONT,
                                cairo.FONT_SLANT_NORMAL, 
                                cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(font_size)
        width = cr.text_extents(content)[2]
        
        return (int(width), font_size)
    else:
        return (0, font_size)

def remove_file(path):
    '''Remove file.'''
    if os.path.exists(path):
        os.remove(path)
        
def remove_directory(path):
    """equivalent to rm -rf path"""
    for i in os.listdir(path):
        full_path = os.path.join(path, i)
        if os.path.isdir(full_path):
            remove_directory(full_path)
        else:
            os.remove(full_path)
    os.rmdir(path)        

def touch_file(filepath):
    '''Touch file.'''
    # Create directory first.
    dir = os.path.dirname(filepath)
    if not os.path.exists(dir):
        os.makedirs(dir)
        
    # Touch file.
    open(filepath, "w").close()

def read_file(filepath, check_exists=False):
    '''Read file.'''
    if check_exists and not os.path.exists(filepath):
        return ""
    else:
        r_file = open(filepath, "r")
        content = r_file.read()
        r_file.close()
        
        return content

def read_first_line(filepath, check_exists=False):
    '''Read first line.'''
    if check_exists and not os.path.exists(filepath):
        return ""
    else:
        r_file = open(filepath, "r")
        content = r_file.readline().split("\n")[0]
        r_file.close()
        
        return content

def eval_file(filepath, check_exists=False):
    '''Eval file content.'''
    if check_exists and not os.path.exists(filepath):
        return None
    else:
        try:
            read_file = open(filepath, "r")
            content = eval(read_file.read())
            read_file.close()
            
            return content
        except Exception, e:
            print e
            
            return None

def write_file(filepath, content):
    '''Write file.'''
    f = open(filepath, "w")
    f.write(content)
    f.close()

def kill_process(proc):
    '''Kill process.'''
    try:
        if proc != None:
            proc.kill()
    except Exception, e:
        pass
    
def get_command_output_first_line(commands):
    '''Run command and return result.'''
    process = subprocess.Popen(commands, stdout=subprocess.PIPE)
    process.wait()
    return process.stdout.readline()

def get_command_output(commands):
    '''Run command and return result.'''
    process = subprocess.Popen(commands, stdout=subprocess.PIPE)
    process.wait()
    return process.stdout.readlines()
    
def run_command(command):
    '''Run command.'''
    subprocess.Popen("nohup %s > /dev/null 2>&1" % (command), shell=True)
    
def get_os_version():
    '''Get OS version.'''
    version_infos = get_command_output_first_line(["lsb_release", "-i"]).split()
    
    if len(version_infos) > 0:
        return version_infos[-1]
    else:
        return ""

def get_current_time():
    '''Get current time.'''
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

def add_in_list(e_list, element):
    '''Add element in list.'''
    if not element in e_list:
        e_list.append(element)
        
def remove_from_list(e_list, element):
    '''Remove element from list.'''
    if element in e_list:
        e_list.remove(element)
        
def sort_alpha(e_list):
    '''Get alpha list.'''
    return sorted(e_list, key=lambda e: e)

def get_dir_size(dirname):
    '''Get directory size.'''
    total_size = 0
    for root, dirs, files in os.walk(dirname):
        for filepath in files:
            total_size += os.path.getsize(os.path.join(root, filepath))
            
    return total_size

def print_env():
    '''Print environment variable.'''
    for param in os.environ.keys():
        print "*** %20s %s" % (param,os.environ[param])                

def print_exec_time(func):
    '''Print execute time.'''
    def wrap(*a, **kw):
        start_time = time.time()
        ret = func(*a, **kw)
        print "%s time: %s" % (str(func), time.time() - start_time)
        return ret
    return wrap

def get_font_families():
    '''Get all font families in system.'''
    fontmap = pangocairo.cairo_font_map_get_default()
    return map (lambda f: f.get_name(), fontmap.list_families())

def format_file_size(bytes, precision=2):
    '''Returns a humanized string for a given amount of bytes'''
    bytes = int(bytes)
    if bytes is 0:
        return '0B'
    else:
        log = math.floor(math.log(bytes, 1024))
        quotient = 1024 ** log
        size = bytes / quotient
        remainder = bytes % quotient
        if remainder < 10 ** (-precision): 
            prec = 0
        else:
            prec = precision
        return "%.*f%s" % (prec,
                           size,
                           ['B', 'KB', 'MB', 'GB', 'TB','PB', 'EB', 'ZB', 'YB']
                           [int(log)])

def add_color_stop_rgba(pat, pos, color_info):
    '''ADd color stop RGBA.'''
    (color, alpha) = color_info
    (r, g, b) = color_hex_to_cairo(color)
    pat.add_color_stop_rgba(pos, r, g, b, alpha)
    
def alpha_color_hex_to_cairo((color, alpha)):
    '''Alpha color hext to cairo color.'''
    (r, g, b) = color_hex_to_cairo(color)
    return (r, g, b, alpha)

def color_hex_to_cairo(color):
    """ 
    Convert a html (hex) RGB value to cairo color. 
     
    @type color: html color string 
    @param color: The color to convert. 
    @return: A color in cairo format. 
    """ 
    if color[0] == '#': 
        color = color[1:] 
    (r, g, b) = (int(color[:2], 16), 
                    int(color[2:4], 16),  
                    int(color[4:], 16)) 
    return color_rgb_to_cairo((r, g, b)) 

def color_rgb_to_cairo(color): 
    """ 
    Convert a 8 bit RGB value to cairo color. 
     
    @type color: a triple of integers between 0 and 255 
    @param color: The color to convert. 
    @return: A color in cairo format. 
    """ 
    return (color[0] / 255.0, color[1] / 255.0, color[2] / 255.0) 

def get_match_parent(widget, matchType):
    '''Get parent widget match given type, otherwise return None.'''
    parent = widget.get_parent()
    if parent == None:
        return None
    elif type(parent).__name__ == matchType:
        return parent
    else:
        return get_match_parent(parent, matchType)
        
def widget_fix_cycle_destroy_bug(widget):
    '''Fix bug that PyGtk destroys cycle too early.'''
    # This code to fix PyGtk bug <<Pygtk destroys cycle too early>>, 
    # The cycle is wrongly freed 
    # by Python's GC because Pygobject does not tell Python that the widget's 
    # wrapper object is referenced by the underlying GObject.  As you have 
    # found, in order to break the cycle Python zeros out the callback 
    # closure's captured free variables, which is what causes the "referenced 
    # before assignment" exception. 
    # detail see: https://bugzilla.gnome.org/show_bug.cgi?id=546802 .
    # 
    # Otherwise, will got error : "NameError: free variable 'self' referenced before assignment in enclosing scope".
    widget.__dict__

def map_value(value_list, get_value_callback):
    '''Map value.'''
    if value_list == None:
        return []
    else:
        return map(get_value_callback, value_list)

def get_match_widgets(widget, type_name):
    '''Get widget match given type, those widget at same level with widget argument.'''
    parent = widget.get_parent()
    if parent == None:
        return []
    else:
        return filter(lambda w:type(widget).__name__ == type_name, parent.get_children())

def mix_list_max(list_a, list_b):
    '''Mix max item in two list.'''
    if list_a == []:
        return list_b
    elif list_b == []:
        return list_a
    elif len(list_a) == len(list_b):
        result = []
        for (index, item_a) in list_a:
            if item_a > list_b[index]:
                result.append(item_a)
            else:
                result.append(list_b[index])
        
        return result        
    else:
        print "mix_list_max: two list's length not same."
        return []

def unzip(unzip_list):
    '''Unzip [(1, 'a'), (2, 'b'), (3, 'c')] to ([1, 2, 3], ['a', 'b', 'c']).'''
    first_list, second_list = zip(*unzip_list)
    return (list(first_list), list(second_list))

def window_is_max(widget):
    '''Whether window is maximized status.'''
    toplevel_window = widget.get_toplevel()
    if toplevel_window.window.get_state() == gtk.gdk.WINDOW_STATE_MAXIMIZED:
        return True
    else:
        return False

