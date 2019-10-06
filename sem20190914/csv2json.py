#!/usr/bin/env python
import sys
import csv
import json
import fileinput

def main(argv):
    args = argv[1:]
    fp = fileinput.input(args)
    keys = None
    a = []
    for row in csv.reader(fp):
        if keys is None:
            keys = row
        else:
            obj = dict(zip(keys, row))
            a.append(obj)
    print(json.dumps(a))
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
