#!/usr/bin/env python
import sys
import sqlite3
import json
import math

dbname = 'articles.db'
db = sqlite3.connect(dbname)
cur = db.cursor()

artids = [ artid for (artid,) in
           cur.execute('SELECT ArtId FROM Article;') ]
artids = artids[:100]

def getarticle(cur, artid):
    for (title,wordcount) in cur.execute(
        'SELECT Title,Words FROM Article WHERE ArtId = ?;', (artid,)):
        return (title, json.loads(wordcount))

def calcdot(a, b):
    v = {}
    for k in a.keys():
        v[k] = 0
    for k in b.keys():
        v[k] = 0
    prod = 0
    norma = normb = 0
    for k in v.keys():
        va = a.get(k,0)
        vb = b.get(k,0)
        prod += vb*va
        norma += va*va
        normb += vb*vb
    return (prod/math.sqrt(norma*normb))

class Group:

    def __init__(self):
        self.artids = []
        return

    def __repr__(self):
        return ('<Group: %r>' % self.artids)

    def add(self, artid):
        self.artids.append(artid)
        return

    def merge(self, group):
        self.artids.extend(group.artids)
        return

# 各グループの所属を保持する辞書:
groups = {}

def connect(p, q):
    print('connect', p, q)
    if p in groups and q in groups:
        # p, q 両方が別々のグループに含まれている場合: g[p] と g[q] を統合する。
        if groups[p] is groups[q]:
            pass
        else:
            g = groups[p]
            g.merge(groups[q])
            print('merge', g, groups[q])
            # 各要素の所属をつけかえる。
            for x in g.artids:
                groups[x] = g
    elif p in groups:
        # p のみがグループに含まれている場合: q を g[p] に追加する。
        g = groups[p]
        g.add(q)
        print('add', q, 'to', g)
    elif q in groups:
        # q のみがグループに含まれている場合: p を g[q] に追加する。
        g = groups[q]
        g.add(p)
        print('add', p, 'to', g)
    else:
        # p, q どちらもグループに含まれていない場合: 新規グループを作成する。
        g = Group()
        g.add(p)
        g.add(q)
        groups[p] = groups[q] = g
        print('form', g)

# しきい値
threshold = 0.9

for (i,artid1) in enumerate(artids):
    (title1,wordcount1) = getarticle(cur, artid1)
    for artid2 in artids[i+1:]:
        (title2,wordcount2) = getarticle(cur, artid2)
        sim = calcdot(wordcount1, wordcount2)
        #print(sim, title1, title2)
        if threshold < sim:
            # まとめる
            connect(artid1, artid2)

for g in set(groups.values()):
    print(g)
    for artid in g.artids:
        (title,_) = getarticle(cur, artid)
        print(title)
    print()
