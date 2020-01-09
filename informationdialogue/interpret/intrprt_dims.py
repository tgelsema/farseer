#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 14 16:25:17 2019

@author: tgelsema
"""
from informationdialogue.interpret.intrprt_base import getindexfrompattern, insertsorted, getpaths, getoptimalpath, makecomposition, makeproduct, alle
from informationdialogue.interpret.intrprt_pivot import getpivot, gettarget
from informationdialogue.nlp.tknz import tokenize
from informationdialogue.domainmodel.dm import lookup, defaults
from informationdialogue.term.trm import Application
from informationdialogue.kind.knd import Variable


def getdimensions(paths, target):
    """Build a term that corresponds to the paths representing the dimensions
    of a query. Use getdimensionpaths() to get these paths. Build a (product)
    term of compositions from paths. Return the resulting term.
    """
    # paths = getdimensionpaths(objectlist, keywordlist, pivot, target)
    if paths == [] or paths == [[]]:
        return alle(target)
    dims = []
    for path in paths:
        if path != []:
            arg = makecomposition(path)
            dims.append(arg) #  = insertsorted(dims, arg)
    dimsterm = makeproduct(dims)
    return dimsterm

def getdimensionpaths(objectlist, keywordlist, pivot, target, ignoresplit, hints):
    """Return two lists of paths: one from target to a destination object type,
    that correspond to the dimensions of a query represented by objectlist and
    keywordlist and one originating from pivot. First extract indices to suitable
    object types, object type relations and categorical variables from
    keywordlist. Then find optimal paths from target (pivot) to these object
    types, object type relations and
    categorical variables. Ignore a path that is a part of another path
    (insertwithoutpostfixes). Return the resulting list of paths. Note that
    a path may 'end with' an object type relation (i.e., path[0] is an object
    type relation) or path may 'end with' a categorical variables. Suitable
    variables must therefore be appended to each path (if applicable) to turn
    them into dimensions. See getdimensions().
    """
    pathsfrompivotdict = {}
    dimsdict = extractdimensions(objectlist, keywordlist, pivot, target)
    someclues = getsomeclues(objectlist, keywordlist, target, dimsdict)
    pathsfromtarget = []
    pathsfrompivot = []
    for k in dimsdict.keys():
        clues = someclues
        obj = objectlist[k]
        if k != dimsdict[k]:
            clues.append(objectlist[dimsdict[k]])
        if keywordlist[k] == '<ot>':
            dest = obj
        else:
            dest = obj.codomain
            clues.append(obj)
        if dest != ignoresplit:
            path = getoptimalpath(getpaths(target, dest), clues, [])
            pathsfromtarget = insertwithoutpostfixes(path, pathsfromtarget)
            hint = []
            if k in hints.keys():
                if hints[k] != []:
                    if isinstance(hints[k][0], Variable):
                        hint = hints[k][1:]
                    else:
                        hint = hints[k]
            path = getoptimalpath(getpaths(pivot, dest), clues, hint)
            pathsfrompivot = insertwithoutpostfixes(path, pathsfrompivot)
            pathsfrompivotdict[k] = path
    # returnpaths = []
    # for path in pathsfromtarget:
        # path = appendvariables(path)
    #     returnpaths.append(path)
    return (pathsfromtarget, pathsfrompivot, pathsfrompivotdict)

def getsomeclues(objectlist, keywordlist, target, dimsdict):
    """Return some object types as clues to find optimal paths. Object types
    must not be the 'endpoints' of the objects pointed to by dimsdict. Find
    remaning object types in objectlist and return them. Target is always a
    clue.
    """
    clues = [target]
    endpoints = []
    for k in dimsdict.keys():
        obj = objectlist[k]
        if keywordlist[k] == '<ot>':
            if obj not in endpoints: 
                endpoints.append(obj)
        else:
            if obj.codomain not in endpoints:
                endpoints.append(obj.codomain)
    k = 0
    while k < len(keywordlist):
        if keywordlist[k] == '<ot>' and objectlist[k] not in clues:
            clues.append(objectlist[k])
        k += 1
    return clues

def insertwithoutpostfixes(path, paths):
    """Insert path into a list of paths if path is not part of another path p
    already present in the list. Also, if there is a path p in paths that is a
    part of path, then remove p and insert path into paths. Return the
    resulting paths list. From the way paths are formed, the essential check is
    whether p is a postfix of path, or whether path is a postfix of p.
    """
    donotinsert = False
    for p in paths:
        if ispostfix(path, p):
            donotinsert = True
            break
        if ispostfix(p, path):
            paths.remove(p)
    if not donotinsert:
        paths = insertsorted(paths, path)
    return paths
        
def ispostfix(lst1, lst2):
    """Return True if lst1 is a part of lst2 (or both are equal), when counting
    from the right (postfix). Otherwise, return False.
    """
    i = 0
    while i < len(lst1) and i < len(lst2):
        if lst1[len(lst1) - 1 - i] != lst2[len(lst2) - 1 - i]:
            return False
        i += 1
    if i == len(lst2) and i < len(lst1):
        return False
    return True

def appendvariablestopaths(paths):
    """Append variables to each path in paths, if a path does not end with a
    variable already (i.e., path[0] is not a variable). The variables appended
    are the defaults that are listed in the domainmodel for each object type.
    The routine 'appendvariables()' appends these defauts to an individual path.
    Return the list of paths thus obtained.
    """
    returnpaths = []
    for path in paths:
        if path != []:
            path = appendvariables(path)
        returnpaths.append(path)
    return returnpaths

def appendvariables(path):
    """If path ends with a variable (i.e., if path[0] is a variable), return
    path without change. Otherwise, append a product of suitable default
    variables (taken from the defaults dictionary of domainmodel), i.e., insert
    it at position 0 in the path. Return the resulting path.
    """
    if path == []:
        return path
    elif path[0].__class__.__name__ == 'Variable' or isinstance(path[0], Application):
        return path
    else:
        if path[0].codomain in defaults:
            path.insert(0, makeproduct(defaults[path[0].codomain]))
        return path

def extractdimensions(objectlist, keywordlist, pivot, target):
    """Collect indices to potential dimensions from keywordlist, according to
    some given patterns. For the patterns <ot><prep><otr> and
    <catvar><prep><otr> (these correspond to e.g. 'gemeente van vestiging'
    and 'geslacht van werknemer'), also collect indices to the corresponding
    object type relations ('vestiging' and 'werknemer', respectively). These
    will serve as clues when paths from the target to the endpoints of the
    potential dimensions are investigated. From the dictionary of indices so
    collected, possibly remove indices, e.g. when there is a path from an
    endpoint to the target, or when an endpoint corresponds to the pivot.
    Finally, remove potential dimensions when they correspond to (the
    codomain of) a constant: in this case, the potential dimension has already
    been used as a selection criterion. Return the dictionary of indices and
    clues so obtained.
    """
    dimindices = {}
    i = 0
    while i < len(keywordlist):
        k = [-1, -1, -1]
        k[0] = getindexfrompattern(['<per>'], 0, i, keywordlist, True)
        k[1] = getindexfrompattern(['<prep>','<all>'], 0, i, keywordlist, True)
        k[2] = getindexfrompattern(['<prep>', '<ot>'], 0, i, keywordlist, True)
        j = len(keywordlist)
        for l in k:
            if l != -1 and l < j:
                j = l
        if j < len(keywordlist):
            j += 1
            while j < len(keywordlist) and (
                keywordlist[j] == '<ot>' or
                keywordlist[j] == '<otr>' or
                keywordlist[j] == '<catvar>' or
                keywordlist[j] == '<all>' or
                keywordlist[j] == '<prep>' or ####
                keywordlist[j] == '<unk>'):
                if getindexfrompattern(['<ot>', '<prep>', '<otr>'], 0, j, keywordlist, True) == j:
                    dimindices[j] = j + 2
                    j += 2
                elif getindexfrompattern(['<catvar>', '<prep>', '<otr>'], 0, j, keywordlist, True) == j:
                    dimindices[j] = j + 2
                    j += 2
                elif keywordlist[j] == '<ot>' or keywordlist[j] == '<catvar>' or keywordlist[j] == '<otr>':
                    dimindices[j] = j
                j += 1
        i = j
    # possibly remove some object types. Also correct for selection criteria
    remove = []
    for i in dimindices.keys():
        if keywordlist[i] == '<catvar>':
            obj = objectlist[i].codomain
        elif keywordlist[i] == '<otr>':
            if dimindices[i] != i:
                obj = objectlist[dimindices[i]]
            else:
                obj = objectlist[i].codomain
        else:
            obj = objectlist[i]
        if obj.equals(pivot) or obj.equals(target) or getpaths(obj, target) != []:
            if not i in remove:
                remove.append(i)
        k = 0
        #### while k < len(keywordlist):
        ####     if keywordlist[k] == '<const>':
        ####         if getpaths(obj, objectlist[k].codomain):
        ####             if not i in remove:
        ####                 remove.append(i)
        ####     k += 1
    for r in remove:
        if r in dimindices.keys():
            dimindices.pop(r)
    return dimindices

def test():
    # line = 'het gemiddeld aantal banen als kolonel in een bedrijf naar gemeente van vestiging en geslacht van werknemer'
    # line = 'totale salaris naar adres van werknemer en gemeente van vestiging'
    # line = 'totale salaris naar adres van werknemer en gemeente van wernemer'
    # line = 'wat is het gemiddeld aantal banen dat een persoon heeft per gemeente?'
    # line = 'het gemiddelde aantal banen dat een persoon heeft voor iedere gemeente'
    # line = 'het gemiddeld aantal banen per gemeente'
    line = 'Per adres in Leiden het laagste aantal personen'
    # line = 'het gemiddeld aantal banen bij een bedrijf per gemeente'
    (tokenlist, objectlist, keywordlist) = tokenize(line, lookup)
    pivot = getpivot(objectlist, keywordlist)
    target = gettarget(objectlist, keywordlist, tokenlist, pivot)
    print(target)
    print(getdimensionpaths(objectlist, keywordlist, pivot, target))
    """
    print(ispostfix([], [])) # True
    print(ispostfix([], ['a'])) # True
    print(ispostfix(['a'], [])) # False
    print(ispostfix(['a', 'b', 'c'], ['a', 'b', 'c'])) # True
    print(ispostfix(['b', 'c'], ['a', 'b', 'c'])) # True
    print(ispostfix(['a', 'b', 'c'], ['b', 'c'])) # False
    """