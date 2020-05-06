# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from .sequence import Sequence
from pyglet.gl import *

class Workspace(Sequence):
    def __init__(self, id=None):
        Sequence.__init__(self, id)
        self.xoff = 0
        self.yoff = 0

    def append(self, child, do_layout=True):
        self.items.append(child)
        root = self.root
        child.parent = self
        if root:
            child.compute_style(root.sheet)
            child.update(bubble=False)
            if do_layout:
                self.layout_content(child)
    
    def on_mouse_press(self, x, y, button, modifiers):
        self.mouse_off = x - self.rect.x, y - self.rect.y
        self.root.window.set_exclusive_mouse(True)
        self.add_handler(self)
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.xoff += dx
        self.yoff += dy
    
    def on_mouse_release(self, x, y, button, modifiers):
        x, y = self.mouse_off
        self.root.window.set_exclusive_mouse(False)
        self.parent.set_mouse_position(
            int(self.rect.x+x),
            int(self.rect.y+y),
        )
        self.remove_handler(self)

    def rise(self, widget):
        self.items.remove(widget)
        self.items.append(widget)
    
    def layout_content(self, content):
        style = content.style
        rect = self.rect.translate(-self.xoff, -self.yoff)
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
    
    def draw(self):
        glEnable(GL_SCISSOR_TEST)
        glScissor(self.rect.x, self.rect.y, self.rect.width, self.rect.height)
        glPushMatrix()
        glTranslatef(self.xoff, self.yoff, 0)
        self.draw_background()
        for child in self:
            child.draw()
        glPopMatrix()
        glDisable(GL_SCISSOR_TEST)
