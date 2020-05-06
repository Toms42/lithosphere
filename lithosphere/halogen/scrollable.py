# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from pyglet.gl import *
from .node import Node

class Scrollbar(Node):
    def __init__(self, id=None):
        Node.__init__(self, id)
        self._height = 0

    def on_mouse_press(self, x, y, button, modifiers):
        self.mouse_off = x - self.rect.x, y - self.rect.y
        self.root.window.set_exclusive_mouse(True)
        self.add_handler(self)
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.parent.change(dy)
    
    def on_mouse_release(self, x, y, button, modifiers):
        x, y = self.mouse_off
        self.root.window.set_exclusive_mouse(False)
        self.set_mouse_position(
            int(self.rect.x+x),
            int(self.rect.y+y),
        )
        self.remove_handler(self)
    
    def get_height(self):
        return self._height
    def set_height(self, value):
        self._height = value
    height = property(get_height, set_height)


class Scrollable(Node):
    def __init__(self, content, id=None):
        Node.__init__(self, id)
        scrollbar = self.scrollbar = Scrollbar()
        root = self.root
        self.content = content

        scrollbar.parent = self
        content.parent = self

        if root:
            scrollbar.compute_style(root.sheet)
            content.compute_style(root.sheet)
            scrollbar.refresh()
            content.refresh()

        self.has_layout = False
        self.scroll = 0
    
    def __iter__(self):
        return iter([self.scrollbar, self.content])

    def layout(self):
        content = self.content
        scrollbar = self.scrollbar
        self.scroll_size = content.height - self.height

        content.rect.x = self.rect.left
        content.rect.y = self.rect.bottom - content.height + self.height + self.scroll
        content.layout()

        if self.scroll_size > 0:
            scrollbar.height = int((float(self.height)/content.height) * self.height)
            scrollbar.rect.x = self.rect.right - scrollbar.width
            offset = int((self.height - scrollbar.height) * (float(self.scroll)/self.scroll_size))
            scrollbar.rect.y = self.rect.bottom - scrollbar.height + self.height - offset
            scrollbar.update(bubble=False)

    def change(self, amount):
        self.scroll -= amount
        if self.scroll < 0:
            self.scroll = 0
        elif self.scroll > self.scroll_size:
            self.scroll = self.scroll_size

        content = self.content
        scrollbar = self.scrollbar

        content.rect.y = self.rect.bottom - content.height + self.height + self.scroll
        content.layout()
        offset = int((self.height - scrollbar.height) * (float(self.scroll)/self.scroll_size))
        scrollbar.rect.y = self.rect.bottom - scrollbar.height + self.height - offset

    def draw(self):
        self.draw_background()
        if self.scroll_size > 0:
            self.scrollbar.draw()
        glPushAttrib(GL_SCISSOR_BIT | GL_ENABLE_BIT)
        glEnable(GL_SCISSOR_TEST)
        glScissor(self.rect.x, self.rect.y, self.rect.width-self.scrollbar.width, self.rect.height)
        self.content.draw()
        glPopAttrib()
