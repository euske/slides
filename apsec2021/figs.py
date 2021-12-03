#!/usr/bin/env python
import sys
from xml.etree.ElementTree import tostring, Element, ElementTree


##  misc. functions
##
def tolist(x):
    if x is None:
        return []
    elif isinstance(x, str):
        return x.split(' ')
    else:
        return list(x)

def flatten(seq):
    a = []
    for x in seq:
        if isinstance(x, list) or isinstance(x, tuple):
            a += flatten(x)
        else:
            a.append(x)
    return a

def nsplit(n, seq):
    a = []
    v = []
    for x in seq:
        v.append(x)
        if n <= len(v):
            a.append(v)
            v = []
    return a

def getbounds(pts):
    (x0,y0,x1,y1) = (sys.maxsize, sys.maxsize, -sys.maxsize, -sys.maxsize)
    for (x,y) in pts:
        x0 = min(x0, x)
        y0 = min(y0, y)
        x1 = max(x1, x)
        y1 = max(y1, y)
    return (x0,y0,x1,y1)


##  SVGItem
##
class SVGItem:

    TAG = None

    def __init__(self, **attrs):
        self.fill = attrs.pop('fill', None)
        self.stroke = attrs.pop('stroke', None)
        self.stroke_width = attrs.pop('stroke_width', None)
        self.transforms = tolist(attrs.pop('transform', None))
        self.styles = tolist(attrs.pop('style', None))
        self.marker0 = attrs.pop('marker0', None)
        self.marker1 = attrs.pop('marker1', None)
        self.attrs = attrs
        return

    def __getitem__(self, k):
        return self.attrs.get(k)

    def __setitem__(self, k, v):
        self.attrs[k] = v
        return

    def translate(self, x, y):
        self.transforms.append('translate(%d,%d)' % (x,y))
        return self

    def get(self, k, v=None):
        return self.attrs.get(k, v)

    def set(self, k, v):
        self.attrs[k] = v
        return

    def copy(self, src=None):
        if src is None:
            src = SVGItem()
        src.fill = self.fill
        src.stroke = self.stroke
        src.stroke_width = self.stroke_width
        src.transforms = self.transforms.copy()
        src.marker0 = self.marker0
        src.marker1 = self.marker1
        src.attrs = self.attrs
        return src

    def bbox(self, parent=None):
        return None

    def defs(self):
        a = []
        if self.marker0 is not None:
            a.append(self.marker0)
        if self.marker1 is not None:
            a.append(self.marker1)
        return a

    def toxml(self):
        elem = Element(self.TAG)
        for (k,v) in self.attrs.items():
            k = k.replace('_','-')
            if v is None:
                elem.set(k, 'none')
            elif isinstance(v, list) or isinstance(v, tuple):
                elem.set(k, ' '.join(map(str, flatten(v))))
            else:
                elem.set(k, str(v))
        if self.fill is not None:
            elem.set('fill', self.fill)
        if self.stroke is not None:
            elem.set('stroke', self.stroke)
        if self.stroke_width is not None:
            elem.set('stroke-width', str(self.stroke_width))
        if self.transforms:
            elem.set('transform', ' '.join(self.transforms))
        if self.styles:
            elem.set('style', ' '.join(self.styles))
        if self.marker0 is not None:
            elem.set('marker-begin', 'url(#'+self.marker0.id+')')
        if self.marker1 is not None:
            elem.set('marker-end', 'url(#'+self.marker1.id+')')
        return elem

    def tostring(self):
        return tostring(self.toxml())


##  SVGGroup
##
class SVGGroup(SVGItem):

    TAG = 'g'

    def __init__(self, *children, **attrs):
        SVGItem.__init__(self, **attrs)
        if len(children) == 1 and isinstance(children[0], list):
            children = children[0]
        else:
            children = list(children)
        self.children = children
        return

    def __len__(self):
        return len(self.children)

    def __iter__(self):
        return iter(self.children)

    def copy(self, src=None):
        if src is None:
            children = [ c.copy() for c in self.children ]
            src = SVGGroup(*children)
        return SVGItem.copy(self, src)

    def add(self, obj):
        self.children.append(obj)
        return

    def remove(self, obj):
        self.children.remove(obj)
        return

    def bbox(self, parent=None):
        ok = False
        (x0,y0,x1,y1) = (sys.maxsize, sys.maxsize, -sys.maxsize, -sys.maxsize)
        for c in self.children:
            b = c.bbox(self)
            if b is not None:
                ok = True
                x0 = min(x0, b[0])
                y0 = min(y0, b[1])
                x1 = max(x1, b[2])
                y1 = max(y1, b[3])
        if ok:
            return (x0,y0,x1,y1)
        else:
            return None

    def defs(self):
        a = []
        for c in self.children:
            a.extend(c.defs())
        return a

    def toxml(self):
        elem = SVGItem.toxml(self)
        for c in self.children:
            elem.append(c.toxml())
        return elem

Group = SVGGroup


##  SVGCanvas
##
class SVGCanvas(SVGGroup):

    TAG = 'svg'

    def __init__(self, width=None, height=None, version='1.1', **attrs):
        self.width = attrs.pop('width', width)
        self.height = attrs.pop('height', height)
        self.version = attrs.pop('version', version)
        SVGGroup.__init__(self, **attrs)
        return

    def toxml(self):
        elem = SVGGroup.toxml(self)
        elem.set('xmlns', 'http://www.w3.org/2000/svg')
        elem.set('xmlns:xlink', 'http://www.w3.org/1999/xlink')
        b = self.bbox(self)
        elem.set('width', str(self.width or b[2]))
        elem.set('height', str(self.height or b[3]))
        elem.set('version', self.version)
        defs = self.defs()
        if defs:
            e = Element('defs')
            for d in set(defs):
                e.append(d.toxml())
            elem.insert(0, e)
        return elem

    def dump(self, fp=sys.stdout.buffer, decl=False):
        if decl:
            fp.write(b'<?xml version="1.0" encoding="UTF-8"?>')
        fp.write(self.tostring())
        fp.flush()
        return

SVG = SVGCanvas


##  Line
##
class Line(SVGItem):

    TAG = 'line'

    def __init__(self, *args, **attrs):
        self.x1 = attrs.pop('x1', None)
        self.y1 = attrs.pop('y1', None)
        self.x2 = attrs.pop('x2', None)
        self.y2 = attrs.pop('y2', None)
        if len(args) == 2:
            ((self.x1,self.y1), (self.x2,self.y2)) = args
        elif len(args) == 4:
            (self.x1,self.y1,self.x2,self.y2) = args
        if self.x1 is None: raise SyntaxError('x1 not defined')
        if self.y1 is None: raise SyntaxError('y1 not defined')
        if self.x2 is None: raise SyntaxError('x2 not defined')
        if self.y2 is None: raise SyntaxError('y2 not defined')
        self.p1 = (self.x1, self.y1)
        self.p2 = (self.x2, self.y2)
        SVGItem.__init__(self, **attrs)
        return

    def copy(self, src=None):
        src = Line(self.x1, self.y1, self.x2, self.y2)
        return SVGItem.copy(self, src)

    def move(self, dx, dy):
        self.x1 += dx
        self.y1 += dy
        self.x2 += dx
        self.y2 += dy
        self.p1 = (self.x1, self.y1)
        self.p2 = (self.x2, self.y2)
        return self

    def bbox(self, parent=None):
        if parent is None:
            sw = self.stroke_width or 0
        else:
            sw = parent.stroke_width or 0
        return (self.x1-sw, self.y1-sw,
                self.x2+sw, self.y2+sw)

    def toxml(self):
        elem = SVGItem.toxml(self)
        elem.set('x1', str(self.x1))
        elem.set('y1', str(self.y1))
        elem.set('x2', str(self.x2))
        elem.set('y2', str(self.y2))
        return elem


##  Rect
##
class Rect(SVGItem):

    TAG = 'rect'

    def __init__(self, *args, **attrs):
        self.x = attrs.pop('x', None)
        self.y = attrs.pop('y', None)
        self.width = attrs.pop('width', None)
        self.height = attrs.pop('height', None)
        if len(args) == 2:
            ((self.x,self.y), (self.width,self.height)) = args
        elif len(args) == 4:
            (self.x,self.y,self.width,self.height) = args
        if self.x is None: raise SyntaxError('x not defined')
        if self.y is None: raise SyntaxError('y not defined')
        if self.width is None: raise SyntaxError('width not defined')
        if self.height is None: raise SyntaxError('height not defined')
        self.topleft = (self.x, self.y)
        self.bottomright = (self.x+self.width, self.y+self.height)
        SVGItem.__init__(self, **attrs)
        return

    def copy(self, src=None):
        src = Rect(self.x, self.y, self.width, self.height)
        return SVGItem.copy(self, src)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        return self

    def bbox(self, parent=None):
        if parent is None:
            sw = self.stroke_width or 0
        else:
            sw = parent.stroke_width or 0
        return (self.x-sw, self.y-sw,
                self.x+self.width+sw, self.y+self.height+sw)

    def toxml(self):
        elem = SVGItem.toxml(self)
        elem.set('x', str(self.x))
        elem.set('y', str(self.y))
        elem.set('width', str(self.width))
        elem.set('height', str(self.height))
        return elem


##  Circle
##
class Circle(SVGItem):

    TAG = 'circle'

    def __init__(self, *args, **attrs):
        self.cx = attrs.pop('cx', None)
        self.cy = attrs.pop('cy', None)
        self.r = attrs.pop('r', None)
        if len(args) == 2:
            ((self.cx,self.cy), self.r) = args
        elif len(args) == 3:
            (self.cx,self.cy,self.r) = args
        if self.cx is None: raise SyntaxError('cx not defined')
        if self.cy is None: raise SyntaxError('cy not defined')
        if self.r is None: raise SyntaxError('r not defined')
        SVGItem.__init__(self, **attrs)
        return

    def copy(self, src=None):
        src = Circle(self.cx, self.cy, self.r)
        return SVGItem.copy(self, src)

    def move(self, dx, dy):
        self.cx += dx
        self.cy += dy
        return self

    def bbox(self, parent=None):
        if parent is None:
            sw = self.stroke_width or 0
        else:
            sw = parent.stroke_width or 0
        return (self.cx-self.r-sw, self.cy-self.r-sw,
                self.cx+self.r+sw, self.cy+self.r+sw)

    def toxml(self):
        elem = SVGItem.toxml(self)
        elem.set('cx', str(self.cx))
        elem.set('cy', str(self.cy))
        elem.set('r', str(self.r))
        return elem


##  Polygon
##
class Polygon(SVGItem):

    TAG = 'polygon'

    def __init__(self, *args, **attrs):
        points = flatten(attrs.pop('points', args))
        self.points = nsplit(2, points)
        if not self.points: raise SyntaxError('points not defined')
        SVGItem.__init__(self, **attrs)
        return

    def add(self, *args):
        if len(args) == 1:
            p = args[0]
        elif len(args) == 2:
            p = args
        else:
            raise SyntaxError('invalid args: %r' % args)
        self.points.append(p)
        return self

    def copy(self, src=None):
        src = self.__class__(*self.points)
        return SVGItem.copy(self, src)

    def move(self, dx, dy):
        self.points = [ (x+dx,y+dy) for (x,y) in self.points ]
        return self

    def bbox(self, parent=None):
        if parent is None:
            sw = self.stroke_width or 0
        else:
            sw = parent.stroke_width or 0
        (x0,y0,x1,y1) = getbounds(self.points)
        return (x0-sw, y0-sw, x1+sw, y1+sw)

    def toxml(self):
        elem = SVGItem.toxml(self)
        a = []
        for (x,y) in self.points:
            a.append('%r,%r' % (x,y))
        elem.set('points', ' '.join(a))
        return elem


##  Polyline
##
class Polyline(Polygon):

    TAG = 'polyline'


##  Path
##
class Path(SVGItem):

    TAG = 'path'

    def __init__(self, *args, **attrs):
        self.d = attrs.pop('d', args)
        if not self.d: raise SyntaxError('d not defined')
        SVGItem.__init__(self, **attrs)
        return

    def add(self, *args):
        self.d.extend(args)
        return self

    def copy(self, src=None):
        src = Path(*self.d)
        return SVGItem.copy(self, src)

    def toxml(self):
        elem = SVGItem.toxml(self)
        elem.set('d', ' '.join(map(str, flatten(self.d))))
        return elem


##  Text
##
class Text(SVGItem):

    TAG = 'text'

    def __init__(self, *args, **attrs):
        self.x = attrs.pop('x', None)
        self.y = attrs.pop('y', None)
        text = attrs.pop('text', None)
        if len(args) == 2:
            ((self.x,self.y), self.text) = args
        elif len(args) == 3:
            (self.x,self.y,self.text) = args
        else:
            raise SyntaxError(args)
        if self.x is None: raise SyntaxError('x not defined')
        if self.y is None: raise SyntaxError('y not defined')
        if self.text is None: raise SyntaxError('text not defined')
        SVGItem.__init__(self, **attrs)
        return

    def copy(self, src=None):
        src = Text(self.x, self.y, self.text)
        return SVGItem.copy(self, src)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        return self

    def bbox(self, parent=None):
        return (self.x, self.y, self.x, self.y)

    def toxml(self):
        elem = SVGItem.toxml(self)
        elem.set('x', str(self.x))
        elem.set('y', str(self.y))
        elem.text = self.text
        return elem


##  Marker
##
class Marker(SVGGroup):

    TAG = 'marker'

    def __init__(self, id=None, **attrs):
        self.id = attrs.pop('id', id)
        if self.id is None: raise SyntaxError('id not defined')
        self.orient = attrs.pop('orient', 'auto')
        self.viewBox = None
        SVGGroup.__init__(self, **attrs)
        return

    def add(self, obj):
        SVGGroup.add(self, obj)
        (x0,y0,x1,y1) = self.bbox()
        self.viewBox = (x0, y0, x1-x0, y1-y0)
        return

    def defs(self):
        return [self]

    def toxml(self):
        elem = SVGGroup.toxml(self)
        elem.set('id', self.id)
        elem.set('orient', self.orient)
        elem.set('viewBox', '%r %r %r %r' % self.viewBox)
        return elem


##  Symbol
##
class Symbol(SVGGroup):

    TAG = 'symbol'

    def __init__(self, id=None, **attrs):
        self.id = attrs.pop('id', id)
        if self.id is None: raise SyntaxError('id not defined')
        self.viewBox = None
        SVGGroup.__init__(self, **attrs)
        return

    def add(self, obj):
        SVGGroup.add(self, obj)
        (x0,y0,x1,y1) = self.bbox()
        self.viewBox = (x0, y0, x1-x0, y1-y0)
        return

    def defs(self):
        return [self]

    def toxml(self):
        elem = SVGGroup.toxml(self)
        elem.set('id', self.id)
        elem.set('viewBox', '%r %r %r %r' % self.viewBox)
        return elem


##  Use
##
class Use(SVGItem):

    def __init__(self, item=None, *args, **attrs):
        self.item = attrs.pop('item', item)
        if self.item is None: raise SyntaxError('item not defined')
        SVGItem.__init__(self, *args, **attrs)
        return

    def bbox(self, parent=None):
        return self.item.bbox(parent)

    def toxml(self):
        elem = SVGGroup.toxml(self)
        elem.set('id', self.item.id)
        return elem


##  Arrow
##
class Arrow(Line):

    ARROW = Marker(id='arrow')
    ARROW.add(Polygon([(-5,-5), (5,0), (-5,5)], fill='black', stroke=None))

    def __init__(self, *args, **attrs):
        Line.__init__(self, *args, **attrs)
        self.marker1 = self.ARROW
        return


##  BarChart
##
class BarChart(SVGGroup):

    def __init__(self, pts, width=None, height=None,
                 barcolor='green', captionsize=10, marginratio=0.5,
                 **attrs):
        SVGGroup.__init__(self, [], **attrs)
        width = attrs.pop('width', width)
        height = attrs.pop('height', height)
        barcolor = attrs.pop('barcolor', barcolor)
        captionsize = attrs.pop('captionsize', captionsize)
        texts = attrs.pop('texts', {})
        pts = list(pts)
        (x0,_,x1,y1) = getbounds(pts)
        b = height - captionsize
        w = width / ((x1-x0+1)*(1+marginratio)+marginratio)
        m = w*marginratio
        s = w*(1+marginratio)
        g = Group(stroke='black', fill=barcolor)
        for (x,y) in pts:
            h = y*b/y1
            g.add(Rect(int(m+(x-x0)*s), int(b-h), int(w), int(h)))
        self.add(g)
        if captionsize:
            t = Group(stroke='none', fill='black', text_anchor='middle',
                      style=('font-size: %dpx' % (captionsize*0.8)))
            for (x,y) in pts:
                c = texts.get(x, str(x))
                t.add(Text(int(m+(x-x0)*s+w/2), height, c, dy='-0.3em'))
            self.add(t)
        self.add(Group([Line(0, 0, 0, b), Line(0, b, width, b)],
                       stroke='black', fill='none', stroke_width=1))
        return


# run
def run():
    svg = SVG(400,200)
    w = h = 100
    g = Group(stroke='black', fill='none',
              stroke_width=2, transform='translate(10,10)')
    g.add(Arrow(0,10+h,0,0))
    g.add(Arrow(-10,h,10+w,0+h))
    g.add(Text(-10,h-10,'0', stroke='none',fill='black',
               text_anchor='middle',dy='0.5em'))
    a = [5,9,4,0,7,3,1,8,6,2]
    svg.add(BarChart(enumerate(a), 100, 100, transform='translate(10,10)'))
    dx = 10
    dy = 10
    g.add(Polyline([ (x*dx+dx/2,100-y*dy) for (x,y) in enumerate(a) ],
                     stroke='green'))
    svg.add(g)
    svg.add(Text(svg.width//2,10,'title', stroke='none',fill='black',
               text_anchor='middle', style='font-size:16px'))
    svg.dump()

def avg(a):
    a = list(a)
    return sum(a)/len(a)

def f1():
    t1=[
        ('ant',23,17,5,0),
        ('antlr4',13,22,9,1),
        ('bcel',3,11,31,0),
        ('compress',10,9,24,2),
        ('jedit',7,25,9,4),
        ('jhotdraw',15,17,12,1),
        ('junit',14,21,10,0),
        ('lucene',18,21,6,0),
        ('tomcat',11,27,6,1),
        ('weka',4,28,12,1),
        ('xerces',12,22,9,2),
        ('xz',4,15,26,0),
    ]
    t1.append(('Avg.',avg(x[1] for x in t1),avg(x[2] for x in t1),avg(x[3] for x in t1),avg(x[4] for x in t1)))
    svg = SVG(400,300)
    w = 280
    h = 200
    g = Group(stroke='black', fill='none', stroke_width=2)
    g.add(Line(10,10+h,10,10))
    g.add(Line(10,10+h,10+w,10+h))
    tg = Group(style='font-size: 75%;')
    for (i,(name,a,b,c,d)) in enumerate(t1):
        assert a+b+c+d==45
        x = 20+i*20
        if name =='Avg.': x += 10
        y = 0
        for (v,fill) in zip((a,b,c,d),('#0f0','#0cf','#f0f','#000')):
            v = h*v/45+.5
            g.add(Rect(x, 10+int(y), 10, int(v), fill=fill))
            y += v
        tg.add(Text(0, 0, name, transform=f'translate({x},215) rotate(90)'))
    g.add(Rect(300,10,10,10,fill='#0f0'))
    g.add(Rect(300,40,10,10,fill='#0cf'))
    g.add(Rect(300,70,10,10,fill='#f0f'))
    g.add(Rect(300,100,10,10,fill='#000'))
    tg.add(Text(315,20,'MustBeSame'))
    tg.add(Text(315,50,'CanBeSame'))
    tg.add(Text(315,80,'Different'))
    tg.add(Text(315,110,'Unknown'))
    svg.add(g)
    svg.add(tg)
    svg.dump()

def f2():
    t2 = [
        ('ant',39),
        ('antlr4',34),
        ('bcel',48),
        ('compress',53),
        ('jedit',24),
        ('jhotdraw',4),
        ('junit',34),
        ('lucene',40),
        ('tomcat',34),
        ('weka',29),
        ('xerces',31),
        ('xz',46),
    ]
    t2.append(('Avg.',avg(x[1] for x in t2)))
    svg = SVG(400,300)
    w = 280
    h = 200
    g = Group(stroke='black', fill='none', stroke_width=2)
    g.add(Line(10,10+h,10,10))
    g.add(Line(10,10+h,10+w,10+h))
    tg = Group(style='font-size: 75%;')
    for (i,(name,a)) in enumerate(t2):
        b = 90-a
        x = 20+i*20
        if name =='Avg.': x += 10
        y = 0
        for (v,fill) in zip((a,b),('#0f0','#f0f')):
            v = h*v/90+.5
            g.add(Rect(x, 10+int(y), 10, int(v), fill=fill))
            y += v
        tg.add(Text(0, 0, name, transform=f'translate({x},215) rotate(90)'))
    g.add(Rect(300,10,10,10,fill='#0f0'))
    g.add(Rect(300,40,10,10,fill='#f0f'))
    tg.add(Text(315,20,'Ours'))
    tg.add(Text(315,50,'Orig+Baseline'))
    svg.add(g)
    svg.add(tg)
    svg.dump()

def f3():
    t3 = [
        ('ant',7,8,30,0),
        ('antlr4',8,8,29,0),
        ('bcel',10,15,20,0),
        ('compress',5,5,34,1),
        ('jedit',6,6,33,0),
        ('jhotdraw',4,5,36,0),
        ('junit',2,7,36,0),
        ('lucene',3,14,27,1),
        ('tomcat',7,7,31,0),
        ('weka',1,10,34,0),
        ('xerces',6,10,28,1),
        ('xz',1,7,35,2),
    ]
    t3.append(('Avg.',avg(x[1] for x in t3),avg(x[2] for x in t3),avg(x[3] for x in t3),avg(x[4] for x in t3)))
    svg = SVG(400,300)
    w = 280
    h = 200
    g = Group(stroke='black', fill='none', stroke_width=2)
    g.add(Line(10,10+h,10,10))
    g.add(Line(10,10+h,10+w,10+h))
    tg = Group(style='font-size: 75%;')
    for (i,(name,a,b,c,d)) in enumerate(t3):
        #assert a+b+c+d==45
        x = 20+i*20
        if name =='Avg.': x += 10
        y = 0
        for (v,fill) in zip((a,b,c,d),('#0f0','#0cf','#f0f','#000')):
            v = h*v/45+.5
            g.add(Rect(x, 10+int(y), 10, int(v), fill=fill))
            y += v
        tg.add(Text(0, 0, name, transform=f'translate({x},215) rotate(90)'))
    g.add(Rect(300,10,10,10,fill='#0f0'))
    g.add(Rect(300,40,10,10,fill='#0cf'))
    g.add(Rect(300,70,10,10,fill='#f0f'))
    g.add(Rect(300,100,10,10,fill='#000'))
    tg.add(Text(315,20,'Good'))
    tg.add(Text(315,50,'Soso'))
    tg.add(Text(315,80,'Bad'))
    tg.add(Text(315,110,'Unknown'))
    svg.add(g)
    svg.add(tg)
    svg.dump()


def f4():
    CTYPE = ['PATH','URL','SQL','HOST','PORT','XCOORD','YCOORD','WIDTH','HEIGHT','YEAR','MONTH','DAY','OTHER']
    COLOR = ['#0f0','#f00','#f8f','#08f','#f80','#080','#f0f','#ff0','#0ff','#c00','#0c0','#00c','#444']
    PROJ = [
    ('   alluxio' ,  228 ,  72 ,  12 ,   0 ,  22 ,  26 ,   0 ,   0 ,   0 ,   0 ,  15 ,  15 ,  15 ,  51 ,  228),
    ('   arduino' ,   27 ,  39 ,   5 ,   0 ,  12 ,   9 ,   6 ,   6 ,  42 ,  42 ,   0 ,   0 ,   0 ,   1 ,  162),
    ('   binnavi' ,  309 ,  42 ,   7 ,   1 ,   2 ,   1 ,  23 ,  23 ,  67 ,  67 ,   1 ,   0 ,   0 ,   1 ,  235),
    ('     gephi' ,  120 ,   5 ,   0 ,   2 ,   0 ,   0 ,  28 ,  28 ,  66 ,  66 ,   0 ,   0 ,   0 ,   0 ,  195),
    ('    ghidra' , 1588 , 369 ,  25 ,   0 ,  10 ,   8 , 320 , 320 , 511 , 511 ,  13 ,  13 ,  13 ,  13 , 2126),
    ('      grpc' ,  195 ,  33 ,  16 ,   0 ,  68 ,  71 ,   0 ,   0 ,   0 ,   0 ,   0 ,   0 ,   0 ,  75 ,  263),
    ('      gson' ,   25 ,   0 ,   4 ,   0 ,   2 ,   0 ,   0 ,   0 ,   0 ,   0 ,   6 ,   6 ,   6 ,   7 ,   31),
    ('    hadoop' , 1789 , 978 , 634 ,   9 , 288 , 259 ,   0 ,   0 ,   0 ,   0 ,   2 ,   2 ,   2 , 124 , 2298),
    ('    ignite' , 1165 , 168 ,  85 , 666 , 106 , 111 ,   0 ,   0 ,   0 ,   0 ,  12 ,  12 ,  12 , 101 , 1273),
    ('     jedit' ,  125 , 130 ,  19 ,   0 ,   3 ,   3 ,  50 ,  50 , 112 , 112 ,   0 ,   0 ,   0 ,   3 ,  482),
    ('   jenkins' ,  117 ,  82 ,  28 ,   0 ,   6 ,   6 ,   1 ,   1 ,   1 ,   1 , 102 , 102 , 102 , 237 ,  669),
    ('     jetty' ,  441 ,  72 , 216 ,   9 , 163 , 104 ,   0 ,   0 ,   0 ,   0 ,   0 ,   0 ,   0 ,  37 ,  601),
    ('  jhotdraw' ,   32 ,   6 ,   5 ,   0 ,   1 ,   1 ,  96 ,  96 ,  50 ,  50 ,   0 ,   0 ,   0 ,   1 ,  306),
    ('     jitsi' ,  327 ,  22 ,  18 ,   1 ,   8 ,  31 ,  78 ,  78 , 234 , 234 ,   0 ,   0 ,   0 ,  30 ,  734),
    ('    jmeter' ,  145 , 112 ,  62 ,   2 ,  31 ,  28 ,   7 ,   7 ,  62 ,  62 ,   0 ,   0 ,   0 ,  28 ,  401),
    ('   jpacman' ,    3 ,   0 ,   0 ,   0 ,   0 ,   0 ,   0 ,   0 ,   1 ,   1 ,   0 ,   0 ,   0 ,   0 ,    2),
    ('     kafka' ,  384 ,  37 ,   1 ,   0 ,  85 ,  72 ,   0 ,   0 ,   0 ,   0 ,  14 ,  14 ,  14 ,  44 ,  281),
    ('    libgdx' ,  272 ,  83 ,   7 ,   0 ,   4 ,   5 ,   7 ,   7 ,  36 ,  36 ,   0 ,   0 ,   0 ,   0 ,  185),
    ('     netty' ,  303 ,  38 ,  24 ,   0 ,  54 , 130 ,   0 ,   0 ,   0 ,   0 ,   1 ,   1 ,   1 , 117 ,  366),
    ('    okhttp' ,   36 ,   2 ,  24 ,   0 ,   6 ,   7 ,   0 ,   0 ,   0 ,   0 ,   0 ,   0 ,   0 ,   3 ,   42),
    ('   picasso' ,    9 ,   1 ,   0 ,   0 ,   0 ,   0 ,   0 ,   0 ,   0 ,   0 ,   0 ,   0 ,   0 ,   0 ,    1),
    ('  plantuml' ,  210 ,  29 ,   4 ,   0 ,   5 ,  11 ,   4 ,   4 ,  11 ,  11 ,   2 ,   2 ,   2 ,   2 ,   87),
    ('  selenium' ,   91 ,  44 ,  66 ,   0 ,  15 ,  12 ,   1 ,   1 ,   0 ,   0 ,   1 ,   1 ,   1 ,  21 ,  163),
    ('    tomcat' ,  349 , 207 ,  64 ,  22 ,  38 ,  52 ,   0 ,   0 ,  10 ,  10 ,   0 ,   0 ,   0 ,  47 ,  450),
    (' websocket' ,   15 ,   9 ,  44 ,   0 ,   5 ,  43 ,   0 ,   0 ,   1 ,   1 ,   0 ,   0 ,   0 ,   1 ,  104),
    (' zookeeper' ,  114 ,  88 ,   4 ,   0 , 126 , 192 ,   0 ,   0 ,   1 ,   1 ,   0 ,   0 ,   0 ,  47 ,  459),
    ]
    svg = SVG(680,400)
    w = 530
    h = 300
    g = Group(stroke='black', fill='none', stroke_width=2)
    g.add(Line(30,20+h,30,20))
    g.add(Line(30,20+h,30+w,20+h))
    g.add(Line(30+w,20,30+w,20+h))
    tg = Group(style='font-size: 75%;')
    cg = Group(style='font-size: 70%;')
    for (i,row) in enumerate(PROJ):
        x = 40+i*20
        name = row[0].strip()
        kloc = row[1]
        total = 0
        for (color,v) in zip(COLOR,row[2:]):
            total += v
            assert total < 2500, row
            y = 1-total/2500
            v = v/2500
            g.add(Rect(x, 20+int(h*y+.5), 10, int(h*v+.5), fill=color))
        y = 0.95-kloc/2000
        g.add(Circle(x+5, int(h*y+.5), 4, fill='white'))
        tg.add(Text(0, 0, name, transform=f'translate({x},{h+25}) rotate(90)'))
    g.add(Circle(610, 15, 4, fill='white'))
    tg.add(Text(620, 20, 'kloc'))
    cg.add(Text(550, 16, '#ctype'))
    for (i,(color,ctype)) in enumerate(zip(COLOR,CTYPE)):
        y = 55+i*20
        g.add(Rect(605,y,10,10,fill=color))
        tg.add(Text(620,y+10,ctype))
    for kloc in range(200,2000,200):
        y = 0.95-kloc/2000
        s = str(kloc)
        cg.add(Text(28, int(h*y+.5), s, text_anchor='end'))
    for n in range(0,2500,200):
        y = 1-n/2500
        cg.add(Text(562, 25+int(h*y+.5), str(n)))
    cg.add(Text(32, int(h*(0.95-1800/2000)+.5), 'kloc'))
    svg.add(g)
    svg.add(tg)
    svg.add(cg)
    svg.dump()

def f5():
    CTYPE = [
    ('PATH'  , 49.6, 22.8, 7.0, 6.3, 4.8, 2.2, 7.3),
    ('URL'   , 31.6, 18.5, 13.7, 13.5, 10.2, 5.8, 6.8),
    ('SQL'   , 47.5, 12.1, 8.7, 3.1, 4.4, 5.5, 18.8),
    ('HOST'  , 59.2, 11.5, 3.0, 22.1, 2.0, 0.1, 2.1),
    ('PORT'  , 68.4, 27.5, 2.1, 1.2, 0.3, 0.4, 0.0),
    ('XCOORD', 54.1, 24.6, 9.8, 6.4, 1.6, 2.1, 1.3),
    ('YCOORD', 52.5, 22.4, 10.1, 9.0, 2.6, 1.9, 1.4),
    ('WIDTH' , 71.0, 15.2, 6.3, 2.5, 1.5, 1.8, 1.7),
    ('HEIGHT', 71.4, 15.4, 6.4, 3.1, 1.5, 1.3, 1.0),
    ('YEAR'  , 96.4, 2.4, 1.2, 0.0, 0.0, 0.0, 0.0),
    ('MONTH' , 79.8, 19.6, 0.6, 0.0, 0.0, 0.0, 0.0),
    ('DAY'   , 99.4, 0.0, 0.6, 0.0, 0.0, 0.0, 0.0),
    ]
    COLOR = ['#0f0','#f00','#f8f','#08f','#f80','#080','#f0f','#ff0','#0ff','#c00','#0c0','#00c','#444']
    RANGE = ['n=1','n=2','n=3','n=4','n=5','n=6','n≧7']
    svg = SVG(400,250)
    w = 280
    h = 200
    g = Group(stroke='black', fill='none', stroke_width=2)
    g.add(Line(30,20+h,30,10))
    g.add(Line(30,20+h,30+w,20+h))
    tg = Group(style='font-size: 75%;')
    fg = Group(fill='none', stroke_width=3)
    bg = Group(fill='white', stroke='black')
    cg = Group(style='font-size: 70%;', text_anchor='end')
    a = list(zip(COLOR,CTYPE))
    a.reverse()
    for (i,(color,row)) in enumerate(a):
        p = []
        for (j,v) in enumerate(row[1:]):
            x = 50+j*40
            y = 20+int(h*(1-v/100))
            p.append((x,y))
            bg.add(Rect(x-3,y-3,6,6,fill=color))
        fg.add(Polyline(p, stroke=color))
    for (i,(color,ctype)) in enumerate(zip(COLOR,CTYPE)):
        y = 20+i*17
        bg.add(Rect(320,y,6,6,fill=color))
        tg.add(Text(332,y+7,ctype[0]))
    for (i,s) in enumerate(RANGE):
        x = 50+i*40
        tg.add(Text(x,h+40,s, text_anchor='middle'))
    for v in range(0,101,20):
        y = 1-v/100
        cg.add(Text(28, 22+int(h*y+.5), f'{v}%'))
    svg.add(g)
    svg.add(fg)
    svg.add(bg)
    svg.add(cg)
    svg.add(tg)
    svg.dump()
