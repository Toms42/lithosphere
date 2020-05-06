# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from pyglet.event import EventDispatcher
from pyglet.window.key import LSHIFT, RIGHT, LEFT

from .node import Node
from .container import Container

class Handle(Node):

    @property
    def width(self):
        width = self.style.width
        if width:
            return width
        else:
            return 0

    @property
    def height(self):
        height = self.style.height
        if height:
            return height
        else:
            return 0
    
    def on_mouse_press(self, x, y, button, modifiers):
        self.root.window.set_exclusive_mouse(True)
        self.add_handler(self)
        return True
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.parent.change(dx)
    
    def on_mouse_release(self, x, y, button, modifiers):
        self.root.window.set_exclusive_mouse(False)
        self.set_mouse_position(
            int(self.rect.x+self.rect.width/2),
            int(self.rect.y+self.rect.height/2),
        )
        self.remove_handler(self)

class Slider(Container, EventDispatcher):
    '''
        The Slider supports three different ways to modify its state
        - Dragging the Handle with the mouse
        - Scrolling the mouse wheel while the slider has focus
        - Pressing left/right while the slider has focus

        all changes are subject to the modifier key LSHIFT, which
        reduces the rate of change to allow for more accurate control
    '''

    normal = 1.0
    slow = 0.02
    modifier = LSHIFT
    right = RIGHT
    left = LEFT

    def __init__(self, id=None, start=0):
        Container.__init__(self, Handle(), id)
        self._value = start

    def get_value(self):
        return self._value
    def set_value(self, value):
        value = float(value)
        if self._value != value:
            self._value = value
            self.dispatch_event('on_change', value)
        if self.root:
            self.layout()
    value = property(get_value, set_value)
   
    @property
    def range(self):
        return float(self.rect.width - self.content.rect.width)

    @property
    def offset(self):
        return int(self.range * self.value)

    @property
    def width(self):
        width = self.style.width
        if width:
            return width
        else:
            return 0

    @property
    def height(self):
        height = self.style.height
        if height:
            return height
        else:
            return 0

    def layout(self):
        self.content.rect.x = self.rect.x + self.offset
        self.content.rect.y = self.rect.y + (self.rect.height - self.content.height) / 2
        self.rect.dirty = False

    def on_change(self, value): pass

    def on_focus(self):
        self.add_handler(self)

    def on_blur(self):
        self.remove_handler(self)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.change(scroll_y)

    def on_key_press(self, symbol, modifiers):
        if symbol == self.right:
            self.change(1)
        elif symbol == self.left:
            self.change(-1)
    
    def change(self, delta):
        if self.root.keys[self.modifier]:
            factor = self.slow
        else:
            factor = self.normal

        value = self.value + (factor*delta)/self.range

        if value < 0:
            value = 0.0
        elif value > 1.0:
            value = 1.0
            
        self.value = value
        self.content.rect.x = self.rect.x + self.offset

Slider.register_event_type('on_change')
