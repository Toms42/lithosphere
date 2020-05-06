# -*- coding: utf-8 -*-

"""
    :copyright: 2009 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from __future__ import with_statement

from gletools.gl import *
from .util import Context, DependencyException, Group, gen_buffers, enabled, get
from ctypes import *

def vertex_pointer(size, type, stride):
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(size, type, stride, 0)

def normal_pointer(size, type, stride):
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(type, stride, 0)

def index_pointer(size, type, stride):
    pass

modes = {
    'static'    : {
        'read'     : GL_STATIC_READ, 
        'draw'     : GL_STATIC_DRAW,
        'copy'     : GL_STATIC_COPY,
    },
    'dynamic'   : {
        'read'     : GL_DYNAMIC_READ,
        'draw'     : GL_DYNAMIC_DRAW,
        'copy'     : GL_DYNAMIC_COPY,
    },
    'stream'    : {
        'read'     : GL_STREAM_READ, 
        'draw'     : GL_STREAM_DRAW,
        'copy'     : GL_STREAM_COPY,
    },
}
    
typemap = {
    'f': (c_float, GL_FLOAT),
}

enablers = {
    'v': (vertex_pointer, 'vertices'),
    'n': (normal_pointer, 'normals')
}

class Buffer(object):
    def __init__(self, mode, data_target, draw_target, component_length, enable, type, ctype, data):
        self.data_target = data_target
        self.draw_target = draw_target
        self.component_length = component_length
        self.enable = enable
        self.type = type
        if component_length:
            self.stride = sizeof(ctype)*component_length
        else:
            self.stride = None

        if not isinstance(data, ctype*len(data)):
            data = (ctype*len(data))(*data)

        self.id = gen_buffers()
        glBindBuffer(self.data_target, self.id)
        glBufferData(self.data_target, sizeof(data), data, mode)
        glBindBuffer(self.data_target, 0)

    def draw_bind(self):
        glBindBuffer(self.draw_target, self.id)
        self.enable(self.component_length, self.type, self.stride)

    def copy_from(self, texture):
        glReadBuffer(texture.attachment)
        glBindBufferARB(GL_PIXEL_PACK_BUFFER_ARB, self.id)
        glReadPixels(0, 0, texture.width, texture.height, GL_RGBA, GL_FLOAT, 0) #GL_RGB might be a cludge
        glBindBufferARB(GL_PIXEL_PACK_BUFFER_ARB, 0)

class VertexObject(object):
    def __init__(self, indices, pbo=False, **buffers):
        self.size = len(indices)

        self._buffers = [Buffer(
            GL_STATIC_DRAW, GL_ELEMENT_ARRAY_BUFFER, GL_ELEMENT_ARRAY_BUFFER,
            None, index_pointer, GL_UNSIGNED_INT, c_uint, indices
        )]
        
        for format, data in buffers.items():
            format = format.split('_')
            if len(format) == 3:
                mode_storage, mode_use, format = format
            else:
                format = format[0]
                mode_storage = 'static'
                mode_use = 'draw'

            enabler, component_length, type = format
            mode = modes[mode_storage][mode_use]
            component_length = int(component_length)
            enabler, member_name = enablers[enabler]
            ctype, enum = typemap[type]
            if pbo:
                buffer = Buffer(mode, GL_PIXEL_PACK_BUFFER_ARB, GL_ARRAY_BUFFER, component_length, enabler, enum, ctype, data)
            else:
                buffer = Buffer(mode, GL_ARRAY_BUFFER, GL_ARRAY_BUFFER, component_length, enabler, enum, ctype, data)
            setattr(self, member_name, buffer)
            self._buffers.append(buffer)
    
    def __enter__(self):
        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT | GL_CLIENT_PIXEL_STORE_BIT)
        for buffer in self._buffers:
            buffer.draw_bind()

    def __exit__(self, exc_type, exc_val, exc_tb):
        glPopClientAttrib()

    def draw(self, primitive=GL_TRIANGLES, bind=True):
        if bind:
            with self:
                glDrawElements(primitive, self.size, GL_UNSIGNED_INT, 0)
        else:
            glDrawElements(primitive, self.size, GL_UNSIGNED_INT, 0)

    def draw_instanced(self, amount, primitive=GL_TRIANGLES):
        with self:
            DrawElementsInstanced(primitive, self.size, GL_UNSIGNED_INT, None, amount)
