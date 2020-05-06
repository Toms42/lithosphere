# -*- coding: utf-8 -*-
"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL3, see LICENSE for more details.
"""
from math import sin, cos, pi

from pyglet.gl import *
import pyglet

def normalize(x, y, z):
    length = (x**2.0 + y**2.0 + z**2.0) ** 0.5
    return x/length, y/length, z/length

class Sphere(object):
    def __init__(self, size=1.0):
        v3f = list()
        n3f = list()
        count = 0

        def sphere_vert(i, j):
            i = i/10.0
            j = j/40.0
            s = sin(pi*i*0.5)
            z = cos(pi*i*0.5) * size
            x = sin(pi*j*2.0) * s * size
            y = cos(pi*j*2.0) * s * size
            v3f.extend((x,y,z))
            n3f.extend(normalize(x,y,z))
    
        for j in range(40):
            sphere_vert(0, j)
            sphere_vert(1, j)
            sphere_vert(1, j+1)
      
        for i in range(1, 10):
            for j in range(40):
                sphere_vert(i, j)
                sphere_vert(i+1, j)
                sphere_vert(i+1, j+1)
              
                sphere_vert(i, j)
                sphere_vert(i+1, j+1)
                sphere_vert(i, j+1)

        self.display = pyglet.graphics.vertex_list(len(v3f)/3,
            ('v3f/static', v3f),
            ('n3f/static', n3f),
            ('t3f/static', n3f),
        )

    def draw(self):
        self.display.draw(GL_TRIANGLES)
