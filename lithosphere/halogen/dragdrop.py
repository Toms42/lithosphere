# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from pyglet.event import EventDispatcher

from .container import Container
from .label import Label

class Slot(Container):
    def far(self, dropable):
        if self.state.near:
            self.state.near = False
            if hasattr(self, 'on_far'):
                self.on_far(dropable)

    def near(self, dropable):
        if not self.state.near:
            self.state.near = True
            if hasattr(self, 'on_near'):
                self.on_near(dropable)

    def drop(self, dropable):
        self.content = dropable
        if self != dropable.previous:
            if hasattr(self, 'on_drop'):
                self.on_drop(dropable)

    def layout(self):
        if self.content:
            content = self.content
            rect = self.rect
            top, bottom, left, right = self.padding
            
            content.rect.x = rect.left + (rect.width-left-right-content.rect.width)/2 + left
            content.rect.y = rect.bottom + (rect.height-bottom-top-content.rect.height)/2 + bottom

            content.layout()

        self.rect.dirty = False

class Dropable(Container):
    near = 20.0
    target = Slot

    def __init__(self, content=None, id=None, layer=None):
        Container.__init__(self, content, id)
        self._layer = layer
        self.previous = None

    @property
    def layer(self):
        if self._layer:
            return self._layer
        else:
            return self.root

    def find_slots(self):
        return [slot for slot in self.root.find(self.target) if not slot.content]

    def on_mouse_press(self, x, y, button, modifiers):
        root = self.root
        layer = self.layer
        self.previous = self.parent

        self.slots = self.find_slots()
        root.window.set_exclusive_mouse(True)
        self.add_handler(self)
        self.remove()
        layer.append(self, do_layout=False)
        return True
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.rect.x += dx
        self.rect.y += dy
        if self.content:
            self.content.layout()
       
        center = self.rect.center
        for slot in self.slots:
            if slot.rect.center.distance(center) < self.near:
                slot.near(self)
            else:
                slot.far(self)
    
    def on_mouse_release(self, x, y, button, modifiers):
        self.root.window.set_exclusive_mouse(False)
        self.set_mouse_position(
            int(self.rect.x+self.rect.width/2),
            int(self.rect.y+self.rect.height/2),
        )
        self.remove_handler(self)

        for slot in self.slots:
            slot.far(self)

        center = self.rect.center
        distances = sorted((slot.rect.center.distance(center), slot) for slot in self.slots)
        if distances:
            nearest, slot = distances[0]
            if nearest > self.near:
                slot = None
        else:
            slot = None

        previous = self.previous

        self.remove()
        if slot:
            slot.drop(self)

        if slot != previous:
            if hasattr(self, 'on_drop'):
                self.on_drop(slot)
            
            if previous and hasattr(previous, 'on_remove'):
                self.previous.on_remove(self)
