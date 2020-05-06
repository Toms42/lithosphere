# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

import pyglet
from pyglet.gl import *
from string import ascii_letters, digits, punctuation

ascii = ascii_letters + digits + punctuation

def convert(glyph):
    data = glyph.get_image_data()
    bytes = data.get_data('A', data.width)
    result = ''
    for c in bytes:
        result += chr(255) + chr(255) + chr(255) + c

    if glyph.tex_coords[1] > glyph.tex_coords[7]:
        return pyglet.image.ImageData(data.width, data.height, 'RGBA', result, data.width*4)
    else:
        return pyglet.image.ImageData(data.width, data.height, 'RGBA', result, -data.width*4)

class Glyph(object):
    def __init__(self, region, baseline, bearing, advance, width, height):
        self.region = region
        self.baseline = baseline
        self.bearing = bearing
        self.advance = advance
        self.width = width
        self.height = height

class Font(object):
    '''
        Linux 15pt: Font(height=21, bottom=5)
        Linux 10pt: Font(height=13, bottom=3)
    '''
    def __init__(self, resources, name, size, bold, italic, color):
        self.color = color
        self.font = font = pyglet.font.load(name.value, size=size.value, bold=bold, italic=italic)
        self.glyphs = {}
        self.resources = resources
        
        top = 0
        bottom = 0
        for char, glyph in zip(ascii, font.get_glyphs(ascii)):
            data = convert(glyph)
            advance = glyph.advance
            bearing = glyph.vertices[0]
            baseline = -glyph.vertices[1]
            top = max(top, data.height-baseline)
            bottom = min(bottom, -baseline)
            x, y = resources.allocator.alloc(data.width, data.height)
            region = resources.texture.get_region(x, y, data.width, data.height)
            resources.texture.blit_into(data, x, y, 0)
            self.glyphs[char] = Glyph(region, baseline, bearing, advance, data.width, data.height)
        self.height = top - bottom
        self.bottom = - bottom

    def get_glyph(self, char):
        glyph = self.glyphs.get(char)
        if not glyph:
            glyph = self.font.get_glyphs(char)[0]
            data = convert(glyph)
            advance = glyph.advance
            bearing = glyph.vertices[0]
            baseline = -glyph.vertices[1]
            x, y = self.resources.allocator.alloc(data.width, data.height)
            region = self.resources.texture.get_region(x, y, data.width, data.height)
            self.resources.texture.blit_into(data, x, y, 0)
            glyph = self.glyphs[char] = Glyph(region, baseline, bearing, advance, data.width, data.height)
        return glyph

    @property
    def word_spacing(self):
        return self.height/2

    def compute_width(self, text):
        lines = text.split('\n')

        result = 0
        for line in lines:
            width = 0
            for c in line:
                if c == ' ':
                    width += self.word_spacing
                else:
                    glyph = self.get_glyph(c)
                    #width += glyph.bearing + glyph.advance
                    width += glyph.advance
            result = max(result, width)

        return result

    def compute(self, node):
        return self

    def __repr__(self):
        return 'Font(height=%i, bottom=%i)' % (self.height, self.bottom)
