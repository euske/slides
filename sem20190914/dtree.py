#!/usr/bin/env python

import sys
from math import log2


def calcent(objs):
    count = {}
    for obj in objs:
        k = obj['Decision']
        if k not in count:
            count[k] = 0
        count[k] += 1
    probs = [ n/len(objs) for n in count.values() ]
    return sum( -p*log2(p) for p in probs )

def getbest(objs):
    count = {}
    for obj in objs:
        k = obj['Decision']
        if k not in count:
            count[k] = 0
        count[k] += 1
    maxc = -1
    maxk = None
    for (k,c) in count.items():
        if maxc < c:
            maxc = c
            maxk = k
    return maxk


class Feature:

    def __init__(self, attr):
        self.attr = attr
        return

    # 与えられたオブジェクトから素性を取り出す。
    def ident(self, obj):
        return obj[self.attr]

    # 与えられたオブジェクト列をこの素性で分割する。
    def split(self, objs):
        raise NotImplementedError

class DiscreteFeature(Feature):

    # 与えられたオブジェクト列をこの素性で分割する。
    def split(self, objs):
        assert 2 <= len(objs)
        # 自分の素性に従って objs を分割する。
        d = {}
        for obj in objs:
            v = self.ident(obj)
            if v in d:
                a = d[v]
            else:
                a = d[v] = []
            a.append(obj)
        # この時点で
        # d = { 値1: [オブジェクト, オブジェクト, ...],
        #       値2: [オブジェクト, オブジェクト, ...],
        #       ... }
        # 各項目の平均エントロピーを計算する。
        n = len(objs)
        ent = sum( len(a) * calcent(a) for a in d.values() ) / n
        # 平均エントロピーと分割結果を返す。
        return (ent, d)


class Node:

    # 与えられたオブジェクトに対する判定結果を返す。
    def test(self, obj):
        raise NotImplementedError

class Leaf(Node):

    def __init__(self, answer):
        self.answer = answer
        return

    # 与えられたオブジェクトに対する判定結果を返す。
    def test(self, obj):
        # これは木の終端なので、すでに答えは決まっている。
        return self.answer

class Branch(Node):

    def __init__(self, feature, children):
        self.feature = feature
        self.children = children
        return

    # 与えられたオブジェクトに対する判定結果を返す。
    def test(self, obj):
        # 決められた素性を使って、子ノードのいずれかを選ぶ。
        v = self.feature.ident(obj)
        branch = self.children[v]
        # 子ノードにオブジェクトを渡して予測させる。
        return branch.test(obj)


# buildtree:
#   素性の集合 feats を使って、オブジェクト列 objs を分類する決定木を返す。
EPSILON = 0.90
def buildtree(feats, objs):
    # これ以上分岐しても意味がない場合は Leaf を返す。
    if calcent(objs) < EPSILON:
        return Leaf(getbest(objs))
    # objs をもっともよく分割するような素性を探す。
    minent = 9999
    minfeat = None
    minsplit = None
    for feat in feats:
        (ent, split) = feat.split(objs)
        if ent < minent:
            # もっともエントロピーが少ない時の feat と split を記録。
            minent = ent
            minfeat = feat
            minsplit = split
    assert minsplit is not None
    # split の各結果に対してさらに部分木を構築する。
    children = {}
    for (v,a) in minsplit.items():
        children[v] = buildtree(feats, a)
    return Branch(minfeat, children)


# main
def main(argv):
    import json
    with open('picnic.json') as fp:
        objs = json.loads(fp.read())
    feats = [
        DiscreteFeature('Outlook'),
        DiscreteFeature('Temp'),
        DiscreteFeature('Humidity'),
        DiscreteFeature('Wind')
    ]
    tree = buildtree(feats, objs)
    for obj in objs:
        print(obj['Decision'], tree.test(obj))
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
