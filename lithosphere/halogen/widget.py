# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from .rowcol import Column
from .label import Label
from .area import Area
from .container import Container

class Bar(Container):
    def __init__(self, caption, dragable=True):
        self.dragable = dragable

        if isinstance(caption, str):
            Container.__init__(self, Label(caption))
        else:
            Container.__init__(self, caption)
    
    def on_mouse_press(self, x, y, button, modifiers):
        if self.dragable:
            self.mouse_off = x - self.rect.x, y - self.rect.y
            self.root.window.set_exclusive_mouse(True)
            self.add_handler(self)
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        widget = self.parent
        widget.rect.x += dx
        widget.rect.y += dy
        widget.layout()
    
    def on_mouse_release(self, x, y, button, modifiers):
        x, y = self.mouse_off
        self.root.window.set_exclusive_mouse(False)
        self.set_mouse_position(
            int(self.rect.x+x),
            int(self.rect.y+y),
        )
        self.remove_handler(self)

class Content(Container): pass

class Widget(Column):
    def __init__(self, caption, content=None, id=None, dragable=True):
        Column.__init__(self, id=id)
        Bar(caption, dragable).append_to(self)
        self._content = Content(content).append_to(self)

    def on_mouse_press(self, x, y, button, modifiers):
        self.parent.rise(self)
        return True

    def get_content(self):
        return self._content.content
    def set_content(self, content):
        self._content.content = content

    content = property(get_content, set_content)
    del set_content, get_content
        
