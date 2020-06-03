#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 11:25:08 2019

@author: tgelsema
"""

from informationdialogue.interpret.intrprt_base import getpaths, alle, makecartesianproduct, makeprojection, makeproduct
from informationdialogue.interpret.intrprt_iota import getiota
from informationdialogue.term.trm import Application

def getsplitfromkappa(objectlist, keywordlist, target, kappa, nosplits):
    paths = getpathsfromkappa(kappa)
    return getsplit(objectlist, keywordlist, target, paths, nosplits)

def getsplitfromobjectlist(objectlist, keywordlist, target, nosplits):
    potentialsplits = getpotentialsplits(objectlist, keywordlist, target, nosplits)
    if potentialsplits != []:
        return potentialsplits[0]
    else:
        return None
    
def getpathsfromkappa(kappa):
    if kappa == None:
        return []
    if kappa.op.name == 'inverse':
        c = kappa.args[0]
        iota = c.args[len(c.args) - 1]
    else:
        iota = kappa
    paths = []
    i = 0
    while i < len(iota.args):
        if i % 2 == 0:
            if iota.args[i].__class__.__name__ == 'Application':
                if iota.args[i].op.name == 'composition':
                    paths.append(iota.args[i].args)
            else:        
                paths.append([iota.args[i]])
        i += 1
    return paths
    

def splitkappa(objectlist, keywordlist, split):
    splitkappa = getiota(objectlist, keywordlist, split, split)
    return splitkappa


def splitpaths(paths, split, finals, target):
    """Split paths, which form the dimensions of a query, into two: pathsleft
    and pathsright. Pathsleft corresponds to the dimensions of a numerator
    term; pathsright to a denominator term. The criterion for the split is
    indicated by 'split': an object type that may or may not occur in each
    path as a codomain (note that 'split' is not equal to 'target'). The actual
    splitting is deferred to the routine splitpath() that splits an individual
    path. Return the combination (pathsleft, pathsright).
    """
    pathsleft = []
    pathsright = []
    if len(paths) == 1 and finals[0] == split:
        pathsleft = [[alle(target)]]
        pathsright = [[alle(split)]]
    else:
        i = 0
        while i < len(paths):
            (pathleft, pathright) = splitpath(paths[i], split, finals[i])
            pathsleft.append(pathleft)
            pathsright.append(pathright)
            i += 1
    return (pathsleft, pathsright)
    
def splitpath(path, split, final):
    """Split a path into (pathleft, pathright), which correspond to a dimension
    for a numerator and a denominator, respectively. Split is an object type
    which may or may not occur in path as a codomain. In the default case,
    pathleft equals path, and pathright copies the elements from path from the
    split onwards. If split does not occur in path, pathright remains empty.
    Only when 'split' equals the endpoint of path (i.e. 'split' equals
    'final'), pathleft remains empty and pathright is an 'all' term over
    'split'. Return the combination (pathleft, pathright).
    """
    pathleft = []
    pathright = []
    splitpassed = False
    if split == final:
        pathleft =  []
        pathright = [alle(split)]
    else:
        for d in path:
            if d.codomain == split:
                splitpassed = True
            if not splitpassed:
                pathright.append(d)
            pathleft.append(d)
        if not splitpassed:
            pathright = []
    return(pathleft, pathright)

def getpotentialsplits(objectlist, keywordlist, target, nosplits):
    potentialsplits = []
    i = 0
    while i < len(keywordlist):
        if keywordlist[i] == '<ot>':
            if objectlist[i] != target and not objectlist[i] in nosplits:
                potentialsplits.append(objectlist[i])
        i += 1
    return potentialsplits

def getsplit(objectlist, keywordlist, target, paths, nosplits):
    """Return the 'split' of a query as represented by objectlist and
    keywordlist: an object type that occurs in objectlist and does not equal
    the target. Split must be an object type that occurs somewehere as a
    codomain in paths. As a heuristic, return the split 'closest' to
    target, if multiple splits are found.
    """
    potentialsplits = getpotentialsplits(objectlist, keywordlist, target, nosplits)
    split = None
    for p in potentialsplits:
        for path in paths:
            for d in path:
                if not isinstance(d, Application) and d.codomain.equals(p):
                    if split == None or (getpaths(p, split) != [] and getpaths(target, p) != []):
                        split = p
    return split

def getfinals(paths):
    """Return the list of 'endpoints' for each path in paths. An endpoint of a
    path is the codomain of its first element, whether it is a variable or an
    object type relation.
    """
    finals = []
    for path in paths:
        if path != []:
            finals.append(path[0].codomain)
    return finals

def connectdimensions(pathsl, pathsr):
    """Return a correction term to align the dimensions indicated by pathsl
    with those indicated by pathsr. The correction term is either an 'all'
    term over the Cartesian product of the 'endpoints' of pathsl, or it is
    a projection term from this Cartesian product, selecting those endpoints
    that align with those in pathsr.
    """
    if not [] in pathsr:
        return None
    elif [] in pathsl or pathsr == [[]]:
        return alle(makecartesianproduct(getfinals(pathsl)))
    else:
        i = 0
        projs = []
        types = []
        while i < len(pathsr):
            if pathsl[i] != []:
                t = pathsl[i][0].codomain
                types.append(t)
                if pathsr[i] != []:
                    projs.append(i + 1)
            i += 1
        args = []
        for j in projs:
            args.append(makeprojection(types + [j]))
    return makeproduct(args)