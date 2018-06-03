#!/usr/bin/env python

VARS = [1,2,3,4]
CLAUSES = [(1,2,-3),(2,3,-4),(3,4,1),(4,-1,2),(-1,-2,3),(-2,-3,4),(-3,-4,-1)]
#CLAUSES.append( (-4,1,-2) )

assign = []
decisions = {}
implications = {}

def decide():
    for v in VARS:
        if v not in assign and -v not in assign:
            level = len(decisions)
            decisions[level] = v
            assign.append(v)
            print('decide(%r)' % level, 'add:%r' % v, assign)
            return True
    return False

def bcp():
    level = len(decisions)-1
    implications[level] = []
    while True:
        for clause in CLAUSES:
            sat = False
            unassigned = []
            for lit in clause:
                if lit in assign:
                    sat = True
                    break
                elif lit not in assign and -lit not in assign:
                    unassigned.append(lit)
            if sat:
                pass
            elif len(unassigned) == 1:
                v = unassigned[0]
                implications[level].append(v)
                assign.append(v)
                print('bcp(%r)' % level, clause, 'add:%r' % v, assign)
                break
            elif not unassigned:
                print('conflict(%r)' % level, clause, assign)
                return False
        else:
            return True

def resolveConflict():
    clause = tuple( -v for v in decisions.values() )
    print('learned', clause)
    CLAUSES.append(clause)
    level = len(decisions)-1
    while 0 <= level:
        v = decisions[level]
        if 0 < v:
            lev = len(decisions)
            while level < lev:
                lev -= 1
                for v1 in implications[lev]:
                    assign.remove(v1)
                    print('rewind(%r)' % lev, 'remove:%r' % v1, assign)
                del implications[lev]
                v1 = decisions[lev]
                assign.remove(v1)
                del decisions[lev]
                print('undecide(%r)' % lev, 'remove:%r' % v1, assign)
            v = -v
            decisions[level] = v
            assign.append(v)
            print('reassign(%r)' % level, 'add:%r' % v, assign)
            return True
        level -= 1
    return False

def solve():
    while True:
        if not decide():
            return 'sat'
        while not bcp():
            if not resolveConflict():
                return 'unsat'

print(solve())
