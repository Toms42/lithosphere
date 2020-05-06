# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from .rect import Rect
from .event import Event, State

class Node(object):
    parent = None
    xoff = 0
    yoff = 0

    def __init__(self, id=None):
        self.classes = []
        self.id = id
        self.rect = Rect()
        self.state = State(self)
        self.events = Event(self)
   
    ## helper functions ##
    @property
    def root(self):
        if self.parent:
            return self.parent.root

    @property
    def padding(self):
        padding = self.style.padding
        if padding:
            return padding.values
        else:
            return 0, 0, 0, 0
    
    def append_to(self, node, update=True):
        node.append(self, update)
        return self

    def insert_before(self, sibling):
        seq = sibling.parent
        index = seq.index(sibling)
        seq.insert(index, self)
        return self

    def remove(self):
        self.parent.remove(self) 
        return self

    def find(self, type):
        result = []
        if isinstance(self, type):
            result.append(self)
        for child in self:
            result += child.find(type)
        return result

    @property
    def absolute_rect(self):
        rect = self.rect.copy()
        rect.x, rect.y = self.absolute_coords(rect.x, rect.y)
        return rect

    def absolute_coords(self, x, y):
        return self.parent.absolute_coords(x+self.xoff, y+self.yoff)
    
    def translate_coords(self, x, y):
        return x-self.xoff, y-self.yoff

    def set_mouse_position(self, x, y):
        self.parent.set_mouse_position(x+self.xoff, y+self.yoff)

    ## event code ##
    def add_handler(self, handler):
        self.root.window.push_handlers(handler)

    def remove_handler(self, handler):
        self.root.window.remove_handlers(handler)

    ## class methods ##
    def add_class(self, name):
        self.classes.append(name)
        self.refresh()
        return self

    def remove_class(self, name):
        self.classes.remove(name)
        self.refresh()
        return self

    def toggle_class(self, name):
        if name in self.classes:
            self.classes.remove(name)
        else:
            self.classes.append(name)
        self.refresh()
        return self

    ## layouting/style ##
    def refresh(self):
        root = self.root
        if root:
            self.compute_style(root.sheet)
            self.update()

    def compute_style(self, sheet):
        self.style = sheet.style(self)
        for child in self:
            child.compute_style(sheet)

    def update(self, bubble=True):
        self.rect.width, self.rect.height = self.width, self.height
        
        if self.rect.dirty:
            for child in self:
                child.update(bubble=False)
            
            if bubble:
                if self.parent:
                    self.parent.update(bubble=True)
                else:
                    self.layout()
            else:
                self.layout()
        else:
            self.layout()
    
    @property
    def width(self):
        width = self.style.width
        if width is None:
            return 0
        else:
            return width

    @property
    def height(self):
        height = self.style.height
        if height is None:
            return 0
        else:
            return height
    
    ## drawing ##
    def draw_background(self):
        background = self.style.background
        if background:
            background.draw(self.rect)
    
    def draw(self):
        self.draw_background()
        for child in self:
            child.draw()
    
    ## node protocol ##
    def __iter__(self):
        return iter([])
    
    def layout(self): pass
