# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self, point):
        return ((self.x-point.x)**2.0 + (self.y-point.y)**2.0)**0.5

class Rect(object):
    def __init__(self):
        self.x = 0
        self.y = 0
        self._width = 0
        self._height = 0
        self.dirty = True
    
    def copy(self):
        new = Rect()
        new.x = self.x 
        new.y = self.y 
        new._width = self._width
        new._height = self._height
        return new

    def translate(self, x, y):
        new = self.copy()
        new.x += x
        new.y += y
        return new

    @property
    def center(self):
        return Point(self.x + self.width/2, self.y + self.height/2)

    def get_width(self):
        return self._width
    def set_width(self, width):
        if self._width != width:
            self.dirty = True
            self._width = width
    width = property(get_width, set_width)

    def get_height(self):
        return self._height
    def set_height(self, height):
        if self._height != height:
            self.dirty = True
            self._height = height
    height = property(get_height, set_height)

    def __repr__(self):
        return 'Rect(%s %s %s %s)' % (self.x, self.y, self.width, self.height)

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.width

    @property
    def bottom(self):
        return self.y

    @property
    def top(self):
        return self.y + self.height

    def __eq__(self, other):
        if isinstance(other, Rect):
            return (
                self.x == other.x and
                self.y == other.y and
                self._width == other._width and
                self._height == other_height
            )
        else:
            return False
    
    def __ne__(self, other):
        if isinstance(other, Rect):
            return (
                self.x != other.x or
                self.y != other.y or
                self._width != other._width or
                self._height != other.height
            )
        else:
            return True

    def hit(self, x, y):
        return self.left <= x <= self.right and self.bottom <= y <= self.top
