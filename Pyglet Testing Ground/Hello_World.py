# -*- coding: utf-8 -*-
"""
Created on Sat Apr 06 22:19:25 2013

@author: mikewesthad
"""

import pyglet

window = pyglet.window.Window()

label = pyglet.text.Label("Hello, World", font_name="Times New Roman", 
                          font_size=36, x=window.width//2, 
                          y=window.height//2, anchor_x="center",
                          anchor_y="center")
                          
@window.event
def on_draw():
    window.clear()
    label.draw()
    
pyglet.app.run()