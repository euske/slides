#!/usr/bin/env python
from svg import *
svg = SVG(220,120)
w = 200
h = 100
g = Group(stroke='black', fill='none', stroke_width=2)
g.add(Line(10,10+h, 10,10))
g.add(Line(10,10+h, 10+w,10+h))
def f(a, color):
    g.add(Polyline([ (15+x*20,105-y*10) for (x,y) in enumerate(a) ],
                     stroke=color ))
#f([0,2,8,9,3,2,1,0,1,0], 'green')
#f([1,1,8,7,2,1,0,1,0,0], 'red')
#f([0,2,8,9,3,2,1,0,1,0], 'green')
#f([1,0,0,2,1,3,7,8,2,4], 'red')
f([0,2,8,9,3,2,1,0,1,0], 'green')
f([0,1,4,5,1,1,0,0,0,0], 'red')
svg.add(g)
svg.dump()
