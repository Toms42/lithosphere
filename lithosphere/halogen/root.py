# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from pyglet.gl import *
from pyglet.window import key

from .area import Area
from .style import Sheet
from .resources import Resources

class Root(Area):
    def __init__(self, window, sheet):
        Area.__init__(self)
        self.window = window
        self.keys = key.KeyStateHandler()
        window.push_handlers(self.keys)
        window.push_handlers(self.events)
        window.push_handlers(self.on_resize)
        self.resources = Resources()
        if isinstance(sheet, str):
            sheet = Sheet(self.resources, sheet)
        self.sheet = sheet
        self.compute_style(sheet)

    def draw(self):
        texture = self.resources.texture

        glPushAttrib(GL_ENABLE_BIT | GL_TEXTURE_BIT)
        glEnable(GL_CULL_FACE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(texture.target)
        glBindTexture(texture.target, texture.id)
        
        Area.draw(self)
        
        glBindTexture(texture.target, 0)
        glPopAttrib()

    @property
    def root(self):
        return self

    @property
    def width(self):
        return self.window.width

    @property
    def height(self):
        return self.window.height

    def set_mouse_position(self, x, y):
        self.window.set_mouse_position(x, y)
    
    def absolute_coords(self, x, y):
        return x, y

    def on_resize(self, width, height):
        #does not work right on minimize/maximize
        self.refresh()
