# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from .sequence import Sequence

class Row(Sequence):
    orientation = 'horizontal'

    @property
    def width(self):
        width = self.style.width
        top, bottom, left, right = self.padding
        if width:
            return width
        elif self.items:
            spacing = self.style.get('spacing', 0) * (len(self.items) - 1)
            return sum(child.width for child in self) + spacing+left+right
        else:
            return left+right

    @property
    def height(self):
        height = self.style.height
        top, bottom, left, right = self.padding
        if height:
            return height+top+bottom
        elif self.items:
            return max(child.height for child in self)+top+bottom
        else:
            return top+bottom
    
    def layout(self):
        top, bottom, left, right = self.padding
        x = self.rect.x + left
        y = self.rect.y + bottom
        spacing = self.style.get('spacing', 0)
        width = self.rect.width

        for child in self:
            style = child.style

            child.rect.x = x
            x += child.rect.width + spacing

            if style.top is not None:
                child.rect.y = self.rect.top - top - child.rect.height - style.top
            elif style.bottom is not None:
                child.rect.y = self.rect.bottom + bottom + style.bottom
            else:
                child.rect.y = self.rect.bottom + bottom

            child.layout()
        self.rect.dirty = False
    
class Column(Sequence):
    orientation = 'vertical'

    @property
    def width(self):
        width = self.style.width
        top, bottom, left, right = self.padding
        if width:
            return width
        elif self.items:
            return max(child.width for child in self)+left+right
        else:
            return left+right

    @property
    def height(self):
        height = self.style.height
        top, bottom, left, right = self.padding
        if height:
            return height
        elif self.items:
            spacing = self.style.get('spacing', 0) * (len(self.items) - 1)
            return sum(child.height for child in self) + spacing+top+bottom
        else:
            return top+bottom
    
    def layout(self):
        spacing = self.style.get('spacing', 0)
        top, bottom, left, right = self.padding
        x = self.rect.x + left
        y = self.rect.y + self.rect.height - top

        for child in self:
            style = child.style

            y -= child.rect.height
            child.rect.y = y
            y -= spacing
            
            if style.left is not None:
                child.rect.x = self.rect.left + style.left
            elif style.right is not None:
                child.rect.x = self.rect.right - child.rect.width - style.right
            else:
                child.rect.x = x
            
            child.layout()
        self.rect.dirty = False
