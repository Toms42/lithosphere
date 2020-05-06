# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from pyglet.gl import *
from pyglet.window.key import MOTION_LEFT, MOTION_RIGHT, MOTION_BACKSPACE, MOTION_DELETE

from .label import Label
from .container import Container

class Input(Container):
    def __init__(self, text='', id=None):
        Container.__init__(self, id=id)
        self.content = Label(text)
        self.caret = 0

    def get_text(self):
        return self.content.text

    def set_text(self, text):
        self.content.text = text
        self.caret = 0

    text = property(get_text, set_text)

    def on_text(self, text):
        self.content.text = self.content.text[:self.caret] + text + self.content.text[self.caret:]
        self.caret += len(text)

    def on_text_motion(self, motion):
        if motion == MOTION_RIGHT:
            self.caret += 1
        elif motion == MOTION_LEFT:
            self.caret -= 1
        elif motion == MOTION_BACKSPACE:
            self.content.text = self.content.text[:self.caret-1] + self.content.text[self.caret:]
            self.caret -= 1
        elif motion == MOTION_DELETE:
            self.content.text = self.content.text[:self.caret] + self.content.text[self.caret+1:]

        if self.caret < 0:
            self.caret = 0
        elif self.caret > len(self.content.text):
            self.caret = len(self.content.text)

    def on_mouse_press(self, x, y, button, modifiers):
        positions = self.content.caret_positions

        a = 0

        for b, position in enumerate(positions):
            if position > x:
                break
            else:
                a = b

        xa = positions[a]
        xb = positions[b]

        if abs(x-xa) < abs(x-xb):
            self.caret = a
        else:
            self.caret = b
    
    def on_focus(self):
        self.add_handler(self)
    
    def on_blur(self):
        self.remove_handler(self)

    def draw(self):
        self.draw_background()
        if self.content:
            self.content.draw()

        if self.state.focus:
            x = self.content.caret_positions[self.caret]
            glBegin(GL_QUADS)
            glTexCoord2f(self.root.resources.white.left, self.root.resources.white.bottom)
            glVertex2f(x-1, self.content.rect.bottom)
            glVertex2f(x, self.content.rect.bottom)
            glVertex2f(x, self.content.rect.top)
            glVertex2f(x-1, self.content.rect.top)
            glEnd()
