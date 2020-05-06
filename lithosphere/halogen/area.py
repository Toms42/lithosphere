# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from .sequence import Sequence

class Area(Sequence):
    def append(self, child, update=True):
        self.items.append(child)
        root = self.root
        child.parent = self
        if root and update:
            child.compute_style(root.sheet)
            child.update()

    def layout_child(self, child):
        style = child.style
        rect = self.rect
        
        left, right = style.left, style.right
        if left is not None:
            child.rect.x = rect.left + left
        elif right is not None:
            child.rect.x = rect.right - child.rect.width - right
        elif style.align and style.align.center:
            child.rect.x = rect.left + (rect.width-child.rect.width)/2
        else:
            child.rect.x = rect.left
        
        top, bottom = style.top, style.bottom
        if bottom is not None:
            child.rect.y = rect.bottom + bottom
        elif top is not None:
            child.rect.y = rect.top - child.rect.height - top
        elif style.align and style.align.middle:
            child.rect.y = rect.bottom + (rect.height-child.rect.height)/2
        else:
            child.rect.y = rect.bottom

        child.layout()

    def layout(self):
        for child in self:
            self.layout_child(child)
        self.rect.dirty = False
