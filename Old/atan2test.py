# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 21:48:43 2013

@author: mikewesthad
"""


from math import atan2, pi
from numpy import arctan2, arange
from Vector2D import Vector2D

angles = arange(0.0, 360.0, 45.0)
headings = []
py_atan2_angles = []
np_atan2_angles = []


for angle in angles:
    heading = Vector2D.generateHeadingFromAngle(angle)
    headings.append(heading)
    py_angle = atan2(heading.y, heading.x) * 180.0/pi
    np_angle = arctan2(heading.y, heading.x) * 180.0/pi
    py_atan2_angles.append(py_angle)
    np_atan2_angles.append(np_angle)


for i in range(len(angles)):
    print angles[i], headings[i], py_atan2_angles[i], np_atan2_angles[i]