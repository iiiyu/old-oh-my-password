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
import gobject
from draw import *
from utils import *
import copy

class ListView(gtk.DrawingArea):
    '''List view.'''
    
    SORT_DESCENDING = True
    SORT_ASCENDING = False
    SORT_PADDING_X = 5
	
    def __init__(self):
        '''Init list view.'''
        # Init.
        gtk.DrawingArea.__init__(self)
        self.add_events(gtk.gdk.POINTER_MOTION_MASK)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
        self.add_events(gtk.gdk.ENTER_NOTIFY_MASK)
        self.add_events(gtk.gdk.LEAVE_NOTIFY_MASK)
        self.items = []
        self.cell_widths = []
        self.cell_min_widths = []
        self.cell_min_heights = []
        self.button_press = False
        self.hover_row = None
        self.titles = None
        self.title_offset_y = 0
        self.item_height = 0
        
        # Signal.
        self.connect("expose-event", self.expose_list_view)    
        self.connect("motion-notify-event", self.motion_list_view)
        self.connect("button-press-event", self.button_press_list_view)
        self.connect("button-release-event", self.button_release_list_view)
        self.connect("leave-notify-event", self.leave_list_view)
        
    def add_titles(self, titles, title_height=24):
        '''Add titles.'''
        self.titles = titles
        self.title_select_column = None
        self.title_adjust_column = None
        self.title_separator_width = 2
        self.title_clicks = map_value(self.titles, lambda _: False)
        self.title_sorts = map_value(self.titles, lambda _: self.SORT_DESCENDING)
        self.set_title_height(title_height)
        
    def add_items(self, items):
        '''Add items in list.'''
        # Add new items.
        self.items += items

        # Re-calcuate.
        title_sizes = map_value(self.titles, lambda title: get_content_size(title, DEFAULT_FONT_SIZE))
        sort_pixbuf = theme.get_dynamic_pixbuf("listview/sort_descending.png").get_pixbuf()
        sort_icon_width = sort_pixbuf.get_width() + self.SORT_PADDING_X * 2
        sort_icon_height = sort_pixbuf.get_height()
        
        cell_min_sizes = []
        for item in items:
            sizes = item.get_column_sizes()
            if cell_min_sizes == []:
                cell_min_sizes = sizes
            else:
                for (index, (width, height)) in enumerate(sizes):
                    if self.titles == None:
                        max_width = max([cell_min_sizes[index][0], width])
                        max_height = max([cell_min_sizes[index][1], sort_icon_height, height])
                    else:
                        max_width = max([cell_min_sizes[index][0], title_sizes[index][0] + sort_icon_width * 2, width])
                        max_height = max([cell_min_sizes[index][1], title_sizes[index][1], sort_icon_height, height])
                    
                    cell_min_sizes[index] = (max_width, max_height)
        
        # Get value.
        (cell_min_widths, cell_min_heights) = unzip(cell_min_sizes)
        self.cell_min_widths = mix_list_max(self.cell_min_widths, cell_min_widths)
        self.cell_min_heights = mix_list_max(self.cell_min_heights, cell_min_heights)
        self.cell_widths = mix_list_max(self.cell_widths, copy.deepcopy(cell_min_widths))
            
        self.item_height = max(self.item_height, max(copy.deepcopy(cell_min_heights)))    
                    
        # Set size request.
        if len(self.items) > 0:
            self.set_size_request(sum(self.cell_min_widths), self.item_height * len(self.items) + self.title_offset_y)
            
    def set_title_height(self, title_height):
        '''Set title height.'''
        self.title_height = title_height
        if self.titles:
            self.title_offset_y = self.title_height
        else:
            self.title_offset_y = 0

    def get_column_sort_type(self, column):
        '''Get sort type.'''
        if 0 <= column <= len(self.title_sorts) - 1:
            return self.title_sorts[column]
        else:
            return None
        
    def set_column_sort_type(self, column, sort_type):
        '''Set sort type.'''
        if 0 <= column <= len(self.title_sorts) - 1:
            self.title_sorts[column] = sort_type
            
    def get_cell_widths(self):
        '''Get cell widths.'''
        return self.cell_widths
    
    def set_cell_width(self, column, width):
        '''Set cell width.'''
        if column <= len(self.cell_min_widths) - 1 and width >= self.cell_min_widths[column]:
            self.cell_widths[column] = width
            
    def set_adjust_cursor(self):
        '''Set adjust cursor.'''
        set_cursor(self, gtk.gdk.SB_H_DOUBLE_ARROW)
        self.adjust_cursor = True    
        
    def reset_cursor(self):
        '''Reset cursor.'''
        set_cursor(self, None)
        self.adjust_cursor = False
            
    def get_offset_coordinate(self, widget):
        '''Get offset coordinate.'''
        # Init.
        rect = widget.allocation

        # Get coordinate.
        viewport = get_match_parent(widget, "Viewport")
        if viewport: 
           (offset_x, offset_y) = widget.translate_coordinates(viewport, rect.x, rect.y)
           return (-offset_x, -offset_y, viewport)
        else:
            return (0, 0, viewport)
            
    def expose_list_view(self, widget, event):
        '''Expose list view.'''
        # Init.
        cr = widget.window.cairo_create()
        rect = widget.allocation
        cell_widths = self.get_cell_widths()
        
        # Get offset.
        (offset_x, offset_y, viewport) = self.get_offset_coordinate(widget)
            
        # Draw background.
        pixbuf = theme.get_dynamic_pixbuf(BACKGROUND_IMAGE).get_pixbuf().subpixbuf(
            viewport.allocation.x,
            viewport.allocation.y,
            viewport.allocation.width,
            viewport.allocation.height)
        draw_pixbuf(cr, pixbuf, offset_x, offset_y)
        
        # Draw mask.
        draw_vlinear(cr, offset_x, offset_y, viewport.allocation.width, viewport.allocation.height,
                     theme.get_dynamic_shadow_color("linearBackground").get_color_info())
            
        if len(self.items) > 0:
            # Save cairo status.
            cr.save()
            
            # Don't draw any item under title area.
            cr.rectangle(offset_x, offset_y + self.title_offset_y,
                          viewport.allocation.width, viewport.allocation.height - self.title_offset_y)        
            cr.clip()
            
            # Draw hover row.
            if self.hover_row != None:
                draw_vlinear(cr, offset_x, self.title_offset_y + self.hover_row * self.item_height,
                             viewport.allocation.width, self.item_height,
                             theme.get_dynamic_shadow_color("listviewHover").get_color_info())
            
            
            # Get viewport index.
            start_y = offset_y - self.title_offset_y
            end_y = offset_y + viewport.allocation.height - self.title_offset_y
            start_index = max(start_y / self.item_height, 0)
            if (end_y - end_y / self.item_height * self.item_height) == 0:
                end_index = min(end_y / self.item_height + 1, len(self.items))
            else:
                end_index = min(end_y / self.item_height + 2, len(self.items))        
                
            # Draw list item.
            for (row, item) in enumerate(self.items[start_index:end_index]):
                renders = item.get_renders()
                for (column, render) in enumerate(renders):
                    cell_width = cell_widths[column]
                    cell_x = sum(cell_widths[0:column])
                    render(cr, gtk.gdk.Rectangle(
                            rect.x + cell_x,
                            rect.y + (row + start_index) * self.item_height + self.title_offset_y,
                            cell_width, 
                            self.item_height
                            ))
            
            # Restore cairo status to draw title area.
            cr.restore()        
            
        # Draw titles.
        if self.titles:
            for (column, width) in enumerate(cell_widths):
                # Get offset x coordinate.
                cell_offset_x = sum(cell_widths[0:column])
                
                # Calcuate current cell width.
                if column == len(cell_widths) - 1:
                    if sum(cell_widths) < rect.width:
                        cell_width = rect.width - cell_offset_x
                    else:
                        cell_width = width
                else:
                    cell_width = width
                    
                # Draw title column background.
                if self.title_select_column == column:
                    if self.button_press:
                        shadow_color = "listviewHeaderPress"
                    else:
                        shadow_color = "listviewHeaderSelect"
                else:
                    shadow_color = "listviewHeader"
                draw_vlinear(cr, cell_offset_x, offset_y, cell_width, self.title_height,
                                 theme.get_dynamic_shadow_color(shadow_color).get_color_info())
                
                # Draw sort icon.
                sort_type = self.get_column_sort_type(column)    
                if sort_type == self.SORT_DESCENDING:
                    sort_pixbuf = theme.get_dynamic_pixbuf("listview/sort_descending.png").get_pixbuf()
                elif sort_type == self.SORT_ASCENDING:
                    sort_pixbuf = theme.get_dynamic_pixbuf("listview/sort_ascending.png").get_pixbuf()
                    
                draw_pixbuf(cr, sort_pixbuf,
                            cell_offset_x + cell_width - sort_pixbuf.get_width() - self.SORT_PADDING_X,
                            offset_y + (self.title_height - sort_pixbuf.get_height()) / 2)    
            
            for (column, title) in enumerate(self.titles):
                # Draw title split line.
                cell_x = sum(cell_widths[0:column])
                    
                if cell_x != 0:
                    draw_vlinear(cr, cell_x, offset_y, 1, self.title_height,
                                 theme.get_dynamic_shadow_color("listviewHeaderSplit").get_color_info())
                    
                # Draw title.
                draw_font(cr, title, DEFAULT_FONT_SIZE, 
                          theme.get_dynamic_color("listItemText").get_color(),
                          cell_x, offset_y, cell_widths[column], self.title_height)    
                
        return False
    
    def motion_list_view(self, widget, event):
        '''Motion list view.'''
        if self.titles:
            # Get offset.
            (offset_x, offset_y, viewport) = self.get_offset_coordinate(widget)
            
            if self.title_adjust_column != None:
                # Set column width.
                cell_min_end_x = sum(self.cell_widths[0:self.title_adjust_column]) + self.cell_min_widths[self.title_adjust_column]
                (ex, ey) = get_event_coords(event)
                if ex >= cell_min_end_x:
                    self.set_cell_width(self.title_adjust_column, ex - sum(self.cell_widths[0:self.title_adjust_column]))
            else:
                if offset_y <= event.y <= offset_y + self.title_height:
                    cell_widths = self.get_cell_widths()
                    for (column, _) in enumerate(cell_widths):
                        if column == len(cell_widths) - 1:
                            cell_start_x = widget.allocation.width
                            cell_end_x = widget.allocation.width
                        else:
                            cell_start_x = sum(cell_widths[0:column + 1]) - self.title_separator_width
                            cell_end_x = sum(cell_widths[0:column + 1]) + self.title_separator_width
                            
                        if event.x < cell_start_x:
                            self.title_select_column = column
                            self.reset_cursor()
                            break
                        elif cell_start_x <= event.x <= cell_end_x:
                            self.title_select_column = None
                            self.set_adjust_cursor()
                            break
                elif len(self.items) > 0:
                    # Rest cursor and title select column.
                    self.title_select_column = None
                    self.reset_cursor()
                    
                    # Set hover row.
                    (event_x, event_y) = get_event_coords(event)
                    self.hover_row = (event_y - self.title_offset_y) / self.item_height
                
            # Redraw after motion.
            self.queue_draw()
        elif len(self.items) > 0:
            # Rest cursor and title select column.
            self.title_select_column = None
            self.reset_cursor()
            
            # Set hover row.
            (event_x, event_y) = get_event_coords(event)
            self.hover_row = (event_y - self.title_offset_y) / self.item_height
                
            # Redraw after motion.
            self.queue_draw()
            
    def button_press_list_view(self, widget, event):
        '''Button press event handler.'''
        self.button_press = True                
        if self.titles:
            # Get offset.
            (offset_x, offset_y, viewport) = self.get_offset_coordinate(widget)
            if offset_y <= event.y <= offset_y + self.title_height:
                cell_widths = self.get_cell_widths()
                for (column, _) in enumerate(cell_widths):
                    if column == len(cell_widths) - 1:
                        cell_end_x = widget.allocation.width
                    else:
                        cell_end_x = sum(cell_widths[0:column + 1]) - self.title_separator_width
                        
                    if column == 0:
                        cell_start_x = 0
                    else:
                        cell_start_x = sum(cell_widths[0:column]) + self.title_separator_width
                        
                    if cell_start_x < event.x < cell_end_x:
                        self.title_clicks[column] = True
                        break
                    elif cell_end_x <= event.x <= cell_end_x + self.title_separator_width * 2:
                        self.title_adjust_column = column
                        break
        
        self.queue_draw()

    def button_release_list_view(self, widget, event):
        '''Button release event handler.'''
        self.button_press = False
        if self.titles:
            # Get offset.
            (offset_x, offset_y, viewport) = self.get_offset_coordinate(widget)
            if offset_y <= event.y <= offset_y + self.title_height:
                cell_widths = self.get_cell_widths()
                for (column, _) in enumerate(cell_widths):
                    if column == len(cell_widths) - 1:
                        cell_end_x = widget.allocation.width
                    else:
                        cell_end_x = sum(cell_widths[0:column + 1]) - self.title_separator_width
                        
                    if column == 0:
                        cell_start_x = 0
                    else:
                        cell_start_x = sum(cell_widths[0:column]) + self.title_separator_width
                        
                    if cell_start_x < event.x < cell_end_x:
                        if self.title_clicks[column]:
                            self.title_sorts[column] = not self.title_sorts[column]
                            self.title_clicks[column] = False
                            break
        
        self.title_adjust_column = None
        self.queue_draw()
        
    def leave_list_view(self, widget, event):
        '''leave-notify-event signal handler.'''
        self.title_select_column = None
        self.title_adjust_column = None
        self.reset_cursor()

        self.queue_draw()
        
gobject.type_register(ListView)

class ListItem(object):
    '''List item.'''
    
    def __init__(self, icon_path, title, artist, length, listen_button):
        '''Init list item.'''
        self.update(icon_path, title, artist, length, listen_button)
        
    def update(self, icon_path, title, artist, length, listen_button):
        '''Update.'''
        # Update.
        self.icon_path = icon_path
        self.title = title
        self.artist = artist
        self.length = length
        self.listen_button = listen_button
        
        # Calculate item size.
        self.icon_padding_x = 10
        self.icon_padding_y = 5
        pixbuf = theme.get_dynamic_pixbuf(icon_path).get_pixbuf()
        self.icon_width = pixbuf.get_width()
        self.icon_height = pixbuf.get_height()
    
        self.title_padding_x = 10
        self.title_padding_y = 5
        (self.title_width, self.title_height) = get_content_size(self.title, DEFAULT_FONT_SIZE)
        
        self.artist_padding_x = 10
        self.artist_padding_y = 5
        (self.artist_width, self.artist_height) = get_content_size(self.artist, DEFAULT_FONT_SIZE)

        self.length_padding_x = 10
        self.length_padding_y = 5
        (self.length_width, self.length_height) = get_content_size(self.length, DEFAULT_FONT_SIZE)
        
        pixbuf = theme.get_dynamic_pixbuf(listen_button).get_pixbuf()
        self.listen_width = pixbuf.get_width()
        self.listen_height = pixbuf.get_height()
                
    def render_icon(self, cr, rect):
        '''Render icon.'''
        render_image(cr, rect, self.icon_path,
                     rect.x + (rect.width - self.icon_width) / 2,
                     rect.y + (rect.height - self.icon_height) / 2)
        
    def render_title(self, cr, rect):
        '''Render title.'''
        rect.x += self.title_padding_x
        render_text(cr, rect, self.title)
    
    def render_artist(self, cr, rect):
        '''Render artist.'''
        rect.x += self.artist_padding_x
        render_text(cr, rect, self.artist)
    
    def render_length(self, cr, rect):
        '''Render length.'''
        rect.width -= self.length_padding_x
        render_text(cr, rect, self.length, ALIGN_END)
        
    def render_listen(self, cr, rect):
        '''Render listen.'''
        render_image(cr, rect, self.listen_button,
                     rect.x + (rect.width - self.listen_width) / 2,
                     rect.y + (rect.height - self.listen_height) / 2)
        
    def get_column_sizes(self):
        '''Get sizes.'''
        return [(self.icon_width + self.icon_padding_x * 2, 
                 self.icon_height + self.icon_padding_y * 2),
                (self.title_width + self.title_padding_x * 2, 
                 self.title_height + self.title_padding_y * 2),
                (self.artist_width + self.artist_padding_x * 2, 
                 self.artist_height + self.artist_padding_y * 2),
                (self.length_width + self.length_padding_x * 2, 
                 self.length_height + self.length_padding_y * 2),
                (self.listen_width + self.icon_padding_x * 2, 
                 self.listen_height + self.icon_padding_y * 2)]    
    
    def get_renders(self):
        '''Get render callbacks.'''
        return [self.render_icon, 
                self.render_title,
                self.render_artist,
                self.render_length,
                self.render_listen]

def render_text(cr, rect, content, align=ALIGN_START, font_size=DEFAULT_FONT_SIZE):
    '''Render text.'''
    draw_font(cr, content, font_size, 
              theme.get_dynamic_color("listItemText").get_color(), 
              rect.x, rect.y, rect.width, rect.height, align)
    
def render_image(cr, rect, image_path, x, y):
    '''Render image.'''
    draw_pixbuf(cr, theme.get_dynamic_pixbuf(image_path).get_pixbuf(), x, y)
