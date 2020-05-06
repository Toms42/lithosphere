# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from .hss import parse, File, Percent, Pixels, Points, Color, Name
from .font import Font

def pick(type, values, default=None):
    for value in values:
        if isinstance(value, type):
            return value
    return default

def pick_keyword(options, values):
    for value in values:
        if value in options:
            return value

def color(resources, values):
    return values[0]

class Horizontal(object):
    def __init__(self, resources, values):
        self.value = values[0]

    def compute(self, node):
        return self.value.compute(node.parent.rect.width)

    def __repr__(self):
        return 'Horizontal(%s)' % self.value

class Vertical(object):
    def __init__(self, resources, values):
        self.value = values[0]

    def compute(self, node):
        return self.value.compute(node.parent.rect.height)
    
    def __repr__(self):
        return 'Vertical(%s)' % self.value

class Spacing(object):
    def __init__(self, resources, values):
        self.value = values[0]

    def compute(self, node):
        if node.orientation == 'horizontal':
            return self.value.compute(node.rect.width)
        else:
            return self.value.compute(node.rect.height)

def background(resources, values):
    file = pick(File, values)
    type = pick_keyword(('image', 'patch'), values)
    color = pick(Color, values) or Color(1.0, 1.0, 1.0, 1.0)

    if file:
        if type == 'image':
            return resources.image(file.name, color)
        elif type == 'patch':
            return resources.patch(file.name, color)
    else:
        return resources.background(color)

class Align(object):
    def __init__(self, resources, values):
        self.values = values
        self.center = 'center' in values
        self.middle = 'middle' in values
        self.baseline = 'baseline' in values

    def compute(self, node):
        return self

    def __repr__(self):
        return 'Align(%s)' % ', '.join(self.values)

class ComputedPadding(object):
    def __init__(self, values):
        self.top, self.right, self.bottom, self.left = values

class Padding(object):
    def __init__(self, resources, values):
        self.top, self.right, self.bottom, self.left = [value.value for value in values]

    @property
    def values(self):
        return self.top, self.bottom, self.left, self.right

    def compute(self, node):
        return self

def font(resources, values):
    name = pick(Name, values)
    size = pick(Points, values, Points(12))
    color = pick(Color, values, Color(1.0, 1.0, 1.0, 1.0)).values
    bold = 'bold' in values
    italic = 'italic' in values
    return Font(resources, name, size, bold, italic, color)

converters = {
    'color': color,
    'font': font,
    'width': Horizontal,
    'height': Vertical,
    'left': Horizontal,
    'right': Horizontal,
    'top': Vertical,
    'bottom': Vertical,
    'background': background,
    'align': Align,
    'spacing': Spacing,
    'padding': Padding,
}

def convert_attributes(resources, attribs):
    for name, value in attribs.items():
        converter = converters[name]
        value = converter(resources, value)
        attribs[name] = value
