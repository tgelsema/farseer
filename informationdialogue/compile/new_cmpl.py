DIALECT_MYSQL = "MySQL"
DIALECT_SQLSERVER = "T-SQL"


class Name:
    def __init__(self, name):
        self.name = str(name)

    def __bool__(self):
        return bool(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name

    def generate_code(self, dialect):
        return self.name


class Alias:
    def __init__(self, alias = ""):
        self.alias = Name(alias)

    def __str__(self):
        return str(self.alias)

    def __bool__(self):
        return bool(self.alias)

    def generate_code(self, dialect):
        return f" AS {self.alias.generate_code(dialect)}" if self.alias else ""
        
    def generate_reference(self, dialect):
        return f"{self.alias.generate_code(dialect)}" if self.alias else ""


class Table:
    def __init__(self, tablename, alias = ""):
        self.tablename = Name(tablename)
        self.alias = Alias(alias)

    def generate_code(self, dialect):
        return f"{self.tablename.generate_code(dialect)}{self.alias.generate_code(dialect)}"

    def generate_reference(self, dialect):
        if self.alias:
            return self.alias.generate_reference(dialect)
        else:
            return self.tablename.generate_code(dialect)


class Column:
    def __init__(self, table, columnname, alias = ""):
        """
        Assume table is a Table object; columnname and alias can be anything for which the str() function gives a valid value
        """
        self.table = table
        self.columnname = Name(columnname)
        self.alias = Alias(alias)

    def generate_code(self, dialect):
        return f"{self.table.generate_reference(dialect)}.{self.columnname.generate_code(dialect)}{self.alias.generate_code(dialect)}"

    def generate_reference(self, dialect):
        return f"{self.table.generate_reference(dialect)}.{self.columnname.generate_code(dialect)}"


class ExpressionColumn:
    def __init__(self, args, alias = "", prefix = "", infix = ", "):
        """
        Assume args is a list of Column objects; alias, prefix and suffix can be anything for which the str() function gives a valid value
        """
        self.args = args
        self.alias = Alias(alias)
        self.prefix = Name(prefix)
        self.infix = Name(infix)

    def generate_code(self, dialect):
        if len(self.args) == 0:
            return ""
        elif len(self.args) == 1 and not self.prefix:
            return f"{self.args[0].generate_code(dialect)}{self.alias.generate_code(dialect)}"
        else:
            argcode = self.infix.generate_code(dialect).join(arg.generate_reference(dialect) for arg in self.args)
            return f"{self.prefix.generate_code(dialect)}({argcode}){self.alias.generate_code(dialect)}"


class Cond:
    def __init__(self, lhs, rhs):
        """
        Assume lhs and rhs are Column objects
        """
        self.lhs = lhs
        self.rhs = rhs

    def generate_code(self, dialect):
        return f"({self.lhs.generate_reference(dialect)} = {self.rhs.generate_reference(dialect)})"


class CondList:
    def __init__(self):
        self.condlist = []

    def add_cond(self, cond):
        """
        Assume cond is a Cond object
        """
        self.condlist.append(cond)

    def generate_code(self, dialect):
        return " AND ".join(cond.generate_code(dialect) for cond in self.condlist)


class JoinSpec:
    def __init__(self, table, condlist):
        """
        Assume table is a Table object and condlist is a CondList object
        """
        self.table = table
        self.condlist = condlist

    def generate_code(self, dialect):
        return f"{self.table.generate_code(dialect)} ON {self.condlist.generate_code(dialect)}"


x = Name("Guido")
print(f"|{x.generate_code(DIALECT_MYSQL)}|")

a = Alias(Name("Heuvel"))
print(f"|{a.generate_code(DIALECT_MYSQL)}|")

b = Alias()
print(f"|{b.generate_code(DIALECT_MYSQL)}|")

y = Table(Name("tblPersonen"), Alias(Name("persoon_werknemer")))
print(f"|{y.generate_code(DIALECT_MYSQL)}|")
print(f"|{y.generate_reference(DIALECT_MYSQL)}|")

z = Table(Name("tblBedrijven"))
print(f"|{z.generate_code(DIALECT_MYSQL)}|")
print(f"|{z.generate_reference(DIALECT_MYSQL)}|")

w = Column(y, Name("Person_age"), Alias(Name("leeftijd")))
print(f"|{w.generate_code(DIALECT_MYSQL)}|")
print(f"|{w.generate_reference(DIALECT_MYSQL)}|")

v = Column(z, Name("Company_address"))
print(f"|{v.generate_code(DIALECT_MYSQL)}|")
print(f"|{v.generate_reference(DIALECT_MYSQL)}|")

c = Cond(v, w)
print(f"|{c.generate_code(DIALECT_MYSQL)}|")

cl = CondList()
cl.add_cond(c)
cl.add_cond(c)
print(f"|{cl.generate_code(DIALECT_MYSQL)}|")

j = JoinSpec(y, cl)
print(f"|{j.generate_code(DIALECT_MYSQL)}|")

e = ExpressionColumn([v, w], alias = "result", infix = " / ")
print(f"|{e.generate_code(DIALECT_MYSQL)}|")