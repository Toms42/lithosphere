# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from .hss import parse, Pixels
from .matchers import parse_matchers, Part
from .attributes import convert_attributes

class Rule(object):
    def __init__(self, parts, attributes):
        self.attributes = attributes
        self.parts = parts

    def match(self, node):

        parts = list(self.parts)
        while parts and node:
            part = parts.pop(0)
            node = part.apply(node)

        if node:
            return self.attributes
        else:
            return {}

    def __repr__(self):
        return 'Rule(%s)' % ', '.join(map(str, self.parts))

inheritable = set([
    'color',
    'font',
])

class Style(object):
    def __init__(self, node, sheet):
        self.__dict__.update(dict(
            node = node,
            sheet = sheet,
            direct = {},
        ))

    def get(self, name, default=None):
        value = self.direct.get(name)
        if value is None:
            value = self.sheet.get(name)
            if value is None and name in inheritable:
                value = self.node.parent.style.get(name)

        if value:
            return value.compute(self.node)
        else:
            return default

    def __getattr__(self, name):
        return self.get(name)
    def __setattr__(self, name, value):
        if isinstance(value, (int, float)):
            value = Pixels(value)
        self.direct[name] = value
        self.node.rect.dirty = True
        self.node.update()

    def __repr__(self):
        return '\n'.join('%s: %s' % (name, value) for name, value in self.sheet.items())

class Sheet(object):
    def __init__(self, resources, path):
        self.resources = resources
        self.rules = []
        for matchers, attribs in parse(path, self.convert):
            matchers = parse_matchers(matchers)
            self.rules.append(Rule(matchers, attribs))
    
    def style(self, node):
        data = {}
        for rule in self.rules:
            data.update(rule.match(node))
        return Style(node, data)
    
    def convert(self, attributes):
        return convert_attributes(self.resources, attributes)
