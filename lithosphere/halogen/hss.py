# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

import os
from .hsl import hsl2rgb
from .util import res_open

def tokenize(source):
    token = ''

    for c in source:
        if c in '\t ':
            if token:
                yield token
                token = ''
            continue
        elif c in '()>:;{},':
            if token:
                yield token
                token = ''
            yield c
        elif c == '\n':
            if token:
                yield token
                token = ''
            yield c
        else:
            token += c
    if token:
        yield token

def comments(tokens):
    for token in tokens:
        if token == '/*':
            while token != '*/':
                token = tokens.next()
        elif token == '//':
            while token != '\n':
                token = tokens.next()
        elif token != '\n':
            yield token

def convert_values(values):
    result = []
    for value in values:
        if value.endswith('pt'):
            value = Points(int(value[:-2]))
        elif value.endswith('px'):
            value = Pixels(int(value[:-2]))
        elif value.endswith('%'):
            value = Percent(float(value[:-1]))
        elif value.isdigit():
            value = int(value)
        elif value[0].isdigit() or value[-1].isdigit():
            value = float(value)
        result.append(value)
    return result

class Color(object):
    def __init__(self, colorspace='rgb', r=0.0, g=0.0, b=0.0, a=1.0):
        if colorspace == 'hsl':
            r, g, b = hsl2rgb(r, g, b)
        self.r, self.g, self.b, self.a = r, g, b, a

    @property
    def values(self):
        return (self.r, self.g, self.b, self.a)

    def compute(self, node):
        return self.values

    def __repr__(self):
        return 'Color(%s %s %s %s)' % self.values

class File(object):
    def __init__(self, location, path):
        self.location = location
        self.path = path

    @property
    def name(self):
        if self.path.startswith('/'):
            return self.path
        else:
            return os.path.abspath(os.path.join(self.location, self.path))

    def __repr__(self):
        return 'File(%s)' % self.name

class Pixels(object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return 'Pixels(%s)' % self.value

    def compute(self, value):
        return self.value

class Percent(object):
    def __init__(self, value):
        self.value = value/100.0

    def __repr__(self):
        return 'Percent(%s)' % self.value

    def compute(self, value):
        return int(self.value * value)

class Points(object):
    def __init__(self, value):
        self.value = value
    
    def __repr__(self):
        return 'Points(%s)' % self.value

class Name(object):
    def __init__(self, name):
        self.value = name

    def __repr__(self):
        return 'Name(%s)' % self.value

function_objs = {
    'hsl': lambda location, name, *args: Color(name, *args),
    'rgb': lambda location, name, *args: Color(name, *args),
    'file': lambda location, name, *args: File(location, *args),
    'name': lambda location, name, *args: Name(' '.join(args))
}

def functions(location, values):
    result = []
    token = values.pop(0)
    while 1:
        if token == '(':
            name = result.pop(-1)
            args = pop_until(values, ')')
            result.append(
                function_objs[name](location, name, *args)
            )
        else:
            result.append(token)
        if values:
            token = values.pop(0)
        else:
            break
    return result

def collect_until(tokens, terminator):
    result = []
    token = tokens.next()
    while token != terminator:
        result.append(token)
        token = tokens.next()
    return result

def pop_until(items, terminator):
    result = []
    token = items.pop(0)
    while token != terminator:
        result.append(token)
        token = items.pop(0)
    return result

def attribute(location, items):
    name = pop_until(items, ':')[0].replace('-', '_')
    values = convert_values(pop_until(items, ';'))
    values = functions(location, values)
    return name, values

def split_by(items, separator):
    result = [[]]
    for item in items:
        if item == separator:
            result.append([])
        else:
            result[-1].append(item)
    return result

def rule(location, tokens, converter):
    matchers = collect_until(tokens, '{')
    matchers = split_by(matchers, ',')
    contents = collect_until(tokens, '}')
    attribs = {}
    while contents:
        name, values = attribute(location, contents)
        attribs[name] = values
   
    converter(attribs)
    return [(matcher, attribs) for matcher in matchers]

def parse(path, converter):
    #source = open(path).read()
    source = res_open(path).read()
    location = os.path.dirname(os.path.abspath(path))
    tokens = comments(tokenize(source))
    try:
        while 1:
            for matchers, attribs in rule(location, tokens, converter):
                yield matchers, attribs
    except StopIteration: pass

def test():
    for matchers, attribs in parse('example.hss'):
        print matchers, attribs

if __name__ == '__main__':
    test()
