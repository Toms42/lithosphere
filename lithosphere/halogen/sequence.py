# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from .node import Node

class Sequence(Node):
    def __init__(self, id=None):
        Node.__init__(self, id)
        self.items = []

    def append(self, child, update=True):
        self.items.append(child)
        root = self.root
        child.parent = self
        if root and update:
            child.compute_style(root.sheet)
            self.update()

    def index(self, child):
        return self.items.index(child)

    def insert(self, index, child):
        self.items.insert(index, child)
        root = self.root
        child.parent = self
        if root:
            child.compute_style(root.sheet)
            self.update()

    def remove(self, child=None):
        if child:
            self.items.remove(child)
            child.parent = None
        else:
            self.parent.remove(self)

    def __iter__(self):
        return iter(self.items)

    @property
    def length(self):
        return len(self.items)
