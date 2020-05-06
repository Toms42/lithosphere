# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from .rowcol import Column, Row
from .label import Label
from .button import Button
from .container import Container

class Content(Container):
    pass

class Tabs(Column):
    def __init__(self, id=None):
        Column.__init__(self, id=id)
        self.tabs = Row().append_to(self)
        self.content = Content().append_to(self)
        self.contents = []

    def add(self, label, content):
        button = Button(label).append_to(self.tabs)
        self.contents.append(content)

        @button.event
        def on_click():
            for btn in self.tabs:
                btn.state.active = False
            button.state.active = True
            self.content.content = content
        
        if not self.content.content:
            self.content.content = content
            button.state.active = True
