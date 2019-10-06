#!/usr/bin/env python
import sys
from math import log

class NaiveBayes:

    def __init__(self):
        self.fcount = {}  # 素性 (f,k) の出現回数。
        return

    # 素性とクラスの相関をひとつ学習する。
    def learn(self, k, feats):
        if k in self.fcount:
            fc = self.fcount[k]
        else:
            fc = self.fcount[k] = {}
        # k の数を数える。
        if 'ALL' not in fc:
            fc['ALL'] = 0
        fc['ALL'] += 1
        # (f,k) の数を数える。
        for f in feats:
            if f not in fc:
                fc[f] = 0
            fc[f] += 1
        return

    def predict(self, feats):
        klass = []
        for (k,fc) in self.fcount.items():
            # P(k)・P(f_i | k) を計算する。
            pk = log(fc['ALL'])
            p = (pk + sum( (log(fc.get(f,1)) - pk) for f in feats ))
            klass.append((p, k))
        # クラスの一覧を確率の大きい順にソートする。
        klass.sort(reverse=True)
        return klass

def main(argv):
    import json
    with open('picnic.json') as fp:
        objs = json.loads(fp.read())
    nb = NaiveBayes()
    FEATS = [ 'Outlook','Temp','Humidity','Wind' ]
    for obj in objs:
        feats = [ f'{k}={obj[k]}' for k in FEATS ]
        nb.learn(obj['Decision'], feats)
    for obj in objs:
        feats = [ f'{k}={obj[k]}' for k in FEATS ]
        print(obj['Decision'], nb.predict(feats))
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
