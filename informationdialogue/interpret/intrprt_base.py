#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  4 10:40:17 2019

@author: tgelsema
"""

from informationdialogue.domainmodel.dm import domainmodel, whichway, getal, overridetarget, one, ones, alls
from informationdialogue.term.trm import Application, product, composition, cartesian_product, projection, alpha, inverse, inclusion
from informationdialogue.kind.knd import Variable, ObjectTypeRelation, Element

def getorigin(obj1, obj2):
    """Return obj1 if there is at least one path from obj1 to obj2 in the
    domain model. Conversely, return obj2 if there is a path from obj2 to obj1.
    If both obj1 and obj2 are not equal to None, inspect the domain model for
    the occurrence of an object type that has a path both to obj1 and obj2.
    Return the object type that is 'closest' to both obj1 and obj2. Note:
    getorigin is for now applied to arguments obj1 and obj2 that are both
    object types. If getorigin needs to be extended to any pair of types, then
    the statement 'if obj.sort == 'object type'' needs to be replaced with
    'if obj.kind == 'type''.
    """
    if obj1 == None:
        return obj2
    if getpaths(obj1, obj2) != []:
        return obj1
    if getpaths(obj2, obj1) != []:
        return obj2
    if obj1 != None and obj2 != None and obj1 != obj2:
        origin = None
        for obj in domainmodel:
            if obj.sort == 'object type':
                if getpaths(obj, obj1) != [] and getpaths(obj, obj2) != []:
                    if getpaths(origin, obj) != [] or origin == None:
                        origin = obj
        return origin
    return obj1

def getpaths(origin, destination):
    """Recursively perform a depth first search through the domain model and
    return all paths from origin to destination. Origin and destination can
    be any types in the model, and paths can be any sequences of elements in
    the domain model.
    """
    paths = []
    for obj in domainmodel:
        if obj.kind == 'element' and obj.domain.equals(origin):
            if obj.codomain.equals(destination):
                paths.append([obj])
            else:
                for path in getpaths(obj.codomain, destination):
                    p = path
                    p.append(obj)
                    if not p in paths:
                        paths.append(p)
    return paths

def getdomainlist(term):
    if isinstance(term.type.args[0], Application):
        if term.type.args[0].op == cartesian_product:
            return term.type.args[0].args
    return [term.type.args[0]]

def align(term1, term2):
    t1domlist = getdomainlist(term1)
    t2domlist = getdomainlist(term2)
    if t1domlist == t2domlist:
        return term1
    args = []
    for d in t1domlist:
        if d != one:
            if not d in t2domlist:
                return None
            else:
                args.append(makeprojection(t2domlist + [t2domlist.index(d) + 1]))
        else:
            return makecomposition([term1, alle(makecartesianproduct(t2domlist))])
    return makecomposition([term1, makeproduct(args)])

def isprefix(p, q):
    i = 0
    while i < len(p):
        if i >= len(q):
            return False
        if p[i] != q[i]:
            return False
        i += 1
    return True

def getoptimalpath(paths, clues, hint):
    optimalpath = []
    n = -1
    for path in paths:
        if hint != []:
            if isprefix(hint, path):
                return path
        k = 0
        for edge in path:
            for clue in clues:
                if edge.equals(clue):
                    k += 10
                if edge.domain.equals(clue) or edge.codomain.equals(clue):
                    k += 4
                if clue.kind == 'element' and clue.domain.equals(one) and clue.codomain in overridetarget.keys():
                    otype = overridetarget[clue.codomain]
                    if edge.domain.equals(otype) or edge.codomain.equals(otype):
                        k += 2
            if edge.domain in whichway.keys():
                if edge == whichway[edge.domain]:
                    k += 1
        if k > n:
            n = k
            optimalpath = path
        elif k == n and len(optimalpath) < len(path):
            optimalpath = path
    return optimalpath

def makecomposition(args):
    if len(args) == 0:
        return None
    elif len(args) == 1:
        return args[0]
    else:
        return Application(composition, args)
    
def makeproduct(args):
    if len(args) == 0:
        return None
    elif len(args) == 1:
        return args[0]
    else:
        return Application(product, args)
    
def makecartesianproduct(args):
    if len(args) == 0:
        return None
    elif len(args) == 1:
        return args[0]
    else:
        return Application(cartesian_product, args)
    
def makealpha(args):
    if len(args) != 2:
        return None
    else:
        return Application(alpha, args)
    
def makeprojection(args):
    if len(args) < 2:
        return None
    else:
        return Application(projection, args)
    
def makeprojectioneasy(arg, n):
    if not isinstance(arg.type.args[1], Application):
        return arg
    if arg.type.args[1].op != cartesian_product:
        return arg
    pargs = arg.type.args[1].args.copy()
    pargs.append(n)
    return makecomposition([makeprojection(pargs), arg])
    
def makekappa(args):
    if len(args) != 1:
        return None
    else:
        return Application(inverse, args)
    
def makeinclusion(args):
    if len(args) < 2:
        return None
    else:
        return Application(inclusion, args)
    
def terminlist(term, lst):
    for t in lst:
        if t.__repr__() == term.__repr__():
            return True
    return False

def een(p):
    title = "een(%s)" % p.name
    for d in ones:
        if d.name == title:
            return d
    return Variable(name=title, domain=p, codomain=getal)

def alle(p):
    title = "alle(%s)" % p.__repr__()
    for d in alls:
        if d.name == title:
            return d
    return Variable(name=title, domain=p, codomain=one)

def identity(p):
    if p.__class__.__name__ == 'ObjectType':
        return ObjectTypeRelation(name="id(%s)" % p.__repr__(), domain=p, codomain=p)
    return Element(name="id(%s)" % p.__repr__(), sortix=22, domain=p, codomain=p) # unspecified element

def lookforward(k, keywordlist):
    """In keywordlist at position k, return the index to the next keyword not
    equal to '<unk>'. Return len(keywordlist) if no such keyword exists.
    """
    n = k + 1
    while n < len(keywordlist) and keywordlist[n] == '<unk>':
        n += 1
    return n
    
def lookback(k, keywordlist):
    """In keywordlist at position k, return the index to the previous keyword
    not equal to '<unk>'. Return -1 if no such keyword exists.
    """
    n = k - 1
    while n >= 0 and keywordlist[n] == '<unk>':
        n -= 1
    return n

def getcontext(k, keywordlist):
    """In keywordlist indexed by k, get the two keywords (not equal to '<unk>')
    in the keywordlist ahead of index k (if they exist) as well as the two
    keywords (not equal to '<unk>') before k (if they exist). Return a list of
    the indices to these four keywords.
    """
    f1 = lookforward(k, keywordlist)
    f2 = lookforward(f1, keywordlist)
    b1 = lookback(k, keywordlist)
    b2 = lookback(b1, keywordlist)
    return [b2, b1, f1, f2]

def getclueindexfrompattern(pattern, clueidx, context, keywordlist):
    """Get the index in keywordlist to a clue, a keyword that is indexed by
    clueidx in pattern, if that pattern matches with context. Context is a list
    of four indices for keywordlist: two indices before a certain index k and
    two indices after k. Pattern is a list with a length not exceeding the
    length of context + 1 of keys, that contains a special marker '*'
    indicating the position for k.
    """
    centeroffset = pattern.index('*')
    match = True
    patternidx = 0
    pastcenter = 0
    while match and patternidx < len(pattern):
        if patternidx != centeroffset:
            if context[patternidx + len(context) // 2 - centeroffset - pastcenter] == None:
                match = False
            elif context[patternidx + len(context) // 2 - centeroffset - pastcenter] >= len(keywordlist):
                match = False
            elif context[patternidx + len(context) // 2 - centeroffset - pastcenter] < 0:
                match = False
            elif pattern[patternidx] != keywordlist[context[patternidx + len(context) // 2 - centeroffset - pastcenter]]:
                match = False  
        else:
            pastcenter = 1
        patternidx += 1
    if match:
        if clueidx > centeroffset:
            pastcenter = 1
        else:
            pastcenter = 0
        return context[clueidx + len(context) // 2 - centeroffset - pastcenter]
    else:
        return -1
    
def getindexfrompattern(pattern, patternidx, index, keywordlist, discardunk):
    """Match the first occurrence of pattern in keywordlist starting at index
    and return the index in keywordlist matching with patternidx in pattern.
    Discard occurrences of '<unk>' in keywordlist. Also: assume that pattern
    does not include occurrences of '<unk>'.
    """
    i = index
    while i < len(keywordlist) and i >= 0:
        j = match(pattern, patternidx, i, keywordlist, discardunk)
        if j != -1:
            return j
        i += 1
    return -1

def match(pattern, patternidx, index, keywordlist, discardunk):
    """Return True if pattern matches with keywordlist starting at index, else
    return False. Discard occurrences of '<unk>' in keywordlist, except if
    keywordlist[index] == '<unk>': in that case, return False.
    """
    foundindex = -1
    if index >= len(keywordlist) or index < 0 or keywordlist[index] == '<unk>':
        return -1
    if patternidx >= len(pattern) or patternidx < 0:
        return -1
    i = index
    j = 0
    while j < len(pattern):
        if i + j >= len(keywordlist) or i + j < 0:
            return -1
        if pattern[j] != keywordlist[i + j] and not discardunk:
            return -1
        if pattern[j] != keywordlist[i + j] and keywordlist[i + j] != '<unk>':
            return -1
        if j == patternidx:
            foundindex = i + j
        if keywordlist[i + j] == '<unk>' and discardunk:
            i += 1
        else:
            j += 1
    return foundindex

def insertsorted(lst, obj):
    """Insert into lst the argument obj, such that the list args remains
    sorted. As sorting criterium use the string representation of obj,
    obtained by the .__repr__() method. Return the list with obj inserted.
    """
    i = 0
    while i < len(lst) and lst[i].__repr__() > obj.__repr__():
        i += 1
    lst.insert(i, obj)
    return lst