#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 11:13:43 2019

@author: tgelsema
"""

from informationdialogue.interpret.intrprt_base import insertsorted, getpaths, getoptimalpath

def getpathfromvar(objectlist, keywordlist, var, target):
    i = 0
    clues = []
    while i < len(keywordlist):
        if keywordlist[i] == '<otr>':
            clues.append(objectlist[i])
        i += 1
    return getoptimalpath(getpaths(var.domain, target), clues, [])

def getpathstonumvars(objectlist, keywordlist, target):
    paths = []
    i = 0
    clues = []
    while i < len(keywordlist):
        if keywordlist[i] == '<otr>':
            clues.append(objectlist[i])
        i += 1
    i = 0
    while i < len(keywordlist):
        if keywordlist[i] == '<numvar>':
            if isinstance(objectlist[i], list):
                var = objectlist[i][0]
            else:
                var = objectlist[i]
            path = []
            if not var.domain.equals(target):
                path = getoptimalpath(getpaths(target, var.domain), clues, [])
            path.insert(0, var)
            paths = insertsorted(paths, path)
        i += 1
    return paths

def getpathstocatvars(objectlist, keywordlist, target):
    paths = []
    i = 0
    clues = []
    while i < len(keywordlist):
        if keywordlist[i] == '<otr>':
            clues.append(objectlist[i])
        i += 1
    i = 0
    while i < len(keywordlist):
        if keywordlist[i] == '<catvar>':
            var = objectlist[i]
            path = []
            if not var.domain.equals(target):
                path = getoptimalpath(getpaths(target, var.domain), clues, [])
            path.insert(0, var)
            paths = insertsorted(paths, path)
        i += 1
    return paths

def getpathstoobjecttypes(objectlist, keywordlist, pivot, target):
    paths = []
    i = 0
    clues = []
    while i < len(keywordlist):
        if keywordlist[i] == '<otr>':
            clues.append(objectlist[i])
        i += 1
    i = 0
    while i < len(keywordlist):
        if keywordlist[i] == '<ot>':
            if not objectlist[i].equals(pivot) and not objectlist[i].equals(target):
                path = getoptimalpath(getpaths(target, objectlist[i]), clues, [])
                if path != None and path != []:
                    paths = insertsorted(paths, path)
        i += 1
    return paths