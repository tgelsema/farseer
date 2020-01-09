#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 14:51:08 2019

@author: tgelsema
"""

from informationdialogue.domainmodel.dm import lookup
from informationdialogue.nlp.tknz import tokenize

def getorder(keywordlist):
    i = 0
    while i < len(keywordlist):
        if keywordlist[i] == '<most>' or keywordlist[i] == '<greatest>':
            return 'desc'
        if keywordlist[i] == '<least>' or keywordlist[i] == '<smallest>':
            return 'asc'
        i += 1
    return ''

"""
def getorder(objectlist, keywordlist):
    Probably deprecated: does not perform well. Better is to have each
    individual class where order is of importance to have the object
    returned to which order applies.
    i = 0
    while i < len(keywordlist):
        if keywordlist[i] == '<most>' or keywordlist[i] == '<least>' or keywordlist[i] == '<greatest>' or keywordlist[i] == '<smallest>':
            obj = vicinity(objectlist, i)
            if keywordlist[i] == '<most>' or keywordlist[i] == '<greatest>':
                order = 'desc'
            if keywordlist[i] == '<least>' or keywordlist[i] == '<smallest>':
                order = 'asc'
            if obj != None:
                if obj.__class__.__name__ == 'ObjectType':
                    if obj in orderedobjecttype.keys():
                        obj = orderedobjecttype[obj]
                return [obj, order]
        i += 1
    return []
"""

def vicinity(objectlist, k):
    """Probably deprecated: does not perform well. Better is to have each
    individual class where order is of importance to have the object
    returned to which order applies.
    """
    i = 1
    while k + i < len(objectlist) or k - i >= 0:
        if k + i < len(objectlist):
            if objectlist[k + i] != None:
                if objectlist[k + i].__class__.__name__ == 'Variable' or objectlist[k + i].__class__.__name__ == 'ObjectType':
                    return objectlist[k + i]
        if k - i >= 0:
            if objectlist[k - i] != None:
                if objectlist[k - i].__class__.__name__ == 'Variable' or objectlist[k - i].__class__.__name__ == 'ObjectType':
                    return objectlist[k - i]
        i += 1
    return []

def test():
    line = 'de grootste persoon'
    (tokenlist, objectlist, keywordlist) = tokenize(line, lookup)
    print(getorder(objectlist, keywordlist))