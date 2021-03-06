# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from halogen import Column, Row, Button, Node, Tabs, Label

class Category(Row):
    def __init__(self, application):
        Row.__init__(self)
        self.application = application
        self.col1 = Column().append_to(self)
        self.col2 = Column().append_to(self)

    def add(self, type):
        if self.col1.length < 5:
            button = Button(type.__name__).append_to(self.col1)
        else:
            button = Button(type.__name__).append_to(self.col2)
        
        @button.event
        def on_click():
            type(self.application)

class Toolbar(object):
    def __init__(self, application):
        self.application = application
        self.tabs = Tabs(id='toolbar').append_to(application.viewport)

        row = Row(id="file")
        col1 = Column().append_to(row)
        col2 = Column().append_to(row)
        Button('Open').append_to(col1).on_click = application.file_open.show
        Button('Save').append_to(col1).on_click = application.file_save.show
        Button('New').append_to(col1).on_click = application.empty
        Label('Export').append_to(col2)
        Button('Heighs').append_to(col2).on_click = application.export_heights_dialog.show
        Button('Material').append_to(col2).on_click = application.export_png_dialog.show
        Button('Obj').append_to(col2).on_click = application.export_obj_dialog.show

        self.tabs.add('File', row)
        
        self.sources = Category(application)
        self.tabs.add('Src', self.sources)
        self.operators = Category(application)
        self.tabs.add('Ops', self.operators)
        self.filters = Category(application)
        self.tabs.add('Filter', self.filters)
