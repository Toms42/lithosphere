# -*- coding: utf-8 -*-

"""
    :copyright: 2009 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from __future__ import with_statement

from gletools.gl import *
from .util import Context, DependencyException, quad
from ctypes import *

from PIL import Image
has_pil = True

__all__ = ['Texture']

class Object(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class Texture(Context):

    gl_byte = Object(
        obj = GLubyte,
        enum = GL_UNSIGNED_BYTE
    )
    gl_short = Object(
        obj = GLushort,
        enum = GL_UNSIGNED_SHORT
    )
    gl_float = Object(
        obj = GLfloat,
        enum = GL_FLOAT,
    )
    gl_half_float = Object(
        obj = GLfloat,
        enum = GL_FLOAT,
    )

    rgb = Object(
        enum = GL_RGB,
        count = 3,
    )
    rgba = Object(
        enum = GL_RGBA,
        count = 4,
    )
    luminance = Object(
        enum  = GL_LUMINANCE,
        count = 1,
    )
    alpha = Object(
        enum = GL_ALPHA,
        count = 1,
    )
    depth = Object(
        enum = GL_DEPTH_COMPONENT,
        count = 1,
    )

    specs = {
        GL_RGB:Object(
            pil = 'RGB',
            type = gl_byte,
            channels = rgb,
        ),
        GL_RGBA:Object(
            pil = 'RGBA',
            type = gl_byte,
            channels = rgba,
        ),
        GL_RGB16:Object(
            type = gl_short,
            channels = rgb,
        ),
        GL_RGBA32F:Object(
            pil = 'RGBA',
            type = gl_float,
            channels = rgba,
        ),
        GL_RGB16F:Object(
            type = gl_half_float,
            channels = rgb,
        ),
        GL_RGB32F:Object(
            pil = 'RGB',
            type = gl_float,
            channels = rgb,
        ),
        GL_LUMINANCE32F:Object(
            pil = 'L',
            type = gl_float,
            channels = luminance,
        ),
        GL_LUMINANCE:Object(
            type = gl_byte,
            channels = luminance,
        ),
        GL_ALPHA:Object(
            type = gl_byte,
            channels = alpha,
        ),
        GL_DEPTH_COMPONENT:Object(
            pil = 'L',
            type = gl_float,
            channels = depth,
        ),
    }

    target = GL_TEXTURE_2D
    
    _get = GL_TEXTURE_BINDING_2D

    def bind(self, id):
        glBindTexture(self.target, id)

    def _enter(self):
        glPushAttrib(GL_ENABLE_BIT | GL_TEXTURE_BIT)
        glActiveTexture(self.unit)
        glEnable(self.target)

    def _exit(self):
        glPopAttrib()

    def __init__(self, width, height, format=GL_RGBA, filter=GL_LINEAR, unit=GL_TEXTURE0, data=None, mipmap=0, clamp=False):
        Context.__init__(self)
        self.clamp = clamp
        self.mipmap = mipmap
        self.width = width
        self.height = height
        self.format = format
        self.filter = filter
        self.unit = unit
        spec = self.spec = self.specs[format]
        self.buffer_type = (spec.type.obj * (width * height * spec.channels.count))
        id = self.id = GLuint()

        glGenTextures(1, byref(id))
        if data:
            self.buffer = self.buffer_type(*data)
        else:
            self._buffer = None

        self.update()
        self.display = self.make_display()

   
    def get_buffer(self):
        if not self._buffer:
            self._buffer = self.buffer_type()
        return self._buffer
    def set_buffer(self, data):
        self._buffer = data
    buffer = property(get_buffer, set_buffer)

    def delete(self):
        glDeleteTextures(1, byref(self.id))

    @classmethod
    def open(cls, filename, format=GL_RGBA, filter=GL_LINEAR, unit=GL_TEXTURE0):
        if not has_pil:
            raise DependencyException('PIL is requried to open image files')
        spec = cls.specs[format]
        pil_format = getattr(spec, 'pil', None)
        if not pil_format:
            raise Exception('cannot load')
        image = Image.open(filename)
        image = image.convert(pil_format)
        width, height = image.size
        data = image.tostring()
        
        if spec.type == cls.gl_float:
            data = map(lambda x: ord(x)/255.0, data)
        else:
            data = map(ord, data)
        
        return cls(width, height, format=format, filter=filter, unit=unit, data=data)

    def save(self, filename):
        self.retrieve()
        if self.spec.type == self.gl_byte:
            source = string_at(self.buffer, sizeof(self.buffer))
            image = Image.frombytes(self.spec.pil, (self.width, self.height), source)
            image = image.resize((1025,1025), Image.ANTIALIAS)
            image.save(filename)
        elif self.spec.type == self.gl_float:
            #source = string_at(self.buffer, sizeof(self.buffer))
            source = [self.buffer[i] for i in xrange(self.width * self.height * 4)]
            m = min(source)
            source = [s-m for s in source]
            m = max(source)
            source = [int(s/m*255) for s in source]
            source = str(bytearray(source))
            image = Image.frombytes(self.spec.pil, (self.width, self.height), source)
            image = image.resize((1025,1025), Image.ANTIALIAS)
            image.save(filename)
            
        else:
            raise Exception('cannot save this type of image!')
        
    def make_display(self):
        uvs = 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0
        x1 = 0.0
        y1 = 0.0
        z = 0.0
        x2 = self.width
        y2 = self.height
        verts = (
             x1,    y1,    z,
             x2,    y1,    z,
             x2,    y2,    z,
             x1,    y2,    z,
        )

        return pyglet.graphics.vertex_list(4,
            ('v3f', verts),
            ('t2f', uvs),
        )
    
    def draw(self, x=0, y=0, scale=1.0):
        with self:
            quad(
                left=x, top=self.height+y, right=self.width+x, bottom=y, scale=scale
            )

    def set_data(self, data=None, clamp=False, level=0):
        with self:
            glTexParameteri(self.target, GL_TEXTURE_MIN_FILTER, self.filter)
            glTexParameteri(self.target, GL_TEXTURE_MAG_FILTER, self.filter)
            if clamp:
                if 's' in clamp:
                    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
                if 't' in clamp:
                    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
           
            if data:
                glTexImage2D(
                    self.target, level, self.format,
                    self.width, self.height,
                    0,
                    self.spec.channels.enum, self.spec.type.enum,
                    data,
                )
            else:
                glTexImage2D(
                    self.target, level, self.format,
                    self.width/2**level, self.height/2**level,
                    #self.width, self.height,
                    #width, height,
                    0,
                    self.spec.channels.enum, self.spec.type.enum,
                    0,
                )

            glFlush()

    def get_data(self, buffer):
        with self:
            glPushClientAttrib(GL_CLIENT_PIXEL_STORE_BIT)
            glGetTexImage(
                self.target, 0, self.spec.channels.enum, self.spec.type.enum,
                buffer,
            )
            glPopClientAttrib()
            glFinish()

    def update(self):
        if self._buffer:
            self.set_data(self.buffer, self.clamp)
        else:
            self.set_data(clamp=self.clamp)

    def retrieve(self):
        self.get_data(self.buffer)
        glFinish()

    def __getitem__(self, (x, y)):
        x, y = x%self.width, y%self.height

        channels = self.spec.channels.count
        pos = (x + y * self.width) * channels
        if channels == 1:
            return self.buffer[pos]
        else:
            end = pos + channels
            return self.buffer[pos:end]

    def __setitem__(self, (x, y), value):
        x, y = x%self.width, y%self.height

        channels = self.spec.channels.count
        pos = (x + y * self.width) * channels
        if channels == 1:
            self.buffer[pos] = value
        else:
            end = pos + channels
            self.buffer[pos:end] = value

    def __iter__(self):
        channels = self.spec.channels.count
        if channels == 1:
            for value in self.buffer:
                yield value
        else:
            for i in range(0, len(self.buffer), channels):
                yield self.buffer[i:i+channels]

class CubeMap(Context):
    '''
        Assumes a texturelayout of all 6 faces as a single row of:
        right = +x, back = -z, left = -x, front = +z, bottom = -y, top = +y
    '''

    _get = GL_TEXTURE_BINDING_CUBE_MAP 
    target = GL_TEXTURE_CUBE_MAP
    unit = GL_TEXTURE0

    def __init__(self, width, height, data):
        Context.__init__(self)
        id = self.id = GLuint()
        glGenTextures(1, byref(id))
        self.width = width
        self.height = height

        with self:
            glTexParameteri(self.target, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(self.target, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

            right = GL_TEXTURE_CUBE_MAP_POSITIVE_X
            left = GL_TEXTURE_CUBE_MAP_NEGATIVE_X
            top = GL_TEXTURE_CUBE_MAP_POSITIVE_Y
            bottom = GL_TEXTURE_CUBE_MAP_NEGATIVE_Y
            front = GL_TEXTURE_CUBE_MAP_POSITIVE_Z
            back = GL_TEXTURE_CUBE_MAP_NEGATIVE_Z
            face_size = (self.height**2) * 4

            self.set_data(right, data, 0)
            self.set_data(back, data, 1)
            self.set_data(left, data, 2)
            self.set_data(front, data, 3)
            self.set_data(bottom, data, 4)
            self.set_data(top, data, 5)
    
    def set_data(self, target, data, index):
        glTexImage2D(
            target, 0, GL_RGBA,
            self.height, self.height,
            0,
            GL_RGBA, GL_UNSIGNED_BYTE,
            self.face_data(data, index),
        )
    
    def face_data(self, data, index):
        result = ''
        face_pitch = self.height*4
        full_pitch = self.width*4

        for y in range(self.height):
            offset = y*full_pitch
            start = offset + index*face_pitch
            end = start + face_pitch
            result += data[start:end]

        return result
    
    def bind(self, id):
        glBindTexture(self.target, id)

    def _enter(self):
        glPushAttrib(GL_ENABLE_BIT | GL_TEXTURE_BIT)
        glActiveTexture(self.unit)
        glEnable(self.target)

    def _exit(self):
        glPopAttrib()

    @classmethod
    def open(cls, filename):
        if not has_pil:
            raise DependencyException('PIL is requried to open image files')

        image = Image.open(filename)
        image = image.convert('RGBA')
        width, height = image.size
        data = image.tostring()
        
        return cls(width, height, data)
