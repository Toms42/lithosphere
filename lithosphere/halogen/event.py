# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

class State(object):
    def __init__(self, node):
        self.__dict__.update(dict(
            _node = node,
        ))
        
        self._hover = False
        self._focus = False
        self._pressed = False

    def __contains__(self, name):
        return getattr(self, name, False)

    def __setattr__(self, name, value):
        old = getattr(self, name)
        if old != value:
            self.__dict__[name] = value
            self._node.refresh()

    def __getattr__(self, name):
        return False

class Event(object):
    def __init__(self, node):
        self.state = node.state
        self.rect = node.rect
        self.node = node

    def on_mouse_press(self, x, y, button, modifiers):
        self.blur() #maybe not the best solution but works for now
        if self.rect.hit(x, y):
            self.focus()
            self.state.pressed = True
            subx, suby = self.node.translate_coords(x, y)
            for child in list(self.node)[::-1]:
                if child.events.on_mouse_press(subx, suby, button, modifiers):
                    return True
            if hasattr(self.node, 'on_mouse_press'):
                if self.node.on_mouse_press(x, y, button, modifiers):
                    return True

    def on_mouse_motion(self, x, y, dx, dy):
        if self.rect.hit(x, y):
            if not self.state.hover:
                self.on_mouse_enter(x, y)
                self.state.hover = True
            x, y = self.node.translate_coords(x, y)
            for child in self.node:
                child.events.on_mouse_motion(x, y, dx, dy)
        else:
            if self.state.hover:
                self.on_mouse_leave(x, y)
                self.state.hover = False
                x, y = self.node.translate_coords(x, y)
                for child in self.node:
                    child.events.on_mouse_motion(x, y, dx, dy)
    
    def on_mouse_enter(self, x, y):
        if hasattr(self.node, 'on_mouse_enter'):
            self.node.on_mouse_enter(x, y)

    def on_mouse_leave(self, x, y):
        if hasattr(self.node, 'on_mouse_leave'):
            self.node.on_mouse_leave(x, y)

    def focus(self):
        if not self.state.focus:
            self.state.focus = True
            if hasattr(self.node, 'on_focus'):
                self.node.on_focus()

    def blur(self):
        if self.state.focus:
            self.state.focus = False
            if hasattr(self.node, 'on_blur'):
                self.node.on_blur()
            for child in self.node:
                child.events.blur()
