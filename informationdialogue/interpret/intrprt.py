#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  4 10:40:17 2019

@author: tgelsema
"""
# from intrprt_base import *
from informationdialogue.interpret.intrprt_iota import getiota, getkappa, getiotapaths, makeiota
from informationdialogue.interpret.intrprt_pivot import getpivot, gettarget, getpseudodimension, getnexttarget
from informationdialogue.interpret.intrprt_dims import getdimensionpaths, appendvariablestopaths
from informationdialogue.interpret.intrprt_base import een, alle, makecomposition, makeproduct, makealpha, makeprojectioneasy, align
from informationdialogue.interpret.intrprt_split import getsplit, getsplitfromkappa, getsplitfromobjectlist
from informationdialogue.interpret.intrprt_vars import getpathstonumvars, getpathstocatvars, getpathstoobjecttypes, getpathfromvar
from informationdialogue.interpret.intrprt_order import getorder
from informationdialogue.learn.lrn import getsavedmodelandtokenizer_classes, getclassfrommodelandtokenizer, getsavedmodelandtokenizer_targetindex
from informationdialogue.nlp.tknz import tokenize
from informationdialogue.domainmodel.dm import gedeelddoor, lookup, defaults, orderedobjecttype

def ask(line = 'Wie wonen er in Den Haag?'):
    (classmodel, classtokenizer) = getsavedmodelandtokenizer_classes()
    (targetmodel, targettokenizer) = getsavedmodelandtokenizer_targetindex()
    (tokenlist, objectlist, keywordlist) = tokenize(line, lookup)
    print(tokenlist)
    print(objectlist)
    print(keywordlist)
    print()
    cls = getclassfrommodelandtokenizer(classmodel, classtokenizer, keywordlist)
    target = gettarget(tokenlist, objectlist, keywordlist, targetmodel, targettokenizer)
    term = interpret(tokenlist, objectlist, keywordlist, target, cls)
    if isinstance(term, list):
        print('var: %s\norder: "%s"' % (term[1].more(), term[2]))
        term = term[0]
    print(term.more())
    return

def interpret(tokenlist, objectlist, keywordlist, target, cls):
    pivot = getpivot(objectlist, keywordlist)
    # target = gettarget(objectlist, keywordlist, tokenlist, pivot)
    # print('pivot: %s' % pivot)
    # print('target: %s' % target)
    pathstonumvars = getpathstonumvars(objectlist, keywordlist, target)
    pathstoclassvars = getpathstocatvars(objectlist, keywordlist, target)
    pathstootypes = getpathstoobjecttypes(objectlist, keywordlist, pivot, target)
    pathstootypes = appendvariablestopaths(pathstootypes)
    order = getorder(keywordlist)
    numvars = []
    classvars = []
    otypes = []
    for path in pathstonumvars:
        numvars.append(makecomposition(path))
    for path in pathstoclassvars:
        classvars.append(makecomposition(path))
    for path in pathstootypes:
        otypes.append(makecomposition(path))
    iota = getiota(objectlist, keywordlist, pivot, target)
    (paths, pathsfrompivot, ignore) = getdimensionpaths(objectlist, keywordlist, pivot, target, None, {})
    kappa = getkappa(objectlist, keywordlist, pivot, target, iota, pathsfrompivot, None)
    if cls == 1:
        return assembletermforclass1(target, numvars, classvars, otypes, kappa, True)
    elif cls == 2:
        return assembletermforclass2and3(objectlist, keywordlist, pivot, target, pathsfrompivot, [], iota, None)
    elif cls == 3:
        return assembletermforclass2and3(objectlist, keywordlist, pivot, target, pathsfrompivot, numvars, iota, None)
    elif cls == 4:
        return assembletermforclass4(objectlist, keywordlist, pivot, target, pathsfrompivot, numvars, kappa, iota)
    elif cls == 5:
        return assembletermforclass5(objectlist, keywordlist, pivot, target, pathsfrompivot, kappa, iota)
    elif cls == 6:
        return assembletermforclass6(objectlist, keywordlist, target, iota, order)
    elif cls == 7:
        return assembletermforclass7(objectlist, keywordlist, tokenlist, target, pivot, kappa, iota, order)
    elif cls == 8:
        return assembletermforclass8(objectlist, keywordlist, tokenlist, target, pivot, numvars, kappa, iota, order)
    elif cls == 9:
        return assembletermforclass9(objectlist, keywordlist, tokenlist, target, pivot, numvars, kappa, iota, order)
    elif cls == 10:
        return assembletermforclass10(objectlist, keywordlist, tokenlist, target, numvars, otypes, kappa, order)
    elif cls == 11:
        return assembletermforclass11(objectlist, keywordlist, tokenlist, target, pivot, kappa, iota, order)
    elif cls == 0:
        return None
    return None


def insertpseudodimension(objectlist, keywordlist, tokenlist, pseudodimension):
    """For class 7 - 11 queries, say of the form
        'Welke gemeente heeft gemiddeld het grootste aantal personen op een
        adres?'
    which have an object type ('gemeente', a pseudodimension),
    that has to act as a dimension in the resulting term. A little trick is
    used to let the routine getdimenionpaths() detect this dimension: just in
    front of the object type (the pseudodimension) the word 'per' is inserted
    in tokenlist and suitable other terms are inserted in keywordlist and
    tokenlist. If the pseudodimension is not found (as in the case that
    pseudodimension is 'persoon', but that has been derived from a constant,
    'griffier' say) the words 'per persoon' are inserted at the end of
    tokenlist.
    """
    i = 0
    while i < len(keywordlist) and objectlist[i] != pseudodimension:
        i += 1
    if i != len(keywordlist):
        keywordlist.insert(i, '<per>')
        objectlist.insert(i, None)
        tokenlist.insert(i, 'per')
    else:
        keywordlist.insert(i, '<per>')
        keywordlist.insert(i + 1, '<ot>')
        objectlist.insert(i, None)
        objectlist.insert(i + 1, pseudodimension)
        tokenlist.insert(i, 'per')
        tokenlist.insert(i + 1, pseudodimension.__repr__())
    return (objectlist, keywordlist, tokenlist)

def assembletermforclass11(objectlist, keywordlist, tokenlist, target, pivot, kappa, iota, order):
    """Build a term for class 11 queries, which are of the general form
        'Welke gemeente heeft gemiddeld het grootste aantal personen op
        een adres?'
    which requires calculating an average and a total. Queries of class 11 are
    thus ditributed to class 5, after a (pseudo-) dimension is inserted into
    objectlist, keywordlist and tokenlist. In the example above, the average
    number of persons per 'adres' is calculated for each 'gemeente', so
    'gemeente' forms the (pseudo-) dimension here.
    """
    pseudodimension = getnexttarget(objectlist, keywordlist, tokenlist, target)
    if pseudodimension == None:
        return None
    #### print('used target: %s' % target)
    #### print('nexttarget (pseudodimension): %s' % pseudodimension)
    (objectlist, keywordlist, tokenlist) = insertpseudodimension(objectlist, keywordlist, tokenlist, pseudodimension)
    (ignorepaths, paths, ignoredict) = getdimensionpaths(objectlist, keywordlist, pivot, target, None, {})
    return [assembletermforclass5(objectlist, keywordlist, pivot, target, paths, kappa, iota), een(target), order]

def assembletermforclass10(objectlist, keywordlist, tokenlist, target, numvars, otypes, kappa, order):
    """Build a term for class 10 queries, which are of the form
        'In welke gemeente wordt het meeste verdiend'
    and which does not require aggregation. (Note that this differs from a
    query of the form
        'In welke gemeente wordt in totaal het meeste verdiend'
    which is of type 8). Type 10 queries are thus distributed to class 1, where
    all object types (and variables) in the query (objectlist) are treated as
    variables.
    """
    pseudodimension = getnexttarget(objectlist, keywordlist, tokenlist, target)
    if pseudodimension == None or pseudodimension == target:
        includetargetdefaults = True
    else:
        includetargetdefaults = False
    return [assembletermforclass1(target, numvars, [], otypes, kappa, includetargetdefaults), numvars[0], order]

def assembletermforclass9(objectlist, keywordlist, tokenlist, target, pivot, numvars, kappa, iota, order):
    """Build a term for class 9 queries, which are of the form
        'Welke gemeente heeft de kleinste gemiddelde leeftijd?'
    which requires calculating an average. Class 9 queries are thus distributed
    to class 4, after a (pseudo-) dimension is inserted into objectlist,
    keywordlist and tokenlist. In the example above, the average 'leeftijd' is
    calculated for each 'gemeente', so 'gemeente' forms the dimension for the
    class 4 query.
    """
    pseudodimension = getnexttarget(objectlist, keywordlist, tokenlist, target)
    if pseudodimension == None:
        return None
    (objectlist, keywordlist, tokenlist) = insertpseudodimension(objectlist, keywordlist, tokenlist, pseudodimension)
    (ignorepaths, paths, ignoredict) = getdimensionpaths(objectlist, keywordlist, pivot, target, None, {})
    return [assembletermforclass4(objectlist, keywordlist, pivot, target, paths, numvars, kappa, iota), numvars[0], order]

def assembletermforclass8(objectlist, keywordlist, tokenlist, target, pivot, numvars, kappa, iota, order):
    """Build a term for class 8 queries, which are of the form
        'Op welk adres wordt het meeste verdiend in totaal?'
    which requires summing over a numerical variable. Class 8 queries are thus
    distributed to class 3, after a (pseudo-) dimension is inserted into
    objectlist, keywordlist and tokenlist. In the example above, the sum
    over 'inkomen' (verdiend) is calculated for each 'adres', so 'adres' forms
    the dimension for the class 3 query.
    """
    pseudodimension = getnexttarget(objectlist, keywordlist, tokenlist, target)
    if pseudodimension == None:
        return None
    (objectlist, keywordlist, tokenlist) = insertpseudodimension(objectlist, keywordlist, tokenlist, pseudodimension)
    (ignorepaths, paths, ignoredict) = getdimensionpaths(objectlist, keywordlist, pivot, target, None, {})
    return [assembletermforclass2and3(objectlist, keywordlist, pivot, target, paths, numvars, iota, None), numvars[0], order]

def assembletermforclass7(objectlist, keywordlist, tokenlist, target, pivot, kappa, iota, order):
    """Build a term for class 7 queries, which are of the form
        'In welke gemeente wonen de meeste (minste) personen?'
    and which require counting. Class 7 queries are thus distributed
    to class 2, after a (pseudo-) dimension is inserted in objectlist,
    keywordlist and tokenlist. In the example above, 'gemeente' is the
    object type that is marked (by inserting 'per' just in front of it) as
    a dimension. In this way, 'personen' are counted for each 'gemeente'.
    """
    pseudodimension = getnexttarget(objectlist, keywordlist, tokenlist, target)
    if pseudodimension == None:
        return None
    (objectlist, keywordlist, tokenlist) = insertpseudodimension(objectlist, keywordlist, tokenlist, pseudodimension)
    (ignorepaths, paths, ignoredict) = getdimensionpaths(objectlist, keywordlist, pivot, target, None, {})
    return [assembletermforclass2and3(objectlist, keywordlist, pivot, target, paths, [een(target)], iota, None), een(target), order]

def assembletermforclass6(objectlist, keywordlist, target, iota, order):
    """Build a term for class 6, which expresses a query of the form
        'Welke gemeente is het grootst (kleinst)?'
    or variants like
        'Wat is de grootste (kleinste) gemeente?'
    by distributing it to other classes (class 1 or class 3) depending on
    whether calculating the biggest (smallest) such cases requires
    aggregation. In case the variable associated with calculating the biggest
    (smallest) is a variable defined for target, aggregation is not necessary,
    as in the case
        'wat is het grootste bedrijf in Delft'
    depends on 'omzet' only, which is defined for 'bedrijf'. In the two cases
    above the calculation of the largest (smallest) 'gemeente' depends on
    aggregating over 'een(persoon)'.
    """
    pseudodimension = getpseudodimension(objectlist, keywordlist)
    if pseudodimension == None:
        return None
    if pseudodimension in orderedobjecttype.keys():
        var = orderedobjecttype[pseudodimension]
    else:
        return None
    if var.domain == pseudodimension:
        return [assembletermforclass1(target, [var], [], [], iota, True), var, order]
    else:
        path = getpathfromvar(objectlist, keywordlist, var, pseudodimension)
        return [assembletermforclass2and3(objectlist, keywordlist, var.domain, target, [path], [var], iota, None), var, order]   

def assembletermforclass1(target, numvars, classvars, otypes, kappa, includetargetdefaults):
    """Build a term for class 1, which expresses a number of variables for
    target, with or without selection criteria given by kappa. The resulting
    term is thus of the form
            v
    with v possibly a product of variables, or it is of the form
            v o i(y)
    or
            v o k(y)
    depending on whether or not pivot equals target. Return the resulting term
    thus constructed.
    """
    args = []
    if includetargetdefaults:
        if target in defaults.keys():
            for d in defaults[target]:
                if not d in args:
                    args.append(d)
    for n in numvars:
        if not n in args:
            args.append(n)
    for c in classvars:
        if not c in args:
            args.append(c)
    for o in otypes:
        if not o in args:
            args.append(o)
    v = makeproduct(args)
    if kappa != None:
        v = makecomposition([v, kappa])
    return v

def assembletermforclass2and3(objectlist, keywordlist, pivot, target, paths, numvars, iota, split):
    """Build a class 2 term, which is of the form
            a(v, w).
    In the simplest case, v = een(target) and w = alle(target), when no
    selections and dimensions apply and when pivot = target. When selections
    apply, the above case turns into
            a(een(target) o z, alle(target) o z)
    where z is a iota term. When also dimensions apply, v and w generally
    become
            v = een(target) o z
    and
            w = <n(a1,..,an,1)o<u1,..,un>oz,..,n(a1,..,an,n)o<u1,..,un>oz>
    which, after some rewriting is just
            w = <u1,..,un> o z.
    In the case a kappa term applies (i.e., when pivot does not equal target)
    we have in general
            z = k(<u1,..,un> o i(---))
    where '---' indicate proper arguments for a iota term, and we have
            v = een(target) o n(a1,..,an,1) o z
    and
            w = <n(a1,..,an,2) o z, ..., n(a1,..,an,n) o z>
    which in general cannot be simplified. Return the term thus composed.
    
    Class 2 terms are meant to express requests like:
            'Aantal banen'
            'Aantal banen in Leiden'
            'Aantal banen per functie in Leiden'
            'Aantal werknemers per bedrijf per functie in Leiden'
    Only in the last example the general case applies.
    
    A class 3 term is built in just the same way, only then v is of the form
          v = <v1, ..., vk> o z
    where the vi are numerical variables, or v is of the more general form in
    the case a kappa term applies.
    
    Class 3 terms are meant to express requests like:
          'totale omzet in de bouwnijverheid'
          'in Den Haag op de Meppelerweg wat is het totale inkomen?'
          'in Leiden bij bedrijven wat is het totale salaris naar functie?'
          'van personen naar gemeente en geslacht het totale inkomen'
          'de totale omzet van alle bedrijven naar activiteit en gemeente van vestiging'
          'het totale inkomen van werknemers in de zorg in Leiden'
    Only in the last example the general case applies.
    """
    # default case: assume pivot equals target and no selections or dimensions apply
    kappa = getkappa(objectlist, keywordlist, pivot, target, iota, paths, split)
    if numvars != []:
        v = makeproduct(numvars)
    else:
        v = een(target)
    w = alle(target)
    z = None
    if iota != None and pivot == target:
        w = makecomposition([w, iota]) 
        v = makecomposition([v, iota])
    # the cases below are the ones in which kappa is critical
    i = 0
    if pivot != target:
        z = makeprojectioneasy(kappa, 1)
        w = makecomposition([w, z])
        i = 1
        if split != None:
            i += 1
    if paths != [] and paths != [[]]:
        if i == 0 and len(paths) == 1:
            w = kappa
        else:
            j = 0
            zs = []
            while j < len(paths):
                zs.append(makeprojectioneasy(kappa, i + 1))
                i += 1
                j += 1
            w = makeproduct(zs)
    if z != None:
        v = makecomposition([v, z])
    return makealpha([v, w])

def assembletermforclass4(objectlist, keywordlist, pivot, target, paths, numvars, kappa, iota):
    """Build a class 4 term which is of the general form
            a(x(p), w) / a(een(p), w)
    by building seperate terms for nominator and demoninator, using routine
    'assembleforclass2and3()'. See there for the more general forms the
    term returned can assume.
    
    Note that denominator and nominator both reference to the same target 'p'.
    This might not be what is expected from, e.g., a query of the form
    'gemiddeld inkomen op een adres naar geslacht en gemeente'
    where the nominator sums over 'inkomen(persoon)' and the denominator
    sums over 'een(persoon)', thereby ignoring the reference to 'adres'. In
    future implementations, one might allow denominator and nominator to
    reference to different targets. See also the implementation of
    'assembletermforclass5', where a split is extracted from the query. One
    must observe that, e.g., a query like 'gemiddelde leeftijd op een adres
    naar geslacht en gemeente' becomes dubious.
    """
    if numvars == []:
        return None
    x = numvars[0]
    
    z1 = assembletermforclass2and3(objectlist, keywordlist, pivot, target, paths, [x], iota, None)
    z2 = assembletermforclass2and3(objectlist, keywordlist, pivot, target, paths, [], iota, None)
     
    return makecomposition([gedeelddoor, makeproduct([z1, z2])])

def assembletermforclass5(objectlist, keywordlist, pivot, target, paths, kappa, iota):
    """Build a class 5 term, which expresses an average, i.e., a numerator and
    a denominator, which are both aggregate terms for counting objects. The
    numerator counts the objects associated with the target. The code below
    first tries to find the type of objects the denominator counts (the split).
    If no split is found, None is returned. Then dimensions associated with
    the numerator and the denominator are discovered: they need not be the
    same, as even their number may differ, but they must be aligned later.
    In short, the dimensions for the numerator are paths that have the pivot
    as origin and the dimensions for the denominator have the split as origin.
    To ensure both numerator and denominator can be put together in a product
    construction, a correction term for the denominator must be found in the
    general case in order to connect the dimensions for the numerator with
    those for the denominator ('alignment'). The term returned is of the form
            a(x, w) / a(y, u) o c
    where c is the correction term and the a's represent alpha (aggregation)
    terms, and where x counts target objects individually - i.e.,
    x=een(target) - and y counts split objects individually - i.e.,
    y=een(split). The construction of both denominator and numerator is
    diverted to the routine 'assembletermforclass2and3()' Selection criteria as
    well as kappa correction or iota selection may apply to both x and w,
    i.e., x might also be a composition of een(target) with a iota or kappa
    term, and w might also be a composition of dimensions with a iota or kappa
    term. Kappa does not apply to y and u, but iota might. This routine also
    serves terms that have the simple form above, without any iota or kappa
    terms.
    """
    split = None
    if paths != []:
        split = getsplit(objectlist, keywordlist, target, paths)
    if kappa != None and split == None:
        split = getsplitfromkappa(objectlist, keywordlist, target, kappa)
    if split == None:
        split = getsplitfromobjectlist(objectlist, keywordlist, target)
    if split == None:
        return None
    (pathsignore, numdimpaths, pathsdict) = getdimensionpaths(objectlist, keywordlist, split, split, split, {})
    (pathsignore, denomdimpaths, ignore) = getdimensionpaths(objectlist, keywordlist, pivot, target, split, pathsdict)
    iotanumpaths = getiotapaths(objectlist, keywordlist, split, split, {})
    iotadenompaths = getiotapaths(objectlist, keywordlist, pivot, target, iotanumpaths)
    iotadenom = makeiota(iotadenompaths, objectlist, pivot)
    iotanum = makeiota(iotanumpaths, objectlist, split)
    z1 = assembletermforclass2and3(objectlist, keywordlist, pivot, target, denomdimpaths, [], iotadenom, split)
    z2 = assembletermforclass2and3(objectlist, keywordlist, split, split, numdimpaths, [], iotanum, None)
    z2 = align(z2, z1)
    if z2 != None:
        return makecomposition([gedeelddoor, makeproduct([z1, z2])])
    return None


"""Deprecated
def assembletermforclass5(objectlist, keywordlist, target, paths, kappa):"""
"""Build a class 5 term, which expresses an average, i.e., a numerator and
    a denominator, which are both aggregate terms for counting objects. The
    numerator counts the objects associated with the target. The code below
    first tries to find the type of objects the denominator counts (the split).
    If no split is found, None is returned. Then dimensions associated with
    the numerator and the denominator are discovered: they need not be the
    same, as even their number may differ. In short, the dimensions for the
    numerator are paths that have the target as origin and the dimensions for
    the denominator have the split as origin. To ensure both numerator and
    denominator can be put together in a product construction, a correction
    term for the denominator must be found in the general case in order to
    connect the dimensions for the numerator with those for the denominator.
    The term returned is of the form
            a(x, w) / a(y, u) o c
    where c is the correction term and the a's represent alpha (aggregation)
    terms, and where x counts target objects individually - i.e.,
    x=een(target) - and y counts split objects individually - i.e.,
    y=een(split). Selection criteria as well as kappa correction or iota
    selection may apply to both x and w, i.e., x might also be a composition
    of een(target) with a iota or kappa term, and w might also be a composition
    of dimensions with a iota or kappa term. Iota and kappa do not apply to y
    and u, i.e., selection criteria apply to the pivot only. This routine also
    serves terms that have the simple form above, without any iota or kappa
    terms.
    """
"""Deprecated
    split = None
    finals = []
    c = None
    x = een(target)
    if paths != []:
        finals = getfinals(paths)
        split = getsplit(objectlist, keywordlist, target, paths)
    if kappa != None:
        if split == None:
            split = getsplitfromkappa(objectlist, keywordlist, target, kappa)
    if split == None:
        split = getsplitfromobjectlist(objectlist, keywordlist, target)
    if split != None:
        print(kappa)
        print(split)
        y = een(split)
        if paths != []:
            (pathsl, pathsr) = splitpaths(paths, split, finals, target)
            print(pathsl, pathsr)
            pathsl = appendvariablestopaths(pathsl)
            pathsr = appendvariablestopaths(pathsr)
            c = connectdimensions(pathsl, pathsr)
            w = getdimensions(pathsl, target)
            u = getdimensions(pathsr, split)
        else:
            w = alle(target)
            u = alle(split)
        if kappa != None:
            kappasplit = splitkappa(objectlist, keywordlist, split)
            x = makecomposition([x, kappa])
            w = makecomposition([w, kappa])
            if kappasplit != None:
                y = makecomposition([y, kappasplit])
                u = makecomposition([u, kappasplit])
        z1 = makealpha([x, w])
        z2 = makealpha([y, u])
        if c != None:
            z2 = makecomposition([z2, c])
        z = makecomposition([gedeelddoor, makeproduct([z1, z2])])
        return z
    else:
        return None
"""


"""Deprecated
def assembletermforclass14(objectlist, keywordlist, target, kappa):
    split = getsplitfromkappa(objectlist, keywordlist, target, kappa)
    kappasplit = splitkappa(objectlist, keywordlist, split)
    x = een(target)
    w = alle(target)
    if kappa != None:
        x = makecomposition([x, kappa])
        w = makecomposition([w, kappa])
    y = een(split)
    u = alle(split)
    if kappasplit != None:
        y = makecomposition([y, kappasplit])
        u = makecomposition([u, kappasplit])
    z1 = makealpha([x, w])
    z2 = makealpha([y, u])
    z = makecomposition([gedeelddoor, makeproduct([z1, z2])])
    return z
"""

def test14():
    # line = 'gemiddeld aantal personen op een adres in Den Haag naar geslacht'
    # line = 'gemiddeld aantal personen op een adres naar geslacht'
    # line = 'gemiddeld aantal personen op een adres in Den Haag'
    # line = 'op een adres in Den Haag wat is het gemiddeld aantal personen?'
    # line = 'hoeveel vrouwen wonen er gemiddeld op een adres in Den Haag?'
    # line = 'gemiddeld aantal vrouwen op een adres in Den Haag'
    line = 'wat is het gemiddeld aantal banen bij bedrijven in Delft?'
    # line = 'het gemiddeld aantal banen bij bedrijven in Delft'
    # line = 'gemiddeld aantal banen van griffiers in Delft van bedrijven'
    # line = 'wat is het gemiddeld aantal banen bij bedrijven van griffiers in Delft?'
    # line = 'het gemiddeld aantal oogartsen op een adres op de Meppelerweg in Den Haag'
    # line = 'wat is het gemiddeld aantal oogartsen op een adres op de Meppelerweg in Den Haag?'
    (tokenlist, objectlist, keywordlist) = tokenize(line, lookup)
    print(line)
    z = interpret(tokenlist, objectlist, keywordlist, 5)
    if z != None:
        print(z.more())
    else:
        print('nothing')

def test13():
    # line = 'het gemiddeld inkomen van oogartsen'
    # line = 'wat is het gemiddeld inkomen van personen die oogarts zijn?'
    # line = 'het gemiddelde inkomen in Den Haag'
    # line = 'hoeveel wordt er gemiddeld verdiend in Den Haag?'
    line = 'van inwoners van Leiden het gemiddeld inkomen'
    # line = 'wat is het gemiddeld inkomen van inwoners van Leiden?'
    # line = 'wat is in Leiden het gemiddeld inkomen van oogartsen?'
    # line = 'het gemiddeld inkomen van oogartsen in Leiden'
    (tokenlist, objectlist, keywordlist) = tokenize(line, lookup)
    print(line)
    z = interpret(tokenlist, objectlist, keywordlist, 4)
    if z != None:
        print(z.more())
    else:
        print('nothing')

def test15():
    #### check the queries below ####
    line = 'het gemiddeld inkomen op de Meppelerweg in Den Haag naar adres en geslacht'
    #### not quite what was expected. Precisely what was expected. ####
    # line = 'het gemiddeld inkomen per adres naar geslacht op de Meppelerweg in Den Haag'
    # line = 'hoeveel gemiddeld wordt er verdiend per geslacht op een adres op de Meppelerweg in Den Haag?'
    # line = 'van mannen het gemiddelde inkomen naar adres'
    # line = 'wat is het gemiddelde inkomen van personen die man zijn per adres?'
    # line = 'wat is het gemiddeld salaris bij een bedrijf in de industrie per gemeente?'
    # line = 'het gemiddelde salaris bij een bedrijf in de industrie voor iedere gemeente'
    # line = 'de gemiddelde leeftijd op een adres van mannelijke oogartsen'
    # line = 'gemiddelde leeftijd per adres van mannen die oogarts zijn'
    (tokenlist, objectlist, keywordlist) = tokenize(line, lookup)
    print(line)
    z = interpret(tokenlist, objectlist, keywordlist, 4)
    if z != None:
        print(z.more())
    else:
        print('nothing')

def test1():
    # line = 'inkomen van alle personen'
    # line = 'wat is het inkomen van personen?'
    # line = 'welke adressen zijn er?'
    # line = 'alle adressen'
    # line = 'alle personen met adressen' # questionable
    # line = 'personen met adressen'
    line = 'de adressen van alle personen'
    (tokenlist, objectlist, keywordlist) = tokenize(line, lookup)
    print(line)
    z = interpret(tokenlist, objectlist, keywordlist, 1)
    if z != None:
        print(z.more())
    else:
        print('nothing')
    
def test2():
    # line = 'adressen van mannen'
    # line = 'alle adressen van personen die man zijn'
    # line = 'de adressen van griffiers'
    # line = 'wat zijn de adressen van personen die griffier zijn?'
    # line = 'alle griffiers die vrouw zijn'
    # line = 'wat zijn de vrouwelijke griffiers?'
    line = 'wat verdient een griffier?'
    # line = 'wat is het inkomen van personen die griffier zijn?'
    (tokenlist, objectlist, keywordlist) = tokenize(line, lookup)
    print(line)
    z = interpret(tokenlist, objectlist, keywordlist, 1)
    if z != None:
        print(z.more())
    else:
        print('nothing')

def test9():
    line = 'gemiddelde leeftijd op een adres per gemeente'
    # line = 'de gemiddeld leeftijd van een adres voor iedere gemeente'
    # line = 'wat is de leeftijd op een adres per gemeente gemiddeld?'
    # line = 'voor alle gemeenten en geslacht de gemiddelde leeftijd op een adres'
    # line = 'de gemiddelde leeftijd op een adres voor iedere gemeente per geslacht'
    # line = 'gemiddelde leeftijd per gemeente'
    # line = 'wat is per gemeente de leeftijd gemiddeld?'
    (tokenlist, objectlist, keywordlist) = tokenize(line, lookup)
    print(line)
    z = interpret(tokenlist, objectlist, keywordlist, 4)
    if z != None:
        print(z.more())
    else:
        print('nothing')
    
def test10():
    # line = 'hoeveel verdienen personen die oogarts zijn gemiddeld?'
    # line = 'hoeveel wordt er verdiend door mannen gemiddeld?'
    line = 'hoeveel wordt er gemiddeld door mannen verdiend?'
    # line = 'het gemiddeld salaris per bedrijf naar gemeente gevestigd'
    # line = 'wat is het gemiddelde salaris bij een bedrijf voor alle gemeenten waar zij zijn gevestigd?'
    # line = 'het gemiddeld salaris van een persoon naar woongemeente'
    # line = 'wat is naar woongemeente het gemiddelde salaris van een persoon?'
    # line = 'de gemiddelde omzet van een bedrijf per activiteit'
    # line = 'hoeveel is de omzet van een bedrijf gemiddeld per activiteit?'
    # line = 'gemiddeld inkomen op een adres naar geslacht en gemeente'
    # line = 'van alle gemeenten per geslacht het gemiddeld inkomen op een adres'
    (tokenlist, objectlist, keywordlist) = tokenize(line, lookup)
    print(line)
    z = interpret(tokenlist, objectlist, keywordlist, 4)
    if z != None:
        print(z.more())
    else:
        print('nothing')

def test6():
    # line = 'wat is het totale inkomen van personen per geslacht en gemeente?'
    # line = 'van personen naar gemeente en geslacht het totale inkomen'
    # line = 'hoeveel wordt er in totaal verdiend naar geslacht?'
    # line = 'voor ieder geslacht het totale inkomen'
    line = 'de totale omzet naar activiteit en gemeente'
    # line = 'de totale omzet van alle bedrijven naar activiteit en gemeente van vestiging'
    (tokenlist, objectlist, keywordlist) = tokenize(line, lookup)
    print(line)
    z = interpret(tokenlist, objectlist, keywordlist, 3)
    if z != None:
        print(z.more())
    else:
        print('nothing')
        
def test7():
    # line = 'in Den Haag per geslacht het totale inkomen'
    line = 'hoeveel wordt er per geslacht in Den Haag verdiend in totaal?'
    # line = 'in Leiden bij bedrijven wat is het totale salaris naar functie?'
    # line = 'in Leiden het totale salaris naar functie'
    # line = 'wat is van oogartsen hun totale inkomen naar gemeente en geslacht?'
    # line = 'per geslacht en gemeente van alle oogartsen het totale inkomen'
    (tokenlist, objectlist, keywordlist) = tokenize(line, lookup)
    print(line)
    z = interpret(tokenlist, objectlist, keywordlist, 3)
    if z != None:
        print(z.more())
    else:
        print('nothing')
        
def test8():
    # line = 'totale omzet in de bouwnijverheid'
    # line = 'de omzet van alle bedrijven in de bouwnijverheid in totaal'
    # line = 'in Den Haag op de Meppelerweg wat is het totale inkomen?'
    # line = 'wat wordt er verdiend in totaal in Den Haag op de Meppelerweg?'
    # line = 'wat is het totale inkomen van mannelijke personen?'
    line = 'hoeveel wordt er verdiend door mannen in totaal?'
    # line = 'hoeveel wordt er verdiend door mannen in totaal in Leiden?'
    # line = 'hoeveel wordt er verdiend door mannen in totaal die werken in Leiden?'
    (tokenlist, objectlist, keywordlist) = tokenize(line, lookup)
    print(line)
    z = interpret(tokenlist, objectlist, keywordlist, 3)
    if z != None:
        print(z.more())
    else:
        print('nothing')
        
def test4():
    #line = 'hoeveel mensen wonen in Leiden en werken in Rotterdam?'
    # line = 'hoeveel mensen wonen in Leiden en werken in Rotterdam per geslacht?' #### compare this with the next query.
    # line = 'hoeveel mensen wonen in Leiden en werken in Rotterdam per functie?' #### when you think about it, this is actually right.
    # line = 'aantal personen dat vrouw is en werkt in Leiden per functie?' #### other class probably - investigate. No, same reason why previous did not deliver what was (incorrectly) expected.
    # line = 'aantal personen dat vrouw is en werkt in Leiden'
    line = 'aantal vrouwen in Leiden'
    # line = 'hoeveel vrouwen werken er in Leiden?'
    # line = 'hoeveel personen werken er in Leiden?'
    # line = 'hoeveel mensen werken er?'
    # line = 'aantal personen dat werkt'
    # line = 'hoeveel vrouwelijke oogartsen werken er in het openbaar bestuur?'
    # line = 'in het openbaar bestuur hoeveel personen die oogarts zijn en vrouw werken daar?'
    # line = 'wat is het aantal oogartsen in het openbaar bestuur?'
    # line = 'hoeveel kolonellen zijn er?'
    # line = 'hoeveel personen werken er in de industrie?'
    # line = 'aantal mannen dat werkt in het openbaar bestuur'
     # line = 'in het openbaar bestuur hoeveel mensen werken daar die man zijn?'
    # line = 'hoeveel banen zijn er in de industrie?'
    (tokenlist, objectlist, keywordlist) = tokenize(line, lookup)
    print(line)
    z = interpret(tokenlist, objectlist, keywordlist, 2)
    if z != None:
        print(z.more())
    else:
        print('nothing')

def test5():
    # line = 'hoeveel personen naar geslacht zijn er in totaal?'
    # line  = 'mensen naar geslacht'
    # line = 'personen voor ieder geslacht'
    # line = 'ieder geslacht' #### what about that?
    # line = 'aantal mensen naar geslacht'
    # line = 'totaal aantal personen naar geslacht'
    # line = 'voor iedere gemeente het aantal inwoners'
    # line = 'wat is het totaal aantal inwoners per gemeente en geslacht?'
    line = 'wat is per gemeente en functie het aantal banen in totaal?'
    # line = 'totaal aantal banen naar functie naar gemeente'
    # line = 'wat is het aantal banen per functie en gemeente?'
    (tokenlist, objectlist, keywordlist) = tokenize(line, lookup)
    print(line)
    z = interpret(tokenlist, objectlist, keywordlist, 2)
    if z != None:
        print(z.more())
    else:
        print('nothing')

def test3():
    line = 'het aantal personen'
    # line = 'het totaal aantal bedrijven'
    # line = 'hoeveel adressen zijn er?'
    # line = 'wat is het aantal gemeenten'
    # line = 'hoeveel banen?'
    # line = 'het aantal mensen in totaal'
    (tokenlist, objectlist, keywordlist) = tokenize(line, lookup)
    print(line)
    z = interpret(tokenlist, objectlist, keywordlist, 2)
    if z != None:
        print(z.more())
    else:
        print('nothing')

def test12():
    # line = 'gemiddeld aantal mannen op een adres per gemeente'
    line = 'gemiddeld aantal oogartsen op een adres naar gemeente'
    # line = 'gemiddeld aantal oogartsen op een adres naar gemeente en geslacht'
    # line = 'per gemeente het aantal mannen op een adres gemiddeld'
    # line = 'wat is het gemiddeld aantal banen per gemeente van bedrijven in de industrie?'
    # line = 'hoeveel banen zijn er gemiddeld in de industrie bij een bedrijf per gemeente?'
    # line = 'het gemiddeld aantal banen als kolonel in een bedrijf naar gemeente waar het is gevestigd'
    # line = 'hoeveel banen als kolonel zijn er gemiddeld bij een bedrijf voor elke gemeente?'
    (tokenlist, objectlist, keywordlist) = tokenize(line, lookup)
    print(line)
    z = interpret(tokenlist, objectlist, keywordlist, 5)
    if z != None:
        print(z.more())
    else:
        print('nothing')

def test11():
    # what about: 'aantal bedrijven per geslacht?'
    line = 'het gemiddeld aantal banen per baan'
    # line = 'het gemiddeld aantal banen per activiteit'
    # line = 'het gemiddeld aantal banen bij een bedrijf'
    # line = 'het gemiddeld aantal banen bij een bedrijf per activiteit'
    # line = 'het gemiddeld aantal banen per gemeente en activiteit en per geslacht'
    # line = 'het gemiddeld aantal banen per gemeente'
    # line = 'het gemiddeld aantal banen per gemeente en geslacht'
    # line = 'het gemiddeld aantal banen per bedrijf per geslacht'
    # line = 'het gemiddeld aantal banen per bedrijf per geslacht in Delft'
    # line = 'het gemiddeld aantal banen per bedrijf per geslacht en activiteit'
    # line = 'het gemiddeld aantal banen per bedrijf per gemeente en activiteit'
    # line = 'het gemiddeld aantal banen bij een bedrijf per gemeente'
    # line = 'het gemiddeld aantal banen per gemeente bij een bedrijf'
    # line = 'het gemiddeld aantal banen bij een bedrijf per gemeente per geslacht'
    # line = 'het gemiddeld aantal banen per gemeente en geslacht bij een bedrijf'
    # line = 'het gemiddeld aantal banen bij een bedrijf per gemeente per geslacht per functie'
    (tokenlist, objectlist, keywordlist) = tokenize(line, lookup)
    print(line)
    z = interpret(tokenlist, objectlist, keywordlist, 5)
    if z != None:
        print(z.more())
    else:
        print('nothing')
