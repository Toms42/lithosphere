# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

class Part(object):
    def __init__(self, _class, meta):
        self._class = _class
        self.meta = meta

    def match(self, node):
        if self._class:
            has_class = self._class in node.classes
        else:
            has_class = True

        if self.meta:
            has_meta = self.meta in node.state
        else:
            has_meta = True

        return has_meta and has_class

class TypePart(Part):
    def __init__(self, name, _class=None, meta=None):
        Part.__init__(self, _class, meta)
        self.name = name

    def match(self, node):
        return node.__class__.__name__ == self.name and Part.match(self, node)
    
    def __repr__(self):
        return self.name

class IDPart(Part):
    def __init__(self, name, _class=None, meta=None):
        Part.__init__(self, _class, meta)
        self.name = name

    def match(self, node):
        if node.id:
            return node.id == self.name and Part.match(self, node)
        else:
            return False

    def __repr__(self):
        return '#' + self.name

class Is(object):
    def __init__(self, part):
        self.part = part

    def apply(self, node):
        if self.part.match(node):
            return node
    
    def __repr__(self):
        return 'Is(%s)' % self.part

class HasParent(object):
    def __init__(self, part):
        self.part = part
    def apply(self, node):
        if self.part.match(node.parent):
            return node.parent
    
    def __repr__(self):
        return 'HasParent(%s)' % self.part

class FindParent(object):
    def __init__(self, part):
        self.part = part
    def apply(self, node):
        while node.parent:
            if self.part.match(node.parent):
                return node.parent
            else:
                node = node.parent
    
    def __repr__(self):
        return 'FindParent(%s)' % self.part
    
def parse_part(matchers):
    main = matchers.pop()
   
    if matchers and matchers[-1] == ':':
        meta = main
        matchers.pop()
        main = matchers.pop()
    else:
        meta = None

    if matchers and matchers[-1] == '.':
        _class = main
        matchers.pop()
        main = matchers.pop()
    else:
        _class = None
    
    if main.startswith('#'):
        return IDPart(main[1:], _class, meta)
    else:
        return TypePart(main, _class, meta)

def split_class(parts):
    for part in parts:
        if '.' in part:
            items = part.split('.')
            yield items[0]
            yield '.'
            yield items[1]
        else:
            yield part

def parse_matchers(matchers):
    matchers = list(split_class(matchers))
    result = [Is(parse_part(matchers))]
    while matchers:
        if matchers[-1] == '>':
            matchers.pop()
            result.append(
                HasParent(parse_part(matchers))
            )
        else:
            result.append(
                FindParent(parse_part(matchers))
            )
    return result
