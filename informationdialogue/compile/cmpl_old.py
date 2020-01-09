# -*- coding: utf-8 -*-
"""
Created on Thu Aug  9 11:31:05 2018

@author: tgelsema
"""
import re
from term import *
from kind import *
from dm import gedeelddoor, getal, data
# from intrprt import een

somedomainp = Gap(name='p', kindix=0)
somecodomainq = Gap(name='q', kindix=0)
somedomainr = Gap(name='r', kindix=0)
someelementz = Gap(name='z', kindix=1, type=Application(functional_type, [somedomainp, somecodomainq]))
someelementw = Gap(name='w', kindix=1, type=Application(functional_type, [somedomainr, somecodomainq]))
someelementx = Gap(name='x', kindix=1, type=Application(functional_type, [somedomainp, getal]))
someelementy = Gap(name='y', kindix=1, type=Application(functional_type, [somedomainp, getal]))
someelementv = Gap(name='v', kindix=1, type=Application(functional_type, [somedomainr, getal]))
someaggregatex = Application(alpha, [someelementx, someelementz])
someaggregatey = Application(alpha, [someelementy, someelementz])
someaggregateu = Application(alpha, [someelementv, someelementw])
gemiddelde = Application(composition, [gedeelddoor, Application(product, [someaggregatex, someaggregatey])])
complexgemiddelde = Application(composition, [gedeelddoor, Application(product, [someaggregatex, someaggregateu])])


def cmpl(term, order):
    sql = ""
    iotas = extractiotas(term)
    kappas = extractkappas(term)
    sql += cmplfirstpass(term, iotas, kappas)
    sql += cmplsecondpass(term)
    sql += cmplthirdpass(term, order)
    return sql
    
def cmplthirdpass(term, order):
    s = ""
    selects = cmplselectsthirdpass(term)
    innerjoins = cmplinnerjoinsthirdpass(term, False)
    groupbys = cmplgroupbysthirdpass(term, False)
    orderbys = cmplorderbysthirdpass(term, order, selects)
    s += buildquery(selects, innerjoins, [], groupbys, orderbys, "", False, "")
    return s

def cmplorderbysthirdpass(term, order, selects):
    o = []
    if order != []:
        for s in selects:
            if len(s.rsplit('.', 1)) > 1:
                if s.rsplit('.', 1)[1] == order[0].name:
                    o.append(s + ' ' + order[1].upper())
            if len(s.rsplit(' AS ', 1)) > 1:
                if s.rsplit(' AS ', 1)[1] == order[0].name:
                    o.append(order[0] + ' ' + order[1].upper())
                if s.rsplit(' AS ', 1)[1] == 'gemiddeld_aantal':
                    o.append('gemiddeld_aantal' + ' ' + order[1].upper())
                if s.rsplit(' AS ', 1)[1] == 'aantal':
                    o.append('aantal' + ' ' + order[1].upper())
                if len(s.rsplit(' AS ', 1)[1].rsplit('_', 1)) > 1:
                    if s.rsplit(' AS ', 1)[1].rsplit('_', 1)[0] == 'gemiddeld':
                        o.append(s.rsplit(' AS ', 1)[1] + ' ' + order[1].upper())
                    if s.rsplit(' AS ', 1)[1].rsplit('_', 1)[0] == 'som':   
                        o.append(s.rsplit(' AS ', 1)[1] + ' ' + order[1].upper())
    return o


def cmplselectsthirdpass(term):
    return reccmplselectsthirdpass(term)

def getvarname(lst):
    if lst[0].__class__.__name__ == 'Variable':
        return lst[0].name
    return ""
    
def getalias(lst):
    i = len(lst) - 1
    if lst[i] == 'alpha':
        i = i - 1
    alias = lst[i].type.args[0].name    
    while i >= 0:
        if lst[i].__class__.__name__ == 'ObjectTypeRelation':
            alias += '_' + re.sub(' ', '_', lst[i].name)
        i = i - 1
    return alias
    
def getalpha(lst):
    if lst[len(lst) - 1] == 'alpha':
        return True
    return False
    
def getdest(lst):
    n = len(lst) - 1
    if lst[n] == 'alpha':
        n = n - 1
    if lst[n].__class__.__name__ == 'Variable' or lst[n].__class__.__name__ == 'ObjectTypeRelation':
        return lst[n].type.args[0].name

    
def cmplgroupbysthirdpass(term, t):
    global varmap
    if match(term, gemiddelde):
        return cmplgroupbysthirdpass(term.args[1], True)
    if match(term, complexgemiddelde):
        w = varmap[someelementw]
        return cmplgroupbysthirdpass(w, True)
    g = []
    lst = extractvarsnaliasesgroupbys(term, t)
    for l in lst:
        i = len(l) - 1
        alias = l[i].type.args[0].name
        if l[i].name == 'alle':
            continue
        while i >= 0:
            if l[i].__class__.__name__ == 'ObjectTypeRelation':
                alias += '_' + re.sub(' ', '_', l[i].name)
            elif l[i].__class__.__name__ == 'Variable':
                alias += '.' + re.sub(' ', '_', l[i].name)
            i = i - 1
        if not alias in g:
            g.append(alias)
    return g

def cmplinnerjoinsthirdpass(term, aggregate):
    global varmap
    if not match(term, gemiddelde) and match(term, complexgemiddelde):
        w = varmap[someelementw]
        return cmplinnerjoinsthirdpass(w, True)
    if hasalpha(term) or aggregate == True:
        jointype = 'INNER' # 'RIGHT'
    else:
        jointype = 'INNER' # so, for now, always inner; might change in the future
    j = []
    lst = extractvarsnaliases(term)
    aliases = []
    for l in lst:
        i = len(l) - 1
        if l[i] == 'alpha':
            i = i - 1
        alias = l[i].type.args[0].name
        if aliases == []:
            keep = alias
            aliases.append(alias)
            t = findtable(l[i]).name
            j.append([t, alias])
            j.append(["INNER", "tmp_%s" % keep, "tmp_%s" % keep, "tmp_%s.%s = %s.%s" % (keep, keep + '_id', keep, keep + '_id')])
        while i > 0:
            if l[i].__class__.__name__ == 'ObjectTypeRelation':
                relname = re.sub(' ', '_', l[i].name)
                newalias = alias + '_' + relname
                if not newalias in aliases:
                    aliases.append(newalias)
                    e = findtable1(l[i].codomain.name + "_id")
                    j.append([jointype, e.name, newalias, "%s.%s = %s.%s" % (newalias, e.name + '_id', alias, relname)])
                alias = newalias
            i = i - 1
    return j


def hasalpha(term):
    if term.__class__.__name__ == 'Application':
        if term.op.name == 'aggregation':
            return True
        else:
            for arg in term.args:
                if hasalpha(arg):
                    return True
    return False

def reccmplselectsthirdpass(term):
    global varmap
    if match(term, gemiddelde):
        x = varmap[someelementx]
        z = varmap[someelementz]
        varsnaliases = extractvarsnaliases(x)[0]
        t = ["IFNULL(AVG(%s.%s), 0) AS gemiddeld_%s" % (getalias(varsnaliases), getvarname(varsnaliases), getvarname(varsnaliases))]
        s = reccmplselectsthirdpass(z)
        return s + t
    elif match(term, complexgemiddelde):
        w = varmap[someelementw]
        t = ["IFNULL(AVG(tmp_%s.aantal), 0) AS gemiddeld_aantal" % getdest(extractvarsnaliases(w)[0])]
        s = reccmplselectsthirdpass(w)
        return s + t
    elif term.__class__.__name__ == 'Application':
        if term.op.name == 'product':
            s = []
            for arg in term.args:
                t = reccmplselectsthirdpass(arg)
                for attr in t:
                    if not attr in s:
                        s.append(attr)
            return s
    lst = extractvarsnaliases(term)
    s = []
    for l in lst:
        varname = getvarname(l)
        alias = getalias(l)
        alpha = getalpha(l)
        if alpha:
            if varname == 'een':
                s += ["IFNULL(COUNT(%s.%s), 0) AS aantal" % (alias, alias + '_id')]
            else:
                s += ["IFNULL(SUM(%s.%s), 0) AS som_%s" % (alias, varname, varname)]
        else:
            if varname != 'alle':
                s += ["%s.%s" % (alias, varname)]
    return s


def extractvarsnaliasesgroupbys(term, t):
    z = []
    if term.__class__.__name__ == 'Application':
        if term.op.name == 'composition':
            z = zip1alt(term.args, t)
        if term.op.name == 'product':
            z = zip2alt(term.args, t)
        if term.op.name == 'aggregation':
            z = extractvarsnaliasesgroupbys(term.args[1], True)
    elif term.__class__.__name__ == 'Variable' or term.__class__.__name__ == 'ObjectTypeRelation':
        if t == True:
            z = [[term]]
    return z


def extractvarsnaliases(term):
    z = []
    if term.__class__.__name__ == 'Application':
        if term.op.name == 'composition':
            z = zip1(term.args)
        if term.op.name == 'product':
            z = zip2(term.args)
        if term.op.name == 'aggregation':
            z = extractvarsnaliases(term.args[1])
            v = extractvarsnaliases(term.args[0])
            v[0].append('alpha')
            z += v
    elif term.__class__.__name__ == 'Variable' or term.__class__.__name__ == 'ObjectTypeRelation':
        z = [[term]]
    return z
    
    
def zip1alt(args, t):
    z = extractvarsnaliasesgroupbys(args[0], t)
    for arg in args:
        if args.index(arg) != 0:
            for l in z:
                for k in extractvarsnaliasesgroupbys(arg, t):
                    l += k
            if z == []:
                z = extractvarsnaliasesgroupbys(arg, t)
    return z    
    
def zip1(args):
    z = extractvarsnaliases(args[0])
    for arg in args:
        if args.index(arg) != 0:
            for l in z:
                for k in extractvarsnaliases(arg):
                    l += k
            if z == []:
                z = extractvarsnaliases(arg)
    return z
    
def zip2alt(args, t):
    z = []
    for arg in args:
        for k in extractvarsnaliasesgroupbys(arg, t):
            z.append(k)
    return z    
    
def zip2(args):
    z = []
    for arg in args:
        for k in extractvarsnaliases(arg):
            z.append(k)
    return z
    
def cmplsecondpass(term):
    s = ""
    global varmap
    if not match(term, gemiddelde):
        if match(term, complexgemiddelde):
            w = varmap[someelementw]
            x = varmap[someelementx]
            z = varmap[someelementz]
            selects = cmplselectssecondpass(w, z, x)
            innerjoins = cmplinnerjoinssecondpass(w, z)
            groupbys = cmplgroupbyssecondpass(selects)
            intos = cmplintossecondpass(w)
            s += buildquery(selects, innerjoins, [], groupbys, [], "", False, intos)
    return s

def cmplintossecondpass(w):
    name = w.type.args[0].name
    return "tmp_%s" % name

def cmplgroupbyssecondpass(selects):
    g = []
    g.append(selects[0])
    # g.append(selects[1])
    return g    
    
def cmplselectssecondpass(w, z, x):
    s = []
    relsconj = extractconj(w, z)
    relsdiff = extractdiff(w, z)
    alias = ''
    i = len(relsdiff) - 1
    while i >= 0:
        if alias == '':
            alias = relsdiff[i].type.args[0].name
            keep = alias
        relname = re.sub(' ', '_', relsdiff[i].name)
        alias += '_' + relname
        i = i - 1
    rel = relsconj[0]
    d = findtable(rel)
    s.append("%s.%s" % (alias, d.name + "_id"))
    # s.append("%s.%s" % (alias, re.sub(' ', '_', rel.name)))
    vrs = extractvars(x)
    var = vrs[0]
    if var.name == 'een':
        s.append("COUNT(%s.%s) AS aantal" % (keep, keep + '_id'))
    else:
        e = findtable(x)
        s.append("SUM(%s.%s) AS aantal" % (e.name, var.name))
    return s

def extractconj(w, z):
    otrsw = recextractotrs(w)
    otrsz = recextractotrs(z)
    i = 0
    while i < len(otrsw):
        if otrsw[i] != otrsz[i]:
            break
        i += 1
    return otrsz[:i]

# def compilecomplexwheres(term):
#     global varmap
#     w = []
#     if match(term, complexgemiddelde):
#         x = varmap[someelementx]
#         w = compilewheres(x)
#     return w
    
def cmplinnerjoinssecondpass(w, z):
    f = []
    aliases = []
    rels = extractdiff(w, z)
    i = len(rels) - 1
    alias = ''
    keep = ''
    while i >= 0:
        if alias == '':
            alias = rels[i].type.args[0].name
            keep = alias
            aliases.append(alias)
            f.append([findtable(rels[i]).name, alias])
            f.append(["INNER", 'tmp_' + keep, 'tmp_' + keep, "%s.%s = %s.%s" % (keep, keep + '_id', 'tmp_' + keep, keep + '_id')]) # 
        relname = re.sub(' ', '_', rels[i].name)
        newalias = alias + '_' + relname
        if not newalias in aliases:
            aliases.append(newalias)
            e = findtable1(rels[i].codomain.name + "_id")
            f.append(["RIGHT", e.name, newalias, "%s.%s = %s.%s" % (newalias, e.name + '_id', alias, relname)]) # 
        alias = newalias
        i = i - 1
    return f

def extractdiff(w, z):
    otrsw = recextractotrs(w)
    otrsz = recextractotrs(z)
    i = 0
    while i < len(otrsw):
        if otrsw[i] != otrsz[i]:
            break
        i += 1
    return otrsz[i:]
    
def recextractotrs(z):
    if z.__class__.__name__ == 'ObjectTypeRelation':
        return [z]
    if z.__class__.__name__ == 'Application':
        if z.op.name == 'iota' or z.op.name == 'inverse':
            return []
        if z.op.name == 'composition':
            otrs = []
            for arg in z.args:
                otrs += recextractotrs(arg)
            return otrs
    return []


def cmplfirstpass(term, iotas, kappas):
    if kappas != None:
        distinct = True
    else:
        distinct = False
    selects = cmplselectsfirstpass(term, iotas, kappas)
    (t, innerjoins) = cmplinnerjoinsfirstpass(term, iotas, kappas)
    intos = "tmp_" + t
    wheres = cmplwheresfirstpass(iotas)
    return buildquery(selects, innerjoins, wheres, [], [], "", distinct, intos)


def cmplselectsfirstpass(term, iotas, kappas):
    if iotas != []:
        alias = iotas[0].type.args[0].name
    else:
        vrs = extractvarsnaliases(term)
        if vrs != []:
            alias = findtable1(vrs[0][len(vrs[0]) - 1].domain.name + '_id').name
    attr = ""
    if kappas != None:
        rel = extractotherrels(kappas)
        if rel.__class__.__name__ == 'Application':
            i = len(rel.args) - 1
            alias = re.sub(' ', '_', rel.args[i].type.args[0].name)
            while i >= 0:
                alias += "_" + args[i].name
        elif rel.__class__.__name__ == 'ObjectTypeRelation':
            alias = rel.type.args[0].name + '_' + re.sub(' ', '_', rel.name)
        attr = kappas.type.args[1].name + "_id"
    else:
        attr = alias + "_id"
    return [alias + "." + attr]


def cmplinnerjoinsfirstpass(term, iotas, kappas):
    f = []
    if iotas != []:
        t = iotas[0].type.args[0].name
    aliases = []    
    rels = extractrels(iotas)
    if kappas != None:
        e = extractotherrels(kappas)
        rels.append(e)
        t = e.type.args[1].name
    for rel in rels:
        if rel.__class__.__name__ == 'Application':
            if rel.op.name == 'composition':
                i = len(rel.args) - 1
                alias = rel.type.args[0].name
                if aliases == []:
                    aliases.append(alias)
                    d = findtable(rel.args[i]).name
                    f.append([d, alias])
                while i > 0:
                    if rel.args[i].__class__.__name__ == 'ObjectTypeRelation':
                        relname = re.sub(' ', '_', rel.args[i].name)
                        newalias = alias + '_' + relname
                        if not newalias in aliases:
                            aliases.append(newalias)
                            e = findtable1(rel.args[i].codomain.name + "_id")
                            f.append(["INNER", e.name, newalias, "%s.%s = %s.%s" % (newalias, e.name + '_id', alias, relname)])
                        alias = newalias
                    i = i - 1
        elif rel.__class__.__name__ == 'ObjectTypeRelation':
            relname = re.sub(' ', '_', rel.name)
            alias = rel.type.args[0].name
            if aliases == []:
                aliases.append(alias)
                d = findtable(rel).name
                f.append([d, alias])
            newalias = alias + '_' + relname
            if not newalias in aliases:
                aliases.append(newalias)
                e = findtable1(rel.codomain.name + "_id")
                f.append(["INNER", e.name, newalias, "%s.%s = %s.%s" % (newalias, e.name + '_id', alias, relname)])
    if f == []:
        vrs = extractvarsnaliases(term)
        if vrs != []:
            t = findtable1(vrs[0][len(vrs[0]) - 1].domain.name + '_id').name
            f = [[t, t]]
    return (t, f)


def cmplwheresfirstpass(iotas):
    w = []
    for i in range(0, len(iotas) // 2):
        var = extractvars(iotas[i * 2])[0]
        alias = getalias1(iotas[i * 2])
        c = iotas[i * 2 + 1].args[0]
        w.append("%s.%s = '%s'" % (alias, re.sub(' ', '_', var.name), c.name))
    return w
    
    
def getalias1(iota):
    alias = iota.type.args[0].name
    if iota.__class__.__name__ == 'Application':
        i = len(iota.args) - 1
        while i >= 0:
            if iota.args[i].__class__.__name__ == 'ObjectTypeRelation':
                alias += '_' + re.sub(' ', '_', iota.args[i].name)
            i = i -1
    return alias


def extractotherrels(kappas):
    if kappas != None:
        if kappas.args[0].__class__.__name__ == 'Application':
            if kappas.args[0].op.name == 'composition':
                newargs = []
                for arg in kappas.args[0].args:
                    if arg.__class__.__name__ == 'ObjectTypeRelation':
                        newargs.append(arg)
                if len(newargs) == 0:
                    return None
                if len(newargs) == 1:
                    return newargs[0]
                else:
                    return Application(composition, newargs)
        else:
            return kappas.args[0]
    return None
            
def extractrels(iotas):
    rels = []
    for i in range(0, len(iotas)):
        if i % 2 == 0:
            rels.append(iotas[i])
    return rels
        
def extractkappas(term):
    if term.__class__.__name__ == 'Application':
        if term.op.name == 'inverse':
            return term
        else:
            for arg in term.args:
                if extractkappas(arg) != None:
                    return extractkappas(arg)
    return None

def order(otrs):
    source = otrs
    ordotrs = []
    while source != []:
        pivot = source[0]
        for otr in source:
            if otr.codomain == pivot.domain:
                pivot = otr
        ordotrs.append(pivot)
        source.remove(pivot)
    return ordotrs
    
def extractvars(term):
    if term.__class__.__name__ == 'Application':
        vrs = []
        for arg in term.args:
            vrsrec = extractvars(arg)
            for v in vrsrec:
                if not v in vrs:
                    vrs.append(v)
        return vrs
    if term.__class__.__name__ == 'Variable':
        return [term]
    return []   

def extractiotas(term):
    if term.__class__.__name__ == 'Application':
        if term.op.name == 'inclusion':
            return term.args
        else:
            iotas = []
            for arg in term.args:
                iotasrec = extractiotas(arg)
                for i in range(0, len(iotasrec) // 2):
                    if not iotasrec[i * 2] in iotas:
                        iotas.append(iotasrec[i * 2])
                        iotas.append(iotasrec[i * 2 + 1])
            return iotas
    return []

def extractotrs(term):
    if term.__class__.__name__ == 'Application':
        otrs = []
        for arg in term.args:
            for otr in extractotrs(arg):
                if not otr in otrs:
                    otrs.append(otr)
        return otrs
    elif term.__class__.__name__ == 'ObjectTypeRelation':
        return [term]
    return []

def findtable1(s):
    for d in data:
        if foundsome1(s, d.constr):
            return d
    return None
    
def foundsome1(s, term):
    if term.__class__.__name__ == 'Application':
        for arg in term.args:
            if foundsome1(s, arg):
                return True
    if term.__class__.__name__ == 'Variable':
        if term.name == s:
            return True
    return False
    
def findtable(term):
    for d in data:
        if foundsome(term, d.constr):
            return d
        if term.__class__.__name__ == 'Variable' and term.name == 'een' or term.name == 'alle':
            if term.domain.name == d.name:
                return d
    return None
        
def foundsome(subterm, term):
    if term.__class__.__name__ == 'Application':
        for arg in term.args:
            if foundsome(subterm, arg):
                return True
    if term.__class__.__name__ == 'Variable' or term.__class__.__name__ == "Constant" or term.__class__.__name__ == "ObjectTypeRelation":
        if term.name == re.sub(' ', '_', subterm.name):
            return True
        if term.name == subterm.name:
            return True
    return False
    
def buildquery(selects, innerjoins, wheres, groupbys, orderbys, alias, distinct, intos):
    sql = ""
    if intos != '':
        sql += """CREATE TEMPORARY TABLE %s\n""" % intos
    if alias != "":
        sql += """(SELECT """
    else:
        sql += """SELECT """
    if distinct:
        sql += """DISTINCT """
    for s in selects:
        if selects.index(s) + 1 == len(selects):
            sql += s + '\n'
        else:
            sql += s + ', '
    sql += """FROM """ + innerjoins[0][0] + ' AS ' + innerjoins[0][1] + '\n'
    for i in innerjoins:
        if innerjoins.index(i) != 0:
            sql += i[0] + """ JOIN """ + i[1] + """ AS """ + i[2] + """ ON ("""
            for j in i:
                if i.index(j) != 0 and i.index(j) != 1 and i.index(j) != 2:
                    if i.index(j) + 1 == len(i):
                        sql += j + ')' + '\n'
                    else:
                        sql += j + ' AND '
    if len(wheres) > 0:
        sql += """WHERE ("""
        for w in wheres:
            if wheres.index(w) + 1 == len(wheres):
                sql += w + ')' + '\n'
            else:
                sql += w + ' AND '
    if len(groupbys) > 0:
        sql += """GROUP BY """        
        for g in groupbys:
            if groupbys.index(g) + 1 == len(groupbys):
                sql += g + '\n'
            else:
                sql += g + ', '
    if alias != "":
        sql += ') AS %s \n' % alias
    if len(orderbys) > 0:
        sql += """ORDER BY """ + orderbys[0] + '\n'
        sql += """LIMIT 5""" + '\n'
    return sql + '\n'

    
def match(cterm, oterm):
    global varmap
    varmap = {}
    return recmatch(cterm, oterm)
    
def recmatch(cterm, oterm):
    global varmap
    if cterm.__class__.__name__ == 'Application':
        return matchapplication(cterm, oterm)
    else:
        return matchkind(cterm, oterm)
        
def matchapplication(cterm, oterm):
    global varmap
    if oterm.__class__.__name__ == 'Gap':
        if oterm in varmap.keys():
            if varmap[oterm].equals(cterm):
                return True
        else:
            varmap[oterm] = cterm
            return True
    if oterm.__class__.__name__ == 'Application':
        if cterm.__class__.__name__ == 'Application' and cterm.op == oterm.op:
            if len(cterm.args) == len(oterm.args):
                for i in range(len(oterm.args)):
                    if not recmatch(cterm.args[i], oterm.args[i]):
                        return False
                return True
    return False
                    
def matchkind(cterm, oterm):
    global varmap
    if cterm.__class__.__name__ == oterm.__class__.__name__: # both are kinds
        if cterm.equals(oterm):
            return True
    elif oterm.__class__.__name__ == 'Gap':
        if oterm in varmap.keys():
            if varmap[oterm].equals(cterm):
                return True
        else:
            varmap[oterm] = cterm
            return True
    return False

if __name__ == '__main__':
    global varmap
    # cterm = Application(product, [leeftijd, inkomen])
    # p = Gap(name = 'p', kindix = 0)
    # q = Gap(name = 'q', kindix = 0)
    # x = Gap(name = 'x', kindix = 1, type = Application(functional_type, [p, q]))
    # y = Gap(name = 'y', kindix = 1, type = Application(functional_type, [p, q]))
    # oterm = Application(product, [x, y])
    # print(match(cterm, oterm))
    # print(varmap)
    # oterm = Application(product, [x, x])
    # print(match(cterm, oterm))
    # print(varmap)
    # dims = Application(composition, [gemeentenaam, ligtin, woontop])
    # sums = Application(alpha, [leeftijd, dims])
    # counts = Application(alpha, [een(persoon), dims])
    # term = Application(composition, [gedeelddoor, Application(product, [sums, counts])])
    # print(match(term, gemiddelde))
    # print(varmap)
    