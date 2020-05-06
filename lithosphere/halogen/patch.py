# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from ctypes import c_char_p, c_ubyte, pointer, cast, byref, c_char, create_string_buffer, c_float, Structure, POINTER, c_void_p
from .util import TextureRegion, coords
from pyglet.gl import *

class ImageData(object):
    def __init__(self, image):
        self.data = image.data
        self.width = image.texture.width
        self.height = image.texture.height
        self.pitch = image.pitch
        class Pixel(Structure): pass
        Pixel._fields_ = [(c, c_ubyte) for c in image.format.lower()]
        array_type = Pixel*(self.width*self.height)
        self.array = cast(c_char_p(image.data), POINTER(array_type)).contents

    def get(self, x, y):
        if self.pitch > 0:
            return self.array[x+y*self.width] 
        else:
            return self.array[x+(self.height-y-1)*self.width] 


    def __getitem__(self, (x,y)):
        if isinstance(x, slice):
            return [
                self.get(ix, y)
                for ix in range(x.start or 0, x.stop or self.width)
            ]
        elif isinstance(y, slice):
            return [
                self.get(x, iy)
                for iy in range(y.start or 0, y.stop or self.height)
            ]
        else:
            return self.get(x, y)

def borders(image):
    data = ImageData(image)
    top = 0
    bottom = 0
    left = 0
    right = 0

    vertical = data[0,:]
    i = 0
    
    while i < data.height:
        if vertical[i].a > 0:
            bottom = i
            break
        i+=1

    
    while i < data.height:
        if vertical[i].a == 0:
            top = data.height - i
            break
        i+=1
    
    horizontal = data[:,data.height-1]
    i = 0

    while i < data.width:
        if horizontal[i].a > 0:
            left = i
            break
        i+=1

    while i < data.width:
        if horizontal[i].a == 0:
            right = data.width - i
            break
        i+=1

    return top-1, bottom, left-1, right

class Patch(object):
    def __init__(self, image, outer, color):
        self.color = color
        self.outer = outer
        self.borders = top, bottom, left, right = borders(image)
        x_scale = outer.width / image.width
        y_scale = outer.height / image.height

        self.inner = inner = TextureRegion(
            top = outer.top - top * y_scale,
            bottom = outer.bottom + bottom * y_scale,
            left = outer.left + left * x_scale,
            right = outer.right - right * x_scale,
        )

        self.t2f = []
        if bottom:
            self.t2f.extend(coords(inner.bottom, outer.bottom, inner.left, inner.right))
            if left:
                self.t2f.extend(coords(inner.bottom, outer.bottom, outer.left, inner.left))
            if right:
                self.t2f.extend(coords(inner.bottom, outer.bottom, inner.right, outer.right))
        if top:
            self.t2f.extend(coords(outer.top, inner.top, inner.left, inner.right))
            if left:
                self.t2f.extend(coords(outer.top, inner.top, outer.left, inner.left))
            if right:
                self.t2f.extend(coords(outer.top, inner.top, inner.right, outer.right))
        if left:
            self.t2f.extend(coords(inner.top, inner.bottom, outer.left, inner.left))
        if right:
            self.t2f.extend(coords(inner.top, inner.bottom, inner.right, outer.right))
        self.t2f.extend(coords(inner.top, inner.bottom, inner.left, inner.right))

    def compute(self, node):
        return self

    def draw(self, rect):
        top, bottom, left, right = self.borders
        v2f = []

        if bottom:
            v2f.extend(coords(rect.bottom+bottom, rect.bottom, rect.left+left, rect.right-right))
            if left:
                v2f.extend(coords(rect.bottom+bottom, rect.bottom, rect.left, rect.left+left))
            if right:
                v2f.extend(coords(rect.bottom+bottom, rect.bottom, rect.right-right, rect.right))
        if top:
            v2f.extend(coords(rect.top, rect.top-top, rect.left+left, rect.right-right))
            if left:
                v2f.extend(coords(rect.top, rect.top-top, rect.left, rect.left+left))
            if right:
                v2f.extend(coords(rect.top, rect.top-top, rect.right-right, rect.right))
        if left:
            v2f.extend(coords(rect.top-top, rect.bottom+bottom, rect.left, rect.left+left))
        if right:
            v2f.extend(coords(rect.top-top, rect.bottom+bottom, rect.right-right, rect.right))
        v2f.extend(coords(rect.top-top, rect.bottom+bottom, rect.left+left, rect.right-right))

        glColor4f(*self.color.values)
        pyglet.graphics.draw(len(v2f)/2, GL_QUADS,
            ('v2f', v2f),
            ('t2f', self.t2f),
        )
