# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from .node import Node

class Container(Node):
    def __init__(self, content=None, id=None):
        Node.__init__(self, id)
        self._content = None
        if content:
            self.content = content
    
    def compute_style(self, sheet):
        self.style = sheet.style(self)
        if self.content:
            self.content.compute_style(sheet)
    
    @property
    def width(self):
        top, bottom, left, right = self.padding
        width = self.style.width
        if width:
            return width
        elif self.content:
            return self.content.width+left+right
        else:
            return 0

    @property
    def height(self):
        top, bottom, left, right = self.padding
        height = self.style.height
        if height:
            return height
        elif self.content:
            return self.content.height+top+bottom
        else:
            return 0
    
    def set_content(self, content):
        if self.content:
            self.content.parent = None
       
        if content:
            self._content = content
            root = self.root
            content.parent = self
            if root:
                content.compute_style(root.sheet)
                content.update()
                self.update()
                content.layout()

        else:
            self._content = None
    
    def get_content(self):
        return self._content
    
    content = property(get_content, set_content)
    del get_content, set_content

    def remove(self, child=None):
        if child:
            if child == self.content:
                self.content = None
        else:
            self.parent.remove(self)
    
    def layout(self):
        if self.content:
            content = self.content
            style = content.style
            rect = self.rect
            top, bottom, left, right = self.padding
            
            if style.left is not None:
                content.rect.x = rect.left + style.left + left
            elif style.right is not None:
                content.rect.x = rect.right - content.rect.width - style.right - right
            elif style.align and style.align.center:
                content.rect.x = rect.left + (rect.width-left-right-content.rect.width)/2 + left
            else:
                content.rect.x = rect.left + left
            
            if style.bottom is not None:
                content.rect.y = rect.bottom + style.bottom + bottom
            elif style.top is not None:
                content.rect.y = rect.top - content.rect.height - style.top - top
            elif style.align and style.align.middle:
                content.rect.y = rect.bottom + (rect.height-bottom-top-content.rect.height)/2 + bottom
            else:
                content.rect.y = rect.bottom + bottom

            content.layout()

        self.rect.dirty = False

    def draw(self):
        self.draw_background()
        if self.content:
            self.content.draw()
   
    def __iter__(self):
        if self.content:
            return iter([self.content])
        else:
            return iter([])
