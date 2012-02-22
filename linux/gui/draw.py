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
from theme import theme
from math import pi
from utils import *
from constant import *
import math

def draw_window_shape(widget, rect):
    '''Update shape.'''
    if rect.width > 0 and rect.height > 0:
        # Init.
        w, h = rect.width, rect.height
        bitmap = gtk.gdk.Pixmap(None, w, h, 1)
        cr = bitmap.cairo_create()
        
        # Clear the bitmap
        cr.set_source_rgb(0.0, 0.0, 0.0)
        cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.paint()
        
        # Draw our shape into the bitmap using cairo
        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.set_operator(cairo.OPERATOR_OVER)
        draw_round_rectangle(cr, 0, 0, w, h, WINDOW_RADIUS)
        cr.fill()

        # Shape with given mask.
        widget.shape_combine_mask(bitmap, 0, 0)
        
        # Redraw.
        widget.queue_draw()     # import to redraw interface

def draw_round_rectangle(cr, x, y, width, height, r):
    '''Draw round rectangle.'''
    # Top side.
    cr.move_to(x + r, y)
    cr.line_to(x + width - r, y)
    
    # Top-right corner.
    cr.arc(x + width - r, y + r, r, pi * 3 / 2, pi * 2)
    
    # Right side.
    cr.line_to(x + width, y + height - r)
    
    # Bottom-right corner.
    cr.arc(x + width - r, y + height - r, r, 0, pi / 2)
    
    # Bottom side.
    cr.line_to(x + r, y + height)
    
    # Bottom-left corner.
    cr.arc(x + r, y + height - r, r, pi / 2, pi)
    
    # Left side.
    cr.line_to(x, y + r)
    
    # Top-left corner.
    cr.arc(x + r, y + r, r, pi, pi * 3 / 2)

    # Close path.
    cr.close_path()

def draw_pixbuf(cr, pixbuf, x=0, y=0, alpha=1.0):
    '''Draw pixbuf.'''
    if pixbuf != None:
        cr.set_source_pixbuf(pixbuf, x, y)
        cr.paint_with_alpha(alpha)
        
def draw_window_frame(cr, rect, radius=WINDOW_RADIUS, draw_frame=True, draw_frame_light=True):
    '''Draw window frame.'''
    # Draw frame light.
    if draw_frame_light:
        cr.set_source_rgba(*alpha_color_hex_to_cairo(theme.get_dynamic_alpha_color("frameLight").get_color_info()))
        cr.set_operator(cairo.OPERATOR_OVER)
        draw_round_rectangle(cr, 1, 1, rect.width - 2, rect.height - 2, radius)
        cr.stroke()
    
    # Draw frame.
    if draw_frame:
        cr.set_source_rgba(*alpha_color_hex_to_cairo(theme.get_dynamic_alpha_color("frame").get_color_info()))
        cr.set_operator(cairo.OPERATOR_OVER)
        draw_round_rectangle(cr, 0, 0, rect.width, rect.height, radius)
        cr.stroke()
        
def draw_window_background(widget, background_path, alpha=0.0, mask_dcolor="windowMask"):
    '''Draw expose background.'''
    widget.connect_after("expose-event", lambda w, e: expose_window_background(w, e, background_path, alpha, mask_dcolor))
    
def expose_window_background(widget, event, background_path, alpha, mask_dcolor):
    '''Expose background.'''
    # Init.
    cr = widget.window.cairo_create()
    pixbuf = theme.get_dynamic_pixbuf(background_path).get_pixbuf()
    rect = widget.allocation
    
    # Draw background.
    draw_pixbuf(cr, pixbuf)
    
    # Draw mask.
    cr.set_source_rgb(*color_hex_to_cairo(theme.get_dynamic_color(mask_dcolor).get_color()))
    cr.rectangle(0, 0, rect.width, rect.height)    
    cr.paint_with_alpha(alpha)
    
    # Draw frame light.
    cr.set_source_rgba(*alpha_color_hex_to_cairo(theme.get_dynamic_alpha_color("frameLight").get_color_info()))
    cr.set_operator(cairo.OPERATOR_OVER)
    draw_round_rectangle(cr, 1, 1, rect.width - 2, rect.height - 2, WINDOW_RADIUS)
    cr.stroke()
    
    # Draw frame.
    cr.set_source_rgba(*alpha_color_hex_to_cairo(theme.get_dynamic_alpha_color("frame").get_color_info()))
    cr.set_operator(cairo.OPERATOR_OVER)
    draw_round_rectangle(cr, 0, 0, rect.width, rect.height, WINDOW_RADIUS)
    cr.stroke()
    
    # Propagate expose.
    propagate_expose(widget, event)
    
    return True

def draw_font(cr, content, font_size, font_color, x, y, width, height, x_align=ALIGN_MIDDLE, y_align=ALIGN_MIDDLE):
    '''Draw font.'''
    # Set font face.
    if DEFAULT_FONT in get_font_families():
        cr.select_font_face(DEFAULT_FONT,
                            cairo.FONT_SLANT_NORMAL, 
                            cairo.FONT_WEIGHT_NORMAL)
    # Set font size.
    cr.set_font_size(font_size)
    
    # Get font size.
    font_height = font_size
    font_width = cr.text_extents(content)[2]
    
    # Set font color.
    cr.set_source_rgb(*color_hex_to_cairo(font_color))
    
    # Set font coordinate.
    if x_align == ALIGN_START:
        font_x = x
    elif x_align == ALIGN_END:
        font_x = x + width - font_width
    else:
        font_x = x + (width - font_width) / 2
        
    if y_align == ALIGN_START:
        fontY = y
    elif y_align == ALIGN_END:
        fontY = y + height
    else:
        fontY = y + (height + font_height) / 2
    cr.move_to(font_x, fontY - int(font_size) / 8)

    # Show font.
    cr.show_text(content)

def draw_line(cr, start_x, start_y, end_x, end_y, single=False, vertical=False):
    '''Draw line, just use `single` option when you need draw single-pixel line.'''
    # Adjust coordinate when draw single-pixel line.
    # It's a cairo trick: you need adjusting the endpoints by 0.5 in the appropriate direction
    # to draw single-pixel line, otherwise you will got 2-pixel line.
    # Detail to see: http://www.cairographics.org/FAQ/#sharp_lines
    if single:
        if vertical:
            start_x += 0.5
            end_x += 0.5
        else:
            start_y += 0.5
            end_y += 0.5
            
        cr.set_line_width(1)
            
    # Draw.
    cr.move_to(start_x, start_y)
    cr.line_to(end_x, end_y)

def draw_vlinear(cr, x, y, w, h, color_infos, radius=0):
    '''Draw linear rectangle.'''
    pat = cairo.LinearGradient(0, y, 0, y + h)
    for (pos, color_info) in color_infos:
        add_color_stop_rgba(pat, pos, color_info)
    cr.set_source(pat)
    draw_round_rectangle(cr, x, y, w, h, radius)
    cr.fill()

def draw_hlinear(cr, x, y, w, h, color_infos, radius=0):
    '''Draw linear rectangle.'''
    pat = cairo.LinearGradient(x, 0, x + w, 0)
    for (pos, color_info) in color_infos:
        add_color_stop_rgba(pat, pos, color_info)
    cr.set_source(pat)
    draw_round_rectangle(cr, x, y, w, h, radius)
    cr.fill()
    
def expose_linear_background(widget, event, color_infos):
    '''Expose linear background.'''
    # Init.
    cr = widget.window.cairo_create()
    rect = widget.allocation
    
    # Draw linear background.
    draw_vlinear(cr, rect.x, rect.y, rect.width, rect.height, color_infos)
    
    # Propagate expose.
    propagate_expose(widget, event)
    
    return True

def draw_radial_round(cr, x, y, r, color_infos):
    '''Draw radial round.'''
    radial = cairo.RadialGradient(x, y, r, x, y, 0)
    for (pos, color_info) in color_infos:
        add_color_stop_rgba(radial, pos, color_info)
    cr.arc(x, y, r, 0, 2 * math.pi)
    cr.set_source(radial)
    cr.fill()
    
