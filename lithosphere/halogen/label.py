# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

import pyglet
from pyglet.gl import *

from node import Node

class Label(Node):
    def __init__(self, text, id=None):
        Node.__init__(self, id)
        self._text = text

    def get_text(self):
        return self._text
    def set_text(self, text):
        self._text = text
        self.update()

    text = property(get_text, set_text)
    del get_text, set_text

    @property
    def width(self):
        width = self.style.width
        if width:
            return width
        else:
            return self.style.font.compute_width(self.text)

    @property
    def height(self):
        height = self.style.height
        if height:
            return height
        else:
            return (self.text.count('\n')+1) * self.style.font.height

    def layout(self):
        font = self.style.font
        x = self.rect.x
        y = self.rect.top - font.height

        align = self.style.align
        if align:
            if align.baseline:
                align = 0
            elif align.middle:
                align = font.bottom
        else:
            align = 0

        self.v2f = []
        self.t2f = []
        self.c4f = []
        self.caret_positions = []

        self.count = 0
        for i, c in enumerate(self.text):
            self.caret_positions.append(x)
            if c == ' ':
                x += font.word_spacing
            elif c == '\n':
                x = self.rect.x
                y -= font.height
            else:
                self.count += 4
                glyph = font.get_glyph(c)
                left = x+glyph.bearing
                right = left + glyph.width
                bottom = y - glyph.baseline + align
                top = bottom + glyph.height

                self.v2f.extend([
                    left, bottom,
                    right, bottom,
                    right, top,
                    left, top,
                ])
                tc = glyph.region.tex_coords
                left, right, top, bottom = tc[0], tc[3], tc[7], tc[1]
                self.t2f.extend([
                    left, top,
                    right, top,
                    right, bottom,
                    left, bottom,
                ])
                x += glyph.advance
        self.caret_positions.append(x)

    def draw(self):
        self.draw_background()
        glColor4f(*self.style.font.color)
        pyglet.graphics.draw(self.count, GL_QUADS,
            ('v2f', self.v2f),
            ('t2f', self.t2f),
        )

    def __repr__(self):
        return 'Label(%s)' % self.text
