# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

def hue(m1, m2, h):
    if h < 0:
        h += 1
    elif h > 1:
        h -= 1

    if h*6 < 1:
        return m1 + (m2 - m1) * h * 6
    elif h*2 < 1:
        return m2
    elif h*3 < 2:
        return m1 + (m2 - m1) * (2.0 / 3.0 - h) * 6
    else:
        return m1

def hsl2rgb(h, s, l):
    if l <= 0.5:
        m2 = l * (s + 1)
    else:
        m2 = l + s - l*s
    m1 = l*2 - m2
    
    return (
        hue(m1, m2, h + 1.0/3.0), 
        hue(m1, m2, h),
        hue(m1, m2, h - 1.0/3.0),
    ) 
