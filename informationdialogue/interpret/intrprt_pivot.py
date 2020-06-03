#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  4 10:55:32 2019

@author: tgelsema
"""

from informationdialogue.nlp.tknz import tokenize
from informationdialogue.interpret.intrprt_base import getorigin, getindexfrompattern
from informationdialogue.domainmodel.dm import prefvar, orderedobjecttype, overridetarget, lookup, interrogativepronouns, orientation
from informationdialogue.kind.knd import ObjectType, Constant, Variable, ObjectTypeRelation
from informationdialogue.learn.lrn import gettargetindexfrommodelandtokenizer



def getnexttarget(objectlist, keywordlist, tokenlist, target):
    possibletargetlist = []
    possibletargetlist.append(getindexfrompattern(['<whowhat>', '<ot>'], 1, 0, keywordlist, False))
    possibletargetlist.append(getindexfrompattern(['<ot>', '<with>'], 0, 0, keywordlist, False))
    possibletargetlist.append(getindexfrompattern(['<const>', '<with>'], 0, 0, keywordlist, False))
    possibletargetlist.append(getindexfrompattern(['<ot>', '<whowhat>'], 0, 0, keywordlist, False))
    possibletargetlist.append(getindexfrompattern(['<whowhat>', '<ot>'], 1, 0, keywordlist, True))
    possibletargetlist.append(getindexfrompattern(['<whowhat>', '<const>', '<ot>'], 2, 0, keywordlist, False))
    possibletargetlist.append(getindexfrompattern(['<whowhat>', '<const>', '<const>'], 2, 0, keywordlist, False))
    possibletargetlist.append(getindexfrompattern(['<whowhat>', '<const>'], 1, 0, keywordlist, False))
    possibletargetlist.append(getindexfrompattern(['<const>', '<ot>'], 1, 0, keywordlist, False))
    possibletargetlist.append(getindexfrompattern(['<const>', '<const>'], 1, 0, keywordlist, False))
    possibletargetlist.append(getindexfrompattern(['<ot>'], 0, 0, keywordlist, False))
    possibletargetlist.append(getindexfrompattern(['<const>'], 0, 0, keywordlist, False))
    for p in possibletargetlist:
        if p != -1:
            obj = objectlist[p]
            if isinstance(obj, Constant):
                if obj.codomain in overridetarget.keys():
                    obj = overridetarget[obj.codomain]
            if not isinstance(obj, Constant):
                return obj
    return None

                
def converttonexttarget(objectlist, keywordlist, tokenlist, k):
    if keywordlist[k] == '<ot>':
        return objectlist[k]
    if keywordlist[k] == '<const>':
        if objectlist[k].codomain in prefvar.keys():
            return prefvar[objectlist[k].codomain].domain
    if keywordlist[k] == '<otr>' or keywordlist[k] == '<numvar>':
        return objectlist[k].domain
    return None

def getpivot(objectlist, keywordlist):
    """Given a list of objects from the domain model, return the object (not
    neccessarily in the list) from the domain model that is the 'origin' of all
    objects in the list, in the sense that there exist paths in the domain
    model originating from the pivot to all elements in the list. Correct for
    occurrences of keywords '<greatest>' or '<smallest>', as e.g., the query 'wat is
    de grootste gemeente?' expects (according to the domain model) the object
    type 'persoon' to be the subject of counting. Therefore 'persoon' is the
    pivot in that case.
    """
    pivot = None
    for o in objectlist:
        candidate = None
        if o != None:
            if o.__class__.__name__ == 'ObjectType':
                candidate = o
            elif o.__class__.__name__ == 'ObjectTypeRelation' or o.__class__.__name__ == 'Variable':
                candidate = o.domain
            elif o.__class__.__name__ == 'Constant':
                if o.codomain in prefvar.keys():
                    candidate = prefvar[o.codomain].domain
            elif isinstance(o, list):
                if len(o) > 0:
                    if o[0].__class__.__name__ == 'Variable':
                        candidate = o[0].domain
            else:
                candidate = None
            possiblepivot = getorigin(pivot, candidate)
            if possiblepivot != None:
                pivot = possiblepivot
    orderedobjecttypelist = []
    orderedobjecttypelist.append(getindexfrompattern(['<greatest>', '<ot>'], 1, 0, keywordlist, True))
    orderedobjecttypelist.append(getindexfrompattern(['<smallest>', '<ot>'], 1, 0, keywordlist, True))
    orderedobjecttypelist.append(getindexfrompattern(['<greatest>', '<const>', '<ot>'], 2, 0, keywordlist, True))
    orderedobjecttypelist.append(getindexfrompattern(['<smallest>', '<const>', '<ot>'], 2, 0, keywordlist, True))
    orderedobjecttypelist.append(getindexfrompattern(['<ot>', '<greatest>'], 0, 0, keywordlist, True))
    orderedobjecttypelist.append(getindexfrompattern(['<ot>', '<smallest>'], 0, 0, keywordlist, True))
    orderedobjecttypelist.append(getindexfrompattern(['<geatest>', '<const>'], 0, 0, keywordlist, True))
    orderedobjecttypelist.append(getindexfrompattern(['<smallest>', '<const>'], 0, 0, keywordlist, True))
    orderedobjecttypelist.append(getindexfrompattern(['<const>', '<greatest>'], 0, 0, keywordlist, True))
    orderedobjecttypelist.append(getindexfrompattern(['<const>', '<smallest>'], 0, 0, keywordlist, True))
    orderedobjecttypelist.append(getindexfrompattern(['<ot>', '<const>', '<greatest>'], 0, 0, keywordlist, True))
    orderedobjecttypelist.append(getindexfrompattern(['<ot>', '<const>', '<smallest>'], 0, 0, keywordlist, True))
    orderedobjecttypelist.append(getindexfrompattern(['<ot>', '<prep>', '<const>', '<greatest>'], 0, 0, keywordlist, True))
    orderedobjecttypelist.append(getindexfrompattern(['<ot>', '<prep>', '<const>', '<smallest>'], 0, 0, keywordlist, True))
    for p in orderedobjecttypelist:
        if p != -1:
            if isinstance(objectlist[p], ObjectType):
                if pivot == objectlist[p]:
                    if pivot in orderedobjecttype.keys():
                        return orderedobjecttype[pivot].domain
            if isinstance(objectlist[p], Constant):
                if objectlist[p].codomain in prefvar.keys():
                    obj = prefvar[objectlist[p].codomain]
                    if pivot == obj:
                        if obj in orderedobjecttype.keys():
                            return orderedobjecttype[obj].domain
    return pivot

def hasorderedotorconst(keywordlist):
    orderedlist = []
    orderedlist.append(getindexfrompattern(['<greatest>', '<ot>'], 1, 0, keywordlist, False))
    orderedlist.append(getindexfrompattern(['<smallest>', '<ot>'], 1, 0, keywordlist, False))
    orderedlist.append(getindexfrompattern(['<greatest>', '<const>'], 1, 0, keywordlist, False))
    orderedlist.append(getindexfrompattern(['<smallest>', '<const>'], 1, 0, keywordlist, False))
    orderedlist.append(getindexfrompattern(['<greatest>', '<otr>'], 1, 0, keywordlist, False))
    orderedlist.append(getindexfrompattern(['<smallest>', '<otr>'], 1, 0, keywordlist, False))
    orderedlist.append(getindexfrompattern(['<ot>', '<greatest>'], 0, 0, keywordlist, True))
    orderedlist.append(getindexfrompattern(['<ot>', '<smallest>'], 0, 0, keywordlist, True))
    orderedlist.append(getindexfrompattern(['<const>', '<greatest>'], 0, 0, keywordlist, True))
    orderedlist.append(getindexfrompattern(['<const>', '<smallest>'], 0, 0, keywordlist, True))
    orderedlist.append(getindexfrompattern(['<otr>', '<greatest>'], 0, 0, keywordlist, True))
    orderedlist.append(getindexfrompattern(['<otr>', '<smallest>'], 0, 0, keywordlist, True))
    ordered = False
    for o in orderedlist:
        if o >= 0:
            ordered = True
    return ordered

def gettarget(tokenlist, objectlist, keywordlist, model, tokenizer, pivot):
    ordered = hasorderedotorconst(keywordlist)
    k = gettargetindexfrommodelandtokenizer(model, tokenizer, keywordlist)
    target = converttotarget(objectlist, keywordlist, tokenlist, k, ordered)
    if not isinstance(target, ObjectType):
        target = pivot # last resort
    return target

""" Depracated
def gettarget(objectlist, keywordlist, tokenlist, pivot):
    (k, ordered) = getpotentialtarget(objectlist, keywordlist, tokenlist, pivot)
    if k != -1:
        if converttotarget(objectlist, keywordlist, tokenlist, k, ordered) != None:
            return converttotarget(objectlist, keywordlist, tokenlist, k, ordered)
    return pivot
"""

def getpseudodimension(objectlist, keywordlist):
    """Will soon be deprecated and replaced by getpseudotarget().
    """
    pseudodimensionlist = []
    pseudodimensionlist.append(getindexfrompattern(['<whowhat>', '<ot>'], 1, 0, keywordlist, True))
    pseudodimensionlist.append(getindexfrompattern(['<whowhat>', '<const>'], 1, 0, keywordlist, True))
    pseudodimensionlist.append(getindexfrompattern(['<most>', '<ot>'], 1, 0, keywordlist, True))
    pseudodimensionlist.append(getindexfrompattern(['<greatest>', '<ot>'], 1, 0, keywordlist, True))
    pseudodimensionlist.append(getindexfrompattern(['<ot>', '<most>'], 0, 0, keywordlist, True))
    pseudodimensionlist.append(getindexfrompattern(['<ot>', '<greatest>'], 0, 0, keywordlist, True))
    pseudodimensionlist.append(getindexfrompattern(['<least>', '<ot>'], 1, 0, keywordlist, True))
    pseudodimensionlist.append(getindexfrompattern(['<smallest>', '<ot>'], 1, 0, keywordlist, True))
    pseudodimensionlist.append(getindexfrompattern(['<ot>', '<least>'], 0, 0, keywordlist, True))
    pseudodimensionlist.append(getindexfrompattern(['<ot>', '<smallest>'], 0, 0, keywordlist, True))
    pseudodimensionlist.append(getindexfrompattern(['<most>', '<const>'], 1, 0, keywordlist, True))
    pseudodimensionlist.append(getindexfrompattern(['<greatest>', '<const>'], 1, 0, keywordlist, True))
    pseudodimensionlist.append(getindexfrompattern(['<const>', '<most>'], 0, 0, keywordlist, True))
    pseudodimensionlist.append(getindexfrompattern(['<const>', '<greatest>'], 0, 0, keywordlist, True))
    pseudodimensionlist.append(getindexfrompattern(['<least>', '<const>'], 1, 0, keywordlist, True))
    pseudodimensionlist.append(getindexfrompattern(['<const>', '<least>'], 0, 0, keywordlist, True))
    pseudodimensionlist.append(getindexfrompattern(['<smallest>', '<const>'], 1, 0, keywordlist, True))
    pseudodimensionlist.append(getindexfrompattern(['<const>', '<smallest>'], 0, 0, keywordlist, True))
    pseudodimensionlist.append(getindexfrompattern(['<ot>'], 0, 0, keywordlist, True))
    pseudodimensionlist.append(getindexfrompattern(['<const>'], 0, 0, keywordlist, True))
    for p in pseudodimensionlist:
        if p != -1:
            obj = objectlist[p]
            if isinstance(obj, Constant):
                if obj.codomain in overridetarget.keys():
                    obj = overridetarget[obj.codomain]
            if not isinstance(obj, Constant):
                return obj
    return None

def getpotentialtarget(objectlist, keywordlist, tokenlist, pivot):
    """From a sieve of patterns applied to keywordlist, from objectlist get
    indices for potential targets. Then return the first potential target
    found. Note that the order in which patterns are applied is crucial in
    this algorithm: changing the order of patterns will possibly result in
    finding a different target. The target for a query is defined as the object
    type that is, more or less, the subject of the query. Targets will define
    whether a kappa correction must take place before aggregation, if there
    is a need for aggregation, of at all. A kappa correction will result in a
    query requesting all different (SELECT DISTINCT) objects corresponding to
    the query condition instead of requesting all (SELECT) such objects. If
    pivot equals target, no such correction is necessary.
    """
    potentialtargetlist = []
    ### The following patterns are heuristics for finding the target for a
    ### query, translated into a list of keywords. The first pattern that
    ### matches keywordlist will apply in retrieving the target. Order of the
    ### patterns below is thus crucial in the deduction of a target: this order
    ### acts like a sieve in finding a suitable target.
    # potentialtargetlist.append(getindexfrompattern(['<numvar>'], 0, keywordlist))
    potentialtargetlist.append(getindexfrompattern(['<numvar>'], 0, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<num>', '<ot>'], 1, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<num>', '<const>'], 1, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<num>', '<otr>'], 1, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<most>', '<ot>'], 1, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<least>', '<ot>'], 1, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<most>', '<const>'], 1, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<least>', '<const>'], 1, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<most>', '<otr>'], 1, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<least>', '<otr>'], 1, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<ot>', '<most>'], 1, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<ot>', '<least>'], 1, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<const>', '<most>'], 1, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<const>', '<least>'], 1, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<otr>', '<most>'], 1, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<otr>', '<least>'], 1, 0, keywordlist, True))
    potentialtargetlist.append([getindexfrompattern(['<greatest>', '<ot>'], 1, 0, keywordlist, True), 'ord'])
    potentialtargetlist.append([getindexfrompattern(['<smallest>', '<ot>'], 1, 0, keywordlist, True), 'ord'])
    potentialtargetlist.append([getindexfrompattern(['<greatest>', '<const>'], 1, 0, keywordlist, True), 'ord'])
    potentialtargetlist.append([getindexfrompattern(['<smallest>', '<const>'], 1, 0, keywordlist, True), 'ord'])
    potentialtargetlist.append([getindexfrompattern(['<greatest>', '<otr>'], 1, 0, keywordlist, True), 'ord'])
    potentialtargetlist.append([getindexfrompattern(['<smallest>', '<otr>'], 1, 0, keywordlist, True), 'ord'])
    potentialtargetlist.append([getindexfrompattern(['<ot>', '<greatest>'], 1, 0, keywordlist, True), 'ord'])
    potentialtargetlist.append([getindexfrompattern(['<ot>', '<smallest>'], 1, 0, keywordlist, True), 'ord'])
    potentialtargetlist.append([getindexfrompattern(['<const>', '<greatest>'], 1, 0, keywordlist, True), 'ord'])
    potentialtargetlist.append([getindexfrompattern(['<const>', '<smallest>'], 1, 0, keywordlist, True), 'ord'])
    potentialtargetlist.append([getindexfrompattern(['<otr>', '<greatest>'], 1, 0, keywordlist, True), 'ord'])
    potentialtargetlist.append([getindexfrompattern(['<otr>', '<smallest>'], 1, 0, keywordlist, True), 'ord'])
    potentialtargetlist.append(getindexfrompattern(['<howmany>', '<ot>'], 1, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<howmany>', '<const>'], 1, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<howmany>', '<otr>'], 1, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<ot>', '<prep>', '<all>', '<ot>'], 0, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<ot>', '<prep>', '<all>', '<const>'], 0, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<ot>', '<prep>', 'all', '<otr>'], 0, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<ot>', '<prep>', '<ot>'], 0, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<ot>', '<prep>', '<const>'], 0, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<otr>', '<prep>', '<whowhat>', '<ot>'], 0, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<otr>', '<prep>', '<whowhat>', '<const>'], 0, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<ot>', '<prep>', '<otr>'], 0, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<whowhat>', '<all>', '<ot>'], 2, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<whowhat>', '<all>', '<const>'], 2, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<whowhat>', '<all>', '<ot>'], 2, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<whowhat>', '<ot>'], 1, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<whowhat>', '<const>'], 1, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<whowhat>', '<otr>'], 1, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<otr>', '<whowhat>'], 0, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<prep>', '<ot>', '<all>', '<ot>'], 3, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<prep>', '<const>', '<all>', '<ot>'], 3, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<prep>', '<otr>', '<all>', '<ot>'], 3, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<prep>', '<all>', '<ot>', '<ot>'], 3, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<prep>', '<all>', '<const>', '<ot>'], 3, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<prep>', '<all>', '<otr>', '<ot>'], 3, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<prep>', '<ot>', '<ot>'], 2, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<prep>', '<const>', '<ot>'], 2, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<prep>', '<otr>', '<ot>'], 2, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<ot>', '<otr>'], 0, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<const>', '<otr>'], 0, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<ot>', '<const>', '<const>'], 0, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<const>', '<const>'], 1, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<const>', '<ot>'], 0, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<ot>', '<const>'], 1, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<all>', '<ot>'], 1, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<ot>', '<ot>'], 0, 0, keywordlist, True))
    potentialtargetlist.append(getindexfrompattern(['<ot>'], 0, 0, keywordlist, True))
    ordered = False
    for p in potentialtargetlist:
        if isinstance(p, list):
            p = p[0]
            ordered = True
        else:
            ordered = False
        if p != -1:
            return (p, ordered)
    return (-1, False)

"""
def converttotarget(objectlist, keywordlist, tokenlist, k, ordered):
    if k != -1:
        if keywordlist[k] == '<ot>':
            if ordered:
                if objectlist[k] in orderedobjecttype.keys():
                    return orderedobjecttype[objectlist[k]].domain
            return objectlist[k]
        elif keywordlist[k] == '<const>':
            if objectlist[k].codomain in overridetarget.keys():
                return overridetarget[objectlist[k].codomain]
        elif keywordlist[k] == '<numvar>':
            if objectlist[k].__class__.__name__ == 'Variable':
                return objectlist[k].domain
            else:
                return objectlist[k][0].domain
        elif keywordlist[k] == '<otr>':
            if (k > 0 and keywordlist[k - 1] == '<whowhat>'):
                if objectlist[k].domain in interrogativepronouns.keys():
                    if interrogativepronouns[objectlist[k].domain] == tokenlist[k - 1]:
                        return objectlist[k].domain
                if objectlist[k].codomain in interrogativepronouns.keys():
                    if interrogativepronouns[objectlist[k].codomain] == tokenlist[k - 1]:
                        return objectlist[k].codomain
            if (k + 1 < len(keywordlist) and keywordlist[k + 1] == '<whowhat>'):
                if objectlist[k].domain in interrogativepronouns.keys():
                    if interrogativepronouns[objectlist[k].domain] == tokenlist[k + 1]:
                        return objectlist[k].domain
                if objectlist[k].codomain in interrogativepronouns.keys():
                    if interrogativepronouns[objectlist[k].codomain] == tokenlist[k + 1]:
                        return objectlist[k].codomain
            return objectlist[k].domain
    return None
"""

def converttotarget(objectlist, keywordlist, tokenlist, k, ordered):
    target = None
    if k != -1:
        target = objectlist[k]
        if isinstance(target, ObjectTypeRelation):
            if (k > 0) and keywordlist[k - 1] == '<whowhat>':
                if target.domain in interrogativepronouns.keys():
                    if interrogativepronouns[target.domain] == tokenlist[k - 1]:
                        target = target.domain
                elif target.codomain in interrogativepronouns.keys():
                    if interrogativepronouns[target.codomain] == tokenlist[k - 1]:
                        target = target.codomain
            elif (k + 1 < len(keywordlist)) and keywordlist[k + 1] == '<whowhat>':
                if target.domain in interrogativepronouns.keys():
                    if interrogativepronouns[target.domain] == tokenlist[k + 1]:
                        target = target.domain
                elif target.codomain in interrogativepronouns.keys():
                    if interrogativepronouns[target.codomain] == tokenlist[k + 1]:
                        target = target.codomain
        if isinstance(target, ObjectTypeRelation):
            if target in orientation.keys():
                target = orientation[target]
            else:
                target = target.domain
        if isinstance(target, Constant):
            if target.codomain in overridetarget.keys():
                target = overridetarget[target.codomain]
        if isinstance(target, ObjectType):
            if ordered:
                if target in orderedobjecttype.keys():
                    target = orderedobjecttype[target].domain
        if keywordlist[k] == '<numvar>':
            if isinstance(target, Variable):
                target = target.domain
            else:
                target = target[0].domain
    return target

def test():
    line = 'De gemeente waar een persoon woont met de hoogste leeftijd'
    (tokenlist, objectlist, keywordlist) = tokenize(line, lookup)
    k = getindexfrompattern(['<ot>', '<whowhat>'], 0, 0, keywordlist, True)
    l = getindexfrompattern(['<whowhat>', '<ot>'], 1, 0, keywordlist, True)
    #### line = 'Tjalling woont op welk adres?'
    #### (tokenlist, objectlist, keywordlist) = tokenize(line, lookup)
    #### pivot = getpivot(objectlist, keywordlist)
    #### (k, ordered) = getpotentialtarget(objectlist, keywordlist, tokenlist, pivot)
    #### print(tokenlist)
    #### print(k)
    #### target = converttotarget(objectlist, keywordlist, tokenlist, k, ordered)
    # target = gettarget(objectlist, keywordlist, tokenlist, pivot)
    print(keywordlist)
    print(k)
    print(l)