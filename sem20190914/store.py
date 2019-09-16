#!/usr/bin/env python
import math
import sys
import fileinput
import re
import json
import sqlite3

def splitwords(text):
    return [ w.lower() for w in re.findall(r'\w+', text) ]

def countwords(words):
    c = {}
    for w in words:
        if w not in c:
            c[w] = 0
        c[w] += 1
    return c

def doit(args, dbname='articles.db'):
    db = sqlite3.connect(dbname)
    cur = db.cursor()
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS Article (
        ArtId INTEGER PRIMARY KEY,
        Title TEXT,
        Words TEXT);
    ''')
    for line in fileinput.input(args, openhook=fileinput.hook_compressed):
        line = line.decode('utf-8')
        line = line.strip()
        if line.startswith('#'):
            (artid, _, title) = line[2:].partition(' ')
            artid = int(artid)
        elif line:
            # 単語に区切る。
            words = splitwords(line)
        else:
            # この時点で artid, title, words が設定されているはず。
            # 各単語の頻度情報を格納した辞書 wordcount を求める。
            wordcount = countwords(words)
            cur.execute('INSERT INTO Article VALUES (?,?,?);',
                        (artid, title, json.dumps(wordcount)))
            sys.stderr.write('.'); sys.stderr.flush()
    db.commit()
            
def main(argv):
    import getopt
    def usage():
        print('usage: %s [-d] [-o output] [file ...]' % argv[0])
        return 100
    try:
        (opts, args) = getopt.getopt(argv[1:], 'do:')
    except getopt.GetoptError:
        return usage()
    debug = 0
    dbname = 'articles.db'
    for (k, v) in opts:
        if k == '-d': debug += 1
        elif k == '-o': dbname = v
    return doit(args, dbname=dbname)

if __name__ == '__main__': sys.exit(main(sys.argv))
