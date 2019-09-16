#!/usr/bin/env python
import sys
import csv
from math import log2

def calcetp(P):
    s = sum(P)
    P = [ p/s for p in P ]
    return -sum( p*log2(p) for p in P )

def split(feats, items):
    minf = None
    minetp = sys.maxsize
    minbins = None
    for f in feats:
        bins = {}
        for item in items:
            v = item[f]
            if v in bins:
                b = bins[v]
            else:
                b = bins[v] = {}
            k = item['Decision']
            if k not in b:
                b[k] = []
            b[k].append(item)
        e = 0
        for b in bins.values():
            sizes = [ len(z) for z in b.values() ]
            n = sum(sizes)
            e += calcetp(sizes)
            print(b, n, e)
        if e < minetp:
            minetp = e
            minf = f
            minbins = bins
        print(f, e)        
    print(minf, minetp, minbins)
    for (v,b) in minbins.items():
        items2 = []
        for z in b.values():
            items2.extend(z)
        split(feats, items2)
    return 0

def main(argv):
    items = []
    for path in argv[1:]:
        with open(path) as fp:
            for (i,row) in enumerate(csv.reader(fp)):
                if i == 0:
                    feats = row
                else:
                    values = dict(zip(feats, row))
                    items.append(values)
    feats.remove('Day')
    feats.remove('Decision')
    split(feats, items)

if __name__ == '__main__': sys.exit(main(sys.argv))
