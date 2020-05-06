# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from pyglet.event import EventDispatcher

from .container import Container
from .label import Label

class Button(Container, EventDispatcher):
    def __init__(self, content=None, id=None):
        if isinstance(content, str):
            content = Label(content)
        Container.__init__(self, content, id)
    
    def on_mouse_press(self, x, y, button, modifiers):
        self.state.pressed = True
        self.add_handler(self)
        return True
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.rect.hit(x, y):
            self.state.pressed = True
        else:
            self.state.pressed = False
    
    def on_mouse_release(self, x, y, button, modifiers):
        rect = self.absolute_rect
        self.state.pressed = False
        self.remove_handler(self)
        if rect.hit(x, y):
            self.dispatch_event('on_click')
        else:
            self.state.hover = False

    def on_click(self): pass

Button.register_event_type('on_click')
