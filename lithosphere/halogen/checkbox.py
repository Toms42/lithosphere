# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from pyglet.event import EventDispatcher

from .node import Node
from .label import Label

class Checkbox(Node, EventDispatcher):
    def __init__(self, checked=False, id=None):
        Node.__init__(self, id)
        if checked:
            self.check()

    @property
    def checked(self):
        return bool(self.state.on)
    
    def on_mouse_press(self, x, y, button, modifiers):
        self.toggle()
        return True

    def check(self):
        self.state.on = True
        self.dispatch_event('on_change', True)
        self.dispatch_event('on_check')

    def uncheck(self):
        self.state.on = False
        self.dispatch_event('on_change', False)
        self.dispatch_event('on_uncheck')

    def toggle(self):
        if self.state.on:
            self.uncheck()
        else:
            self.check()
    
    def on_change(self, state): pass
    def on_check(self): pass
    def on_uncheck(self): pass

Checkbox.register_event_type('on_change')
Checkbox.register_event_type('on_check')
Checkbox.register_event_type('on_uncheck')
