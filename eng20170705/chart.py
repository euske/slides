#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt

VALUES = [
    ('Apollo 11', 8500),
    ('Space Shuttle', 470000),
    ('Boeing 787', 6500000),
    ('Facebook', 60000000),
    ('Modern car', 100000000),
]
X = [ x for (x,(name,y)) in enumerate(VALUES) ]
Y = [ y for (name,y) in VALUES ]
NAME = [ name for (name,y) in VALUES ]

def fmt(n): return '{:,}'.format(n)

fig = plt.figure()
#plt.yscale('log')
plt.ylabel('Loc (lines of code)')
plt.xticks(X, NAME, rotation=20)

ax = fig.add_subplot(111)
ax.bar(X, Y, 0.5, color='red')

for (x,y) in zip(X, Y):
    s = fmt(y)
    ax.annotate(s, xy=(x,y), xytext=(x,y), ha='center', va='bottom')

plt.show()
