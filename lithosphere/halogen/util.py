# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

import inspect, os
from zipfile import ZipFile

class TextureRegion(object):
    def __init__(self, top, bottom, left, right):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right
        self.width = right - left
        self.height = top - bottom

    def __repr__(self):
        return 'TextureRegion(%s, %s, %s, %s)' % (self.top, self.bottom, self.left, self.right)

def here(path):
    frame = inspect.stack()[1][0]
    return os.path.join(
        os.path.dirname(
            os.path.abspath(frame.f_globals['__file__'])
        ),
        path,
    )

def coords(top, bottom, left, right):
    return [
        left, bottom,
        right, bottom,
        right, top,
        left, top,
    ]

zip_cache = {}

def res_listdir(path):
    index = path.find('.egg')
    if index >= 0:
        index += 4
        zippath = path[:index]
        if os.path.isdir(zippath):
            return os.listdir(path)
        else:
            zipfile = zip_cache.get(zippath)
            if not zipfile:
                zipfile = ZipFile(zippath)
                zip_cache[zippath] = zipfile

            member = path[index+1:]
            return [
                name[len(member)+1:]
                for name in
                zipfile.namelist()
                if name.startswith(member)
            ]
    else:
        return os.listdir(path)

def res_open(path, mode='rb'):
    path = os.path.normpath(path)
    index = path.find('.egg')
    if index >= 0:
        index += 4
        zippath = path[:index]
        if os.path.isdir(zippath):
            return open(path, mode)
        else:
            zipfile = zip_cache.get(zippath)
            if not zipfile:
                zipfile = ZipFile(zippath)
                zip_cache[zippath] = zipfile
            member = path[index+1:]
            return zipfile.open(member.replace('\\', '/'))
    else:
        return open(path, mode)
