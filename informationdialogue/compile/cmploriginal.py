# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 10:40:06 2018

@author: tgelsema
"""
import re
from term import *
from kind import *
from dm import data

class Compilestruct:
    def __init__(self, what, table, domcols, codcols, sql):
        self.what = what
        self.table = table
        self.domcols = domcols
        self.codcols = codcols
        self.sql = sql

def cmp(term, args):
    global beenthere
    global k
    beenthere = {}
    k = 0
    return compile(term, args)

def compile(term, args):
    if term.more() in beenthere.keys():
        what = beenthere[term.more()].what
        table = beenthere[term.more()].table
        domcols = beenthere[term.more()].domcols
        codcols = beenthere[term.more()].codcols
        return Compilestruct(what, table, domcols, codcols, "")
    else:
        c = None
        if term.__class__.__name__ == 'Application':
            if term.op.name == 'product':
                c = compileproduct(term.args)
            if term.op.name == 'inclusion':
                c = compileinclusion(term.args)
            if term.op.name == 'composition':
                c = compilecomposition(term.args)
            if term.op.name == 'aggregation':
                c = compilealpha(term.args)
        if term.__class__.__name__ == 'Gap':
            print('we should never get here')
        if term.__class__.__name__ == 'Variable':
            c = compilevariable(term)
        if term.__class__.__name__ == 'ObjectTypeRelation':
            c = compileobjecttyperelation(term)
        if term.__class__.__name__ == 'Constant':
            c = compileconstant(term)
        if term.__class__.__name__ == 'Operator':
            c = compileoperator(term, args)
        if not term.more() in beenthere.keys():
            beenthere[term.more()] = c
        return c
    return None
    
def compileproduct(args):
    global k
    structs = []
    domcols = []
    codcols = []
    sql = ""
    k += 1
    l = k
    n = 0
    for arg in args:
        struct = compile(arg, [])
        structs.append(struct)
    sqlprd = """CREATE TEMPORARY TABLE tmp%s
SELECT """ % l
    for col in structs[0].domcols:
        sqlprd += structs[0].table + "." + col + " AS col%s, " % n
        domcols.append("col%s" % n)
        n += 1
    for struct in structs:
        for col in struct.codcols:
            if structs.index(struct) + 1 == len(structs) and struct.codcols.index(col) + 1 == len(struct.codcols):
                sqlprd += struct.table + "." + col + " AS col%s" % n
            else:
                sqlprd += struct.table + "." + col + " AS col%s, " % n
            codcols.append("col%s" % n)
            n += 1
    sqlprd += """
FROM %s""" % structs[0].table
    for i in range(1, len(structs)):
        sqlprd += """
INNER JOIN %s ON (""" % structs[i].table
        for j in range(0, len(structs[i].domcols)):
            if j + 1 == len(structs[i].domcols):
                sqlprd += "%s.%s = %s.%s)" % (structs[i].table, structs[i].domcols[j], structs[0].table, structs[0].domcols[j])
            else:
                sqlprd += "%s.%s = %s.%s AND " % (structs[i].table, structs[i].domcols[j], structs[0].table, structs[0].domcols[j])
    sqlprd += "\n"
    for struct in structs:
        sql += struct.sql + "\n"
    sql += sqlprd
    return Compilestruct("product", "tmp%s" % l, domcols, codcols, sql)
        
    
def compileinclusion(args):
    global k
    structs = [] # assumption: every codcols list has only one member
    domcols = []
    codcols = []
    sql = ""
    k += 1
    l = k
    n = 0
    for arg in args:
        struct = compile(arg, [])
        structs.append(struct)
    sqlincl = """CREATE TEMPORARY TABLE tmp%s
SELECT """ % l
    for j in range(0, len(structs[0].domcols)):
        sqlincl += structs[0].table + "." + structs[0].domcols[j] + " AS col%s, " % n
        domcols.append("col%s" % n)
        n += 1
    for j in range(0, len(structs[0].domcols)):
        if j + 1 == len(structs[0].domcols):
            sqlincl += structs[0].table + "." + structs[0].domcols[j] + " AS col%s" % n
        else:
            sqlincl += structs[0].table + "." + structs[0].domcols[j] + " AS col%s, " % n
        codcols.append("col%s" % n)
        n += 1
    sqlincl += """
FROM %s""" % structs[0].table
    for i in range(1, len(structs)):
        sqlincl += """
INNER JOIN %s ON (""" % structs[i].table
        for j in range(0, len(structs[i].domcols)):
            if j + 1 == len(structs[i].domcols): # and i + 1 == len(structs):                    
                sqlincl += "%s.%s = %s.%s)" % (structs[i].table, structs[i].domcols[j], structs[0].table, structs[0].domcols[0])
            else:
                sqlincl += "%s.%s = %s.%s AND " % (structs[i].table, structs[i].domcols[j], structs[0].table, structs[0].domcols[0])
    sqlincl += """
WHERE """
    for i in range(0, len(structs)):
        if i % 2 == 0:
            if i + 2 == len(structs):
                sqlincl += """%s.%s = %s.%s""" % (structs[i].table, structs[i].codcols[0], structs[i + 1].table, structs[i + 1].codcols[0])
            else:
                sqlincl += "%s.%s = %s.%s AND " % (structs[i].table, structs[i].codcols[0], structs[i + 1].table, structs[i + 1].codcols[0])
    sqlincl += "\n"
    for struct in structs:
        sql += struct.sql + "\n"
    sql += sqlincl
    return Compilestruct("inclusion", "tmp%s" % l, domcols, codcols, sql)
    
    
def compilecomposition(args):
    global k
    structs = []
    domcols = []
    codcols = []
    sql = ""
    k += 1
    l = k
    n = 0
    for arg in args:
        if arg.sort != "operator":
            struct = compile(arg, [])
            structs.append(struct)
    if args[0].sort == "operator":
        structs.insert(0, compile(args[0], [structs[0].table + "." + structs[0].codcols[0], structs[0].table + "." + structs[0].codcols[1]]))
        n += 1 # reserved col0 for the result of operator
        codcols.append("col0")
    sqlcomp = """CREATE TEMPORARY TABLE tmp%s
SELECT """ % l
    for col in structs[len(structs) - 1].domcols:
        sqlcomp += structs[len(structs) - 1].table + "." + col + " AS col%s, " % n
        domcols.append("col%s" % n)
        n += 1
    if structs[0].what == "operator":
        sqlcomp += structs[0].sql
    else:
        for col in structs[0].codcols:
            if structs[0].codcols.index(col) + 1 == len(structs[0].codcols):
                sqlcomp += structs[0].table + "." + col + " AS col%s" % n
            else:
                sqlcomp += structs[0].table + "." + col + " AS col%s, " % n
            codcols.append("col%s" % n)
            n += 1
    if structs[0].what == "operator":
        m = 1 # skip first table since it does not exist
    else:
        m = 0
    sqlcomp += """
FROM %s""" % structs[m].table
    for i in range(m + 1, len(structs)):
        sqlcomp += """
INNER JOIN %s ON (""" % structs[i].table
        for j in range(0, len(structs[i].domcols)):
            if j + 1 == len(structs[i].domcols):
                sqlcomp += """%s.%s = %s.%s)""" % (structs[i].table, structs[i].codcols[j], structs[i - 1].table, structs[i - 1].domcols[j])
            else:
                sqlcomp += "%s.%s = %s.%s AND " % (structs[i].table, structs[i].codcols[j], structs[i - 1].table, structs[i - 1].domcols[j])
    sqlcomp += "\n"
    for struct in structs:
        if struct.what != "operator":
            sql += struct.sql + "\n"
    sql += sqlcomp
    return Compilestruct("composition", "tmp%s" % l, domcols, codcols, sql)
                
    
def compilealpha(args):
    global k
    structs = [] # we know that len(structs) is exactly two
    domcols = []
    codcols = []
    sql = ""
    k += 1
    l = k
    n = 0
    for arg in args:
        struct = compile(arg, [])
        structs.append(struct)
    sqlalpha = """CREATE TEMPORARY TABLE tmp%s
SELECT """ % l
    for col in structs[1].codcols:
        sqlalpha += structs[1].table + "." + col + " AS col%s, " % n
        domcols.append("col%s" % n)
        n += 1
    for col in structs[0].codcols:
        if structs[0].codcols.index(col) + 1 == len(structs[0].codcols):
            sqlalpha += "SUM(" + structs[0].table + "." + col + ") AS col%s" % n
        else:
            sqlalpha += "SUM(" + structs[0].table + "." + col + ") AS col%s, " % n
        codcols.append("col%s" % n)
        n += 1
    sqlalpha += """
FROM %s""" % structs[0].table
    sqlalpha += """
INNER JOIN %s ON (""" % structs[1].table
    for j in range(0, len(structs[0].domcols)):
        if j + 1 == len(structs[0].domcols):
            sqlalpha += "%s.%s = %s.%s)" % (structs[0].table, structs[0].domcols[j], structs[1].table, structs[1].domcols[j])
        else:
            sqlalpha += "%s.%s = %s.%s AND " % (structs[0].table, structs[0].domcols[j], structs[1].table, structs[1].domcols[j])
    sqlalpha += """
GROUP BY """
    for col in domcols:
        if domcols.index(col) + 1 == len(domcols):
            sqlalpha += col
        else:
            sqlalpha += col + ", "
    sqlalpha += "\n"
    for struct in structs:
        sql += struct.sql + "\n"
    sql += sqlalpha
    return Compilestruct("alpha", "tmp%s" % l, domcols, codcols, sql)
    
    
def compilevariable(var):
    global k
    if var.name == 'een':
        return compileeen(var)
    if var.name == 'alle':
        return compilealle(var)
    k += 1
    l = k
    table = findtable(var)
    sqlvar = """CREATE TEMPORARY TABLE tmp%s
SELECT %s_id AS col0, %s AS col1
FROM %s
""" % (l, table, var.name, table)
    return Compilestruct("variable", "tmp%s" % l, ["col0"], ["col1"], sqlvar)
   
   
def compileeen(var):
    global k
    k += 1
    l = k
    table = var.domain.name
    sqleen = """CREATE TEMPORARY TABLE tmp%s
SELECT %s_id AS col0, 1 AS col1
FROM %s
""" % (l, table, table)
    return Compilestruct("een", "tmp%s" % l, ["col0"], ["col1"], sqleen)
    
def compilealle(var):
    global k
    k += 1
    l = k
    table = var.domain.name
    sqlalle = """CREATE TEMPORARY TABLE tmp%s
SELECT %s_id AS col0, '*' AS col1
FROM %s
""" % (l, table, table)
    return Compilestruct("alle", "tmp%s" % l, ["col0"], ["col1"], sqlalle)

def findtable(term):
    for d in data:
        if foundsome(term, d.constr):
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
    return False
    
def compileobjecttyperelation(otr):
    global k
    k += 1
    l = k
    table = findtable(otr)
    name = re.sub(' ', '_', otr.name)
    sqlotr = """CREATE TEMPORARY TABLE tmp%s
SELECT %s_id AS col0, %s AS col1
FROM %s
""" % (l, table, name, table)
    return Compilestruct("object type relation", "tmp%s" % l, ["col0"], ["col1"], sqlotr)
    
def compileconstant(const):
    global k
    k += 1
    l = k
    sqlconst = """CREATE TEMPORARY TABLE tmp%s
SELECT '*' AS col0, '%s' AS col1
""" % (l, const.name)
    return Compilestruct("constant", "tmp%s" % l, ["col0"], ["col1"], sqlconst)
    
def compileoperator(oper, args):
    sqloper = ""
    if oper.name == "(/)":
        sqloper = "(%s / %s) AS col0" % (args[0], args[1])
    return Compilestruct("operator", None, [args[0], args[1]], [], sqloper)
    
    
    

    