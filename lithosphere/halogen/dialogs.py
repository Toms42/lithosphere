# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""
import os
import re

from pyglet.event import EventDispatcher
from pyglet.window.key import ESCAPE

from .rowcol import Column, Row
from .label import Label
from .widget import Widget
from .workspace import Workspace
from .scrollable import Scrollable
from .button import Button
from .input import Input

class File(Label):
    def __init__(self, name, dialog):
        self.dialog = dialog
        self.name = name
        Label.__init__(self, name)

    def on_mouse_press(self, x, y, button, modifiers):
        self.dialog.name.text = self.name
        return True

class Directory(Label):
    def __init__(self, name, dialog):
        self.dialog = dialog
        self.name = name
        Label.__init__(self, name)

    def on_mouse_press(self, x, y, button, modifiers):
        self.dialog.go_dir(self.name)
        return True

class Dialog(Workspace, EventDispatcher):
    def show(self):
        self.saved_root.append(self)
        self.add_handler(self.on_key_press)
        self.show_dir()

    def go_up(self):
        self.path = os.path.dirname(self.path)
        self.show_dir()

    def go_dir(self, name):
        self.path = os.path.join(self.path, name)
        self.show_dir()
    
    def show_dir(self):
        file_col = self.file_col
        file_col.items = []
        file_col.refresh()
        for name in sorted(os.listdir(self.path)):
            if not name.startswith('.'):
                if os.path.isdir(os.path.join(self.path, name)):
                    Directory(name, self).append_to(file_col, update=False)
                else:
                    if self.pattern.match(name):
                        File(name, self).append_to(file_col, update=False)

        file_col.refresh()
        self.scrollable.scroll = 0
        self.layout_content(self.widget)

    def hide(self):
        self.remove_handler(self.on_key_press)
        self.remove()

    def on_mouse_press(self, x, y, button, modifiers):
        return True

    def on_key_press(self, symbol, modifiers):
        if symbol == ESCAPE:
            self.hide()
            return True
    
    def action(self):
        name = self.name.text
        full_path = os.path.join(self.path, name)
        self.dispatch_event('on_file', full_path)
        self.hide()

Dialog.register_event_type('on_file')

class FileOpen(Dialog):
    def __init__(self, root, pattern='.*', id=None):
        Workspace.__init__(self, id) 
        self.path = os.path.expanduser('~')

        self.saved_root = root
        self.pattern = re.compile(pattern)

        col = Column()
        Button('up').append_to(col).on_click = self.go_up
        self.file_col = Column()
        row = Row().append_to(col)
        Label('File:').append_to(row)
        self.name = Label('', id='filename').append_to(row)
        self.scrollable = Scrollable(self.file_col).append_to(col)
        row = Row().append_to(col)
        Button('Cancel').append_to(row).on_click = self.hide
        Button('Open').append_to(row).on_click = self.action
        
        self.widget = Widget('File Open', col, dragable=False).append_to(self)

class FileSave(Dialog):
    def __init__(self, root, pattern='.*', id=None):
        Workspace.__init__(self, id) 
        self.path = os.path.expanduser('~')

        self.saved_root = root
        self.pattern = re.compile(pattern)

        col = Column()
        Button('up').append_to(col).on_click = self.go_up
        self.file_col = Column()
        row = Row().append_to(col)
        Label('File:').append_to(row)
        self.name = Input(id='filename').append_to(row)
        self.scrollable = Scrollable(self.file_col).append_to(col)
        row = Row().append_to(col)
        Button('Cancel').append_to(row).on_click = self.hide
        Button('Save').append_to(row).on_click = self.action
        
        self.widget = Widget('File Save', col, dragable=False).append_to(self)
