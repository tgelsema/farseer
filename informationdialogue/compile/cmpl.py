#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 07:55:59 2019

@author: tgelsema
@author: Guido van den Heuvel
"""
import re
from copy import copy, deepcopy

from informationdialogue.term.trm import Application, composition, product, inclusion, inverse, alpha, projection
from informationdialogue.kind.knd import Variable, ObjectTypeRelation, Constant, Operator
from informationdialogue.domainmodel.dm import data, one

# global variable
table_num = 0

# Two constants that determine how aggressive query optimization is

# If FREEZE_ALL is True, all intermediate queries are frozen. This means
# that a new temporary table is generated for each operation.
# If FREEZE_ALL is False, queries remain unfrozen as long as is feasible.
# This tends to lead to fewer queries and therefore, likely faster execution. 
# Currently all aggregation subqueries are frozen, and all others aren't.
FREEZE_ALL = False    

# If DEDUP_FROZEN is False, frozen queries are not deduplicated. Duplicate
# frozen queries arise naturally when the same sub-expression is present
# multiple times.
# If DEDUP_FROZEN is True, identical frozen queries are deduplicated, which
# leads to faster execution times.
DEDUP_FROZEN = True

class Name:
    def __init__(self, name):
        self.name = f"{name}"

    def __bool__(self):
        return bool(repr(self))

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return self.name


class Alias:
    def __init__(self, alias):
        self.alias = Name(alias)
        
    def __repr__(self):
        return f" AS {self.alias}" if self.alias else ""


class TableAlias(Alias):
    def __init__(self, table, alias = ""):
        self.table = Name(table)
        Alias.__init__(self, alias)

    def get_alias(self):
        return repr(self.alias) if self.alias else repr(self.table)

    def replace_alias(self, table, alias):
        self.alias = Name(repr(self.alias).replace(repr(table), repr(alias), 1))

    def substitute_table(self, old, new):
        if self.table == old:
            self.table = new

    def __repr__(self):
        if not self.alias or repr(self.table) == repr(self.alias):
            return repr(self.table)
        return f"{self.table}" + Alias.__repr__(self) if self.table else ""
    

class Column:
    def __init__(self, table, column):
        self.table = Name(table)
        self.column = Name(column)

    def replace_table(self, table, alias):
        self.table = Name(repr(self.table).replace(repr(table), repr(alias), 1))

    def substitute_table(self, old, new):
        if self.table == old:
            self.table = new

    def __eq__(self, other):
        return repr(self) == repr(other)

    def __repr__(self):
        return f"{self.table}.{self.column}" if self.table else f"{self.column}"


class ColumnAlias(Column, Alias):
    def __init__(self, table, column, alias):
        Column.__init__(self, table, column)
        Alias.__init__(self, alias)

    def get_column(self):
        return Column(self.table, self.column)

    def __repr__(self):
        return Column.__repr__(self) + Alias.__repr__(self)


class ExpressionAlias(Alias):
    def __init__(self, args, alias = "", prefix = "", infix = ", "):
        super().__init__(alias)
        self.args = args
        self.prefix = prefix
        self.infix = infix

    def __repr__(self):
        if len(self.args) == 0:
            result = ""
        elif len(self.args) == 1 and self.prefix == "":
            result = repr(self.args[0]) + super().__repr__()
        else:
            argstr = self.infix.join([ repr(a) for a in self.args ])
            result = self.prefix + "(" + argstr + ")" + super().__repr__()
        return result

    def substitute_table(self, old, new):
        for arg in self.args:
            arg.substitute_table(old, new)


class Cond:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        
    def replace_tables(self, table, alias):
        self.lhs.replace_table(table, alias)
        self.rhs.replace_table(table, alias)

    def substitute_table(self, old, new):
        self.lhs.substitute_table(old, new)
        self.rhs.substitute_table(old, new)

    def __repr__(self):
        return f'({self.lhs} = {self.rhs})'


class CondAlias(Cond, TableAlias):
    def __init__(self, table, alias, lhs, rhs):
        TableAlias.__init__(self, table, alias)
        Cond.__init__(self, lhs, rhs)

    def replace_alias(self, table, alias):
        Cond.replace_tables(self, table, alias)
        TableAlias.replace_alias(self, table, alias)

    def substitute_table(self, old, new):
        Cond.substitute_table(self, old, new)
        TableAlias.substitute_table(self, old, new)

    def __repr__(self):
        return f'({TableAlias.__repr__(self)}) ON {Cond.__repr__(self)}'

class QStruct:    
    def __init__(self, selectsdom, selectscod, frm, joins = None, wheres = None, groupbys = None, frozen_qsts = None, distinct = None, orderby = None, orderdir = ""):
        joins = [] if joins is None else joins
        wheres = [] if wheres is None else wheres
        groupbys = [] if groupbys is None else groupbys
        frozen_qsts = [] if frozen_qsts is None else frozen_qsts    
        distinct = False if distinct is None else distinct

        self.frozen_qsts = frozen_qsts
        self.selectsdom = selectsdom
        self.selectscod = selectscod
        self.frm = frm
        self.joins = []
        for j in joins:
            self.add_join(j)
        self.wheres = []
        for w in wheres:
            self.add_where(w)
        self.groupbys = groupbys
        self.distinct = distinct
        self.orderby = orderby
        self.orderdir = orderdir
        
    def add_join(self, new_join):
        for join in self.joins:
            if join.table == new_join.table and join.lhs.column == new_join.lhs.column and repr(join.rhs) == repr(new_join.rhs):
                break
            if repr(join) == repr(new_join):            # Code for new join already in existing joins
                break                                   # therefore the new join can be omitted
        else:
            self.joins.append(new_join)

    def add_where(self, new_where):
        for where in self.wheres:
            if repr(where) == repr(new_where):
                break
        else:
            self.wheres.append(new_where)

    def freeze(self):
        global table_num

        tablename = f"tmp{table_num}"
        table_num += 1

        frozen_qst = copy(self)
        frozen_qst.tablename = Name(tablename)
        column_num = 0
        for s in frozen_qst.selectsdom + frozen_qst.selectscod:
            if not s.alias:
                s.alias = Name(f"col{column_num}")
            column_num += 1
        frozen_qst.frozen_qsts = []
        frozen_qst.orderby = None
        frozen_qst.orderdir = ""

        self.frozen_qsts.append(frozen_qst)
        self.frm = TableAlias(tablename)
        self.selectsdom = [ ColumnAlias(tablename, s.alias, "") for s in frozen_qst.selectsdom ]
        self.selectscod = [ ColumnAlias(tablename, s.alias, "") for s in frozen_qst.selectscod ]
        self.joins = []
        self.wheres = []
        self.groupbys = []
        
        return self

    def substitute_table(self, old_table, new_table):
        for s in self.selectsdom + self.selectscod:
            s.substitute_table(old_table, new_table)
        if self.frm.table == old_table:
            self.frm.table = new_table
        old_joins = self.joins
        self.joins = []
        for j in old_joins:
            if j.table == old_table:
                j.table = new_table
            if j.lhs.table == old_table:
                j.lhs.table = new_table
            if j.rhs.table == old_table:
                j.rhs.table = new_table
            add_join = True
            for j2 in self.joins:
                if j.table == j2.table and j.lhs.column == j2.lhs.column and repr(j.rhs) == repr(j2.rhs):
                    add_join = False
                    break
            if add_join and repr(j.lhs) != repr(j.rhs):
                self.joins.append(j)
        for w in self.wheres:
            if w.lhs.table == old_table:
                w.lhs.table = new_table
            if w.rhs.table == old_table:
                w.rhs.table = new_table
        if isinstance(self.groupbys, list):
            for g in self.groupbys:
                if g.table == old_table:
                    g.table = new_table
            
    def dedup_frozen(self):
        if not DEDUP_FROZEN:
            return self

        old_qsts = self.frozen_qsts
        self.frozen_qsts = []
        queries = []
        for i, qst in enumerate(old_qsts):
            query = repr(qst)
            try:
                j = queries.index(query)
            except ValueError:        
                # Query is not on the list of queries yet, therefore we must keep it
                queries.append(query)
                self.frozen_qsts.append(qst)
                continue

            # Query is the same as some other one already in the list of queries. We therefore
            # don't need this query. We go through the remaining queries to rename all instances
            # of the new query's tablename to the existing query's one.
            cur_table = qst.tablename
            rep_table = old_qsts[j].tablename

            for qst in old_qsts[i+1:]:
                qst.substitute_table(cur_table, rep_table)
            self.substitute_table(cur_table, rep_table)
        return self


    def __repr__(self):
        sql = ""
        for frozen_qst in self.frozen_qsts:
            sql += f"CREATE TEMPORARY TABLE {frozen_qst.tablename}\n{frozen_qst}"

        colspec = ""
        for alias in self.selectsdom + self.selectscod:
            if colspec:
                colspec += ", "
            colspec += repr(alias)
        joinstr = ""
        for join in self.joins:
            joinstr += f"\nJOIN {join}"
        fromstr = f"\nFROM {self.frm}" if repr(self.frm) else ""
        wherestr = ""
        for where in self.wheres:
            wherestr += f" AND {where}" if wherestr else f"\nWHERE {where}"
        groupbystr = ""
        if isinstance(self.groupbys, list):
            for groupby in self.groupbys:
                groupbystr += f", {groupby}" if groupbystr else f"\nGROUP BY {groupby}"
        orderbystr = ""
        if self.orderby is not None:
            orderdir = "DESC" if self.orderdir == "desc" else "ASC"
            orderbystr = f"\nORDER BY {self.orderby} {orderdir} LIMIT 5"
        distinctstr = "DISTINCT " if self.distinct else ""

        sql += f"SELECT {distinctstr}{colspec}{fromstr}{joinstr}{wherestr}{groupbystr}{orderbystr}\n"

        return sql

class QOperator:
    def __init__(self, prefix = "", infix = ""):
        self.prefix = prefix
        self.infix = infix

""" class QProjection:
    contains the data necessary for the projection operator. Projection selects one of the 
    dimensions of the co-domain of a term with a multi-dimensional co-domain.
    Since the dimension provided by the projection operator is 1-based, while Python is
    zero-based, we convert the dimension to zero-based here."""
class QProjection:
    def __init__(self, dimensions):
        self.dimensions = dimensions

def freeze_qsts(qsts):

    for qst in qsts:
        if isinstance(qst, QStruct) and (FREEZE_ALL or qst.groupbys or qst.distinct):
            qst.freeze()

def cmpl(term, var = None, order = ""):
    global table_num

    table_num = 0
    return do_cmpl(term, var, order).dedup_frozen()

def do_cmpl(term, var, order):
    if isinstance(term, Application):
        if term.op == composition:
            return cmplcomposition(term.args, var, order)
        elif term.op == product:
            return cmplproduct(term.args, var, order)
        elif term.op == inclusion:
            return cmplinclusion(term.args, var, order)
        elif term.op == inverse:
            return cmplinverse(term.args, var, order)
        elif term.op == alpha:
            return cmplaggregation(term.args, var, order)
        elif term.op == projection:
            return cmplprojection(term.args, var, order)
    elif isinstance(term, Variable):
        return cmplvariable(term, var, order)
    elif isinstance(term, ObjectTypeRelation):
        return cmplobjecttyperelation(term, var, order)
    elif isinstance(term, Constant):
        return cmplconstant(term, var, order)
    elif isinstance(term, Operator):
        return cmploperator(term, var, order)

def cmplcomposition(args, var, order):
    qsts = []
    for arg in args:
        qsts.append(do_cmpl(arg, var, order))

    freeze_qsts(qsts)

    return do_composition(qsts, var, order)

def do_composition(qsts, var, order):
    if len(qsts) == 1:
        return qsts[0]

    rhs = qsts.pop()
    lhs = qsts.pop()

    if isinstance(rhs, QProjection):
        # Ignore projection operator on the right hand side
        # It works solely on the domain of the entire expression so can be ignored
        # Either that domain is more complex than it needs to be, or some other part
        # of the expression has the entire domain.
        qsts.append(lhs)
        return do_composition(qsts, var, order)

    selectsdom = rhs.selectsdom
    frm = rhs.frm
    joins = rhs.joins
    wheres = rhs.wheres
    orderby = rhs.orderby
    orderdir = rhs.orderdir

    if isinstance(lhs, QOperator):
        alias = ""
        args = deepcopy(rhs.selectscod) # We can assume args is a two-item list
        if orderby is not None:
            if args[0].column == Name("key") or args[0].alias == Name("key"):
                alias = Name("key")
                args[0].alias = ""
            elif args[1].column == Name("key") or args[1].alias == Name("key"):
                alias = Name("key")
                args[1].alias = ""
                orderdir = "desc" if orderdir == "asc" else "desc"
        selectscod = [ ExpressionAlias(args, alias = alias, prefix = lhs.prefix, infix = lhs.infix) ]
        frozen_qsts = [ f for q in [ rhs ] for f in q.frozen_qsts ]
    elif isinstance(lhs, QProjection):
        selectscod = [ rhs.selectscod[x] for x in lhs.dimensions ]
        #selectscod = rhs.selectscod[lhs.dimension:lhs.dimension + 1]
        frozen_qsts = [ f for q in [ rhs ] for f in q.frozen_qsts ]
        if selectscod[0].alias != Name("key"):  # This should not occur - we only order by columns actually selected
            orderby = None
            orderdir = ""
    else:
        selectscod = lhs.selectscod
        wheres = lhs.wheres + wheres

        if lhs.frm.table:
            joinfrm = lhs.frm 
            joincod = rhs.selectscod[0].get_column()
            joindom = lhs.selectsdom[0].get_column()
            if joincod == joindom:
                alias = Name(f"{joincod.table}")
            else:
                if f"{joinfrm.table}"[0:3] == "tmp":
                    alias = joinfrm.table
                    joinfrm.alias = ""
                else:
                    alias = Name(f"{joincod.table}_{joincod.column}")
                    joinfrm.alias = alias
                    joindom.table = alias

                joins.append(CondAlias(joinfrm.table, joinfrm.alias, joindom, joincod))

            for j in lhs.joins:
                j.replace_alias(joinfrm.table, alias)
                joins.append(j)

            for c in selectscod:
                c.replace_table(joinfrm.table, alias)

        frozen_qsts = [ f for q in [ rhs, lhs ] for f in q.frozen_qsts ]
        if lhs.orderby is not None:
            orderby = lhs.orderby
            orderdir = lhs.orderdir
    qsts.append(QStruct(selectsdom, selectscod, frm, joins, wheres, [], frozen_qsts, None, orderby, orderdir))
    return do_composition(qsts, var, order)

def cmplproduct(args, var, order):
    qsts = []
    for arg in args:
        qsts.append(do_cmpl(arg, var, order))

    if isinstance(qsts[0], QProjection):
        dimensions = []
        for qst in qsts:
            if not isinstance(qst, QProjection):
                raise SyntaxError("Product contains mixture of projections and other stuff")
            dimensions += qst.dimensions
        
        return QProjection(dimensions)

    freeze_qsts(qsts)

    selectsdom = qsts[0].selectsdom
    joins = []

    # Is the following necessary? 
    # domain of all product operands must be the same, can we then conclude that table is also the same?
    # If this is the case, this for loop is not necessary
    # Edit: No we cannot. One table or both can be frozen queries, in which case table names are different
    for qst in qsts[1:]:
        if qst.selectsdom[0].table != selectsdom[0].table:
            joins.append(CondAlias(qst.selectsdom[0].table, "", selectsdom[0].get_column(), qst.selectsdom[0].get_column()))
    selectscod = [s for q in qsts for s in q.selectscod ]
    frm = qsts[0].frm
    joins += [ j for q in qsts for j in q.joins ]
    wheres = [ w for q in qsts for w in q.wheres ]
    groupbys = qsts[0].groupbys
    frozen_qsts = [ f for q in qsts for f in q.frozen_qsts ]
    orderby = None
    orderdir = ""
    for qst in qsts:
        if qst.orderby is not None:
            orderby = qst.orderby
            orderdir = qst.orderdir

    qst = QStruct(selectsdom, selectscod, frm, joins, wheres, groupbys, frozen_qsts, None, orderby, orderdir)
    return qst

def cmplinclusion(args, var, order):
    qsts = []
    for arg in args:
        qsts.append(do_cmpl(arg, var, order))

    freeze_qsts(qsts)

    selectsdom = qsts[0].selectsdom
    joins = []
    for qst in qsts[1:]:
        if qst.selectsdom[0].table != selectsdom[0].table:
            joins.append(CondAlias(qst.selectsdom[0].table, "", selectsdom[0].get_column(), qst.selectsdom[0].get_column()))
    selectscod = deepcopy(selectsdom)
    frm = qsts[0].frm
    joins += [ j for q in qsts for j in q.joins]
    wheres = qsts[0].wheres     # Gather wheres from inclusions within inclusions.
                                # If arguments contain wheres, they should be the same for all arguments, 
                                # since the domain of every argument must be the same. Hence it is sufficient
                                # to only gather the wheres from the 1st argument.
    for i, q in enumerate(qsts):
        if i % 2 == 0: # LHS of comparison
            lhs = q.selectscod
        else:
            rhs = q.selectscod
            for l, r in zip(lhs, rhs):  # We can assume the input is well-formed, and hence lhs and rhs have the same length
                wheres.append(Cond(l, r))
    frozen_qsts = [ f for q in qsts for f in q.frozen_qsts ]
    qst = QStruct(selectsdom, selectscod, frm, joins, wheres, [], frozen_qsts)
    return qst

def cmplinverse(args, var, order):
    qsts = []
    for arg in args:
        qsts.append(do_cmpl(arg, var, order))

    freeze_qsts(qsts)

    selectsdom = deepcopy(qsts[0].selectscod)
    selectscod = deepcopy(qsts[0].selectscod)
    frm = qsts[0].frm
    joins = qsts[0].joins
    wheres = qsts[0].wheres
    frozen_qsts = [ f for q in qsts for f in q.frozen_qsts ]
    orderby = qsts[0].orderby
    orderdir = qsts[0].orderdir

    qst = QStruct(selectsdom, selectscod, frm, joins, wheres, [], frozen_qsts, True, orderby, orderdir)
    return qst

def cmplaggregation(args, var, order):
    qsts = []
    for arg in args:
        qsts.append(do_cmpl(arg, var, order))

    freeze_qsts(qsts)

    selectsdom = qsts[1].selectscod
    joins = []

    if qsts[0].selectsdom[0].table and qsts[1].selectsdom[0].table and qsts[0].selectsdom[0].table != qsts[1].selectsdom[0].table:
        joins.append(CondAlias(qsts[0].selectsdom[0].table, "", qsts[0].selectsdom[0].get_column(), qsts[1].selectsdom[0].get_column()))
    selectscod = []
    for s in qsts[0].selectscod:
        selectscod.append(ExpressionAlias([s.get_column()], alias = s.alias, infix = "", prefix = "SUM"))
    frm = qsts[1].frm
    joins += [ j for j in qsts[0].joins + qsts[1].joins ]
    wheres = [ w for w in qsts[0].wheres + qsts[1].wheres ]
    groupbys = [ s.get_column() for s in selectsdom if s.table ]
    if not groupbys:
         groupbys = True
    frozen_qsts = [ f for q in qsts for f in q.frozen_qsts ]
    qst = QStruct(selectsdom, selectscod, frm, joins, wheres, groupbys, frozen_qsts, False, qsts[0].orderby, qsts[0].orderdir)
    return qst

def cmplprojection(args, var, order):
    """ The projection operator has as input n arguments. The last argument is a number n
        while the other arguments are terms. The projection operator selects the nth term
        from the list of terms. The parameter n is between 1 and the number of terms, inclusive"""
    
    return QProjection([args[-1] - 1])

def cmploperator(term, var, order):
    if term.name == "(/)":
        qop = QOperator(infix = " / ")
        return qop
    
def findtable(term_name):
    for d in data:
        if foundsome(term_name, d.constr):
            return d
    return None
        
def foundsome(subterm_name, term):
    if term.__class__.__name__ == 'Application':
        for arg in term.args:
            if foundsome(subterm_name, arg):
                return True
    elif term.__class__.__name__ == 'Variable' or term.__class__.__name__ == "Constant" or term.__class__.__name__ == "ObjectTypeRelation":
        if term.name == subterm_name:
            return True
    return False
    
def cmplobjecttyperelation(term, var, order):
    name = re.sub(' ', '_', term.name)
    table = findtable(name)
    frm = TableAlias(table)
    selectsdom = [ ColumnAlias(frm.get_alias(), f"{table}_id", "") ]
    selectscod = [ ColumnAlias(frm.get_alias(), f"{name}", "") ]
    qst = QStruct(selectsdom, selectscod, frm, [], [])
    return qst

def cmplvariable(term, var, order):
    if term.codomain == one or term.name[:3] == "een":
        return cmplimmediate(term, var, order)

    # Code below copied from cmplobjecttyperelation() and adapted
    table = findtable(term.name)
    name = re.sub(' ', '_', term.name)
    frm = TableAlias(table)
    selectsdom = [ ColumnAlias(frm.get_alias(), f"{table}_id", "") ]
    selectscod = [ ColumnAlias(frm.get_alias(), f"{name}", "") ]
    orderby = None
    if var is not None and var.equals(term):
        orderby = Name("key")
        selectscod[0].alias = Name("key")
    qst = QStruct(selectsdom, selectscod, frm, None, None, None, None, None, orderby, order)
    return qst

def cmplimmediate(term, var, order):
    if term.codomain == one:
        imm = "'*'"
    elif term.name[:3] == "een":
        imm = "1"
    table = term.domain.name
    frm = TableAlias(table) 
    selectsdom = [ ColumnAlias(frm.get_alias(), f"{table}_id", "") ]
    selectscod = [ ColumnAlias("", f"{imm}", "") ]
    orderby = None
    if var is not None and var.equals(term):
        orderby = Name("key")
        selectscod[0].alias = Name("key")
    qst = QStruct(selectsdom, selectscod, frm, None, None, None, None, None, orderby, order)
    return qst

def cmplconstant(term, var, order):
    name = re.sub(" ", "_", term.name)
    selectsdom = [ ColumnAlias("", f"'*'", "") ]
    selectscod = [ ColumnAlias("", f"'{name}'", "") ]
    qst = QStruct(selectsdom, selectscod, TableAlias(""), [], [])
    return qst

if __name__ == '__main__':
    #testTableAlias()
    #testColumn()
    #quit()
    # create = Name('tmp_persoon')
    # selectsdom = [Alias('baan_werknemer.persoon_id', 'baan_werknemer.persoon_id')]
    # selectscod = [Alias('baan_werknemer.naam', 'baan_werknemer.naam')]
    # frm = Alias('baan', 'baan')
    # print(frm)
    # joins = [CondAlias('persoon', 'baan_werknemer', 'baan_werknemer.persoon_id', 'baan.werknemer')]
    # wheres = [Cond('baan_werknemer.woont_in', 'Amsterdam'), Cond('baan.functie', 'tandarts')]
    # groupbys = []
    # orderbys = []
    # #qst = QStruct(create, selectsdom, selectscod, frm, joins, wheres, groupbys, orderbys)
    # qst = QStruct(selectsdom, selectscod, frm, joins, wheres)
    # print(qst)
    # print(wheres)
    # print(joins)
    # q = cmplobjecttyperelation(woontop)
    # r = cmplobjecttyperelation(ligtin)
    pass