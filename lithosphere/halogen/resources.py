# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

import pyglet
from pyglet.gl import *
from .patch import Patch
from .util import TextureRegion, coords, res_open

class Image(object):
    def __init__(self, region, color):
        self.region = region
        self.color = color
        self.t2f = coords(region.top, region.bottom, region.left, region.right)

    def compute(self, node):
        return self
    
    def draw(self, rect):
        v2f = coords(rect.top, rect.bottom, rect.left, rect.right)

        glColor4f(*self.color.values)
        pyglet.graphics.draw(4, GL_QUADS,
            ('v2f', v2f),
            ('t2f', self.t2f),
        )

class Resources(object):
    def __init__(self, width=2048, height=2048):
        self.texture = pyglet.image.Texture.create(width, height, GL_RGBA, mag_filter=GL_NEAREST, min_filter=GL_NEAREST)
        self.allocator = pyglet.image.atlas.Allocator(width, height) #FIXME does only simplistic packing, replace with own

        white = pyglet.image.ImageData(10, 10, 'RGBA', '\xff\xff\xff\xff'*100)
        x, y, self.white = self.allocate(white.width, white.height)
        self.texture.blit_into(white, x, y, 0)

    def allocate(self, width, height):
        x, y = self.allocator.alloc(width, height)
        left = x/float(self.texture.width)
        bottom = y/float(self.texture.height)
        texture_width = width/float(self.texture.width)
        texture_height = height/float(self.texture.height)
        return x, y, TextureRegion(
            top = bottom + texture_height,
            bottom = bottom,
            left = left,
            right = left + texture_width,
        )

    def background(self, color):
        return Image(self.white, color) 

    def image(self, name, color):
        image = pyglet.image.load(name, file=res_open(name))
        x, y, region = self.allocate(image.width, image.height)
        self.texture.blit_into(image, x, y, 0)
        return Image(region, color)

    def patch(self, name, color):
        image = pyglet.image.load(name, file=res_open(name))
        subimg = image.get_region(1, 0, image.width-1, image.height-1)
        x, y, region = self.allocate(subimg.width, subimg.height)
        self.texture.blit_into(subimg, x, y, 0)
        return Patch(image, region, color)

    def font(self, name, size, bold):
        return Font(self, name, size, bold)         
