# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from .node import Node

class Canvas(Node):
    def draw(self):
        self.draw_background()
        if hasattr(self, 'on_draw'):
            self.on_draw()
