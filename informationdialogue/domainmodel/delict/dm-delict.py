from term import Application, product
from kind import Phenomenon, ObjectType, Variable, ObjectTypeRelation, DatasetDesign
from dm import gemeente, gemeentenamen, gemeentenaam, gemeenteid, getal, domainmodel, lookup
from scmcodelookup import lookupscmcode
from maandlookup import lookupmaand
from interpretcodelists import addconsts, makescmcodedata


vocab = []

# object types
delict = ObjectType(name='delict')
buurt = ObjectType(name='buurt')
# gemeente = ObjectType(name='gemeente')
datum = ObjectType(name='datum')

# phenomena and quantities
# getal = Quantity(name='getal')
# gemeentenamen = Phenomenon(name='gemeentenaam')
dagen = Phenomenon(name='dag')
maanden = Phenomenon(name='maand')
buurtnamen = Phenomenon(name='buurtnaam')
delictsoorten = Phenomenon(name='delictsoort')
# locatiesoorten = Phenomenon(name='locatiesoort')
identificaties = Phenomenon(name='identificatie')

# object type relations
gepleegdin = ObjectTypeRelation(name='gepleegd in', domain=delict, codomain=buurt)
onderdeelvan = ObjectTypeRelation(name='onderdeel van', domain=buurt, codomain=gemeente)
gepleegdop = ObjectTypeRelation(name='gepleegd op', domain=delict, codomain=datum)

# variables
# gemeentenaam = Variable(name='gemeentenaam', domain=gemeente, codomain=gemeentenamen)
buurtnaam = Variable(name='buurtnaam', domain=buurt, codomain=buurtnamen)
soort = Variable(name='soort', domain=delict, codomain=delictsoorten)
aantalverdachten = Variable(name='aantal verdachten', domain=delict, codomain=getal)
# soortlocatie = Variable(name='soort locatie', domain=delict, codomain=locatiesoorten)
dag = Variable(name='dag', domain=datum, codomain=dagen)
maand = Variable(name='maand', domain=datum, codomain=maanden)

# keys and foreign keys
delictid = Variable(name='delict_id', domain=delict, codomain=identificaties)
# gemeenteid = Variable(name='gemeente_id', domain=gemeente, codomain=identificaties)
buurtid = Variable(name='buurt_id', domain=buurt, codomain=identificaties)
datumid = Variable(name='datum_id', domain=datum, codomain=identificaties)
delictbuurtid = Variable(name='gepleegd_in', domain=delict, codomain=buurt)
delictdatumid = Variable(name='gepleegd_op', domain=delict, codomain=datum)
buurtgemeenteid = Variable(name='onderdeel_van', domain=buurt, codomain=gemeente)

# nice to haves
eendelict = Variable(name='een', domain=delict, codomain=getal)
eenbuurt = Variable(name='een', domain=buurt, codomain=getal)
# eengemeente = Variable(name='een', domain=gemeente, codomain=getal)
eendatum = Variable(name='een', domain=datum, codomain=getal)


# operators
# gedeelddoor = Operator(name='(/)', domain=Application(cartesian_product,[getal, getal]), codomain=getal)


# domain model
domainmodel += [delict, buurt, datum, dagen, maanden, buurtnamen, delictsoorten,
               identificaties, gepleegdin, onderdeelvan, gepleegdop, buurtnaam,
               soort, aantalverdachten, dag, maand, delictid, buurtid, datumid,
               delictbuurtid, delictdatumid, buurtgemeenteid, eendelict, eenbuurt, eendatum]

lookupdm = {
        'delict' : delict,
        'misdrijf' : delict,
        'vergrijp' : delict,
        'overtreding': delict,
        'buurt' : buurt,
        'datum' : datum,
        'data' : datum,
        'dag': datum,
        'dagen' : datum
}

# constants
# cities

# neighborhoods

# locations
# addconsts('aardlocatie.xml', locatiesoorten, domainmodel)

# crimes
domainmodel += makescmcodedata()

# days
addconsts('dag.xml', dagen, domainmodel)

# months
addconsts('maand.xml', maanden, domainmodel)


# datasets
delictdata = DatasetDesign(name='delict', constr=Application(product, [delictid, soort, aantalverdachten, delictdatumid, delictbuurtid]))
buurtdata = DatasetDesign(name='buurt', constr=Application(product, [buurtid, buurtnaam, buurtgemeenteid]))
gemeentedata = DatasetDesign(name='gemeente', constr=Application(product, [gemeenteid, gemeentenaam]))
datumdata = DatasetDesign(name='datum', constr=Application(product, [datumid, dag, maand]))

data = [delictdata, buurtdata, gemeentedata, datumdata]

# default variables
defaults = {
    delict : [delictid],
    buurt : [buurtnaam],
    gemeente : [gemeentenaam],
    datum : [dag, maand]
}

prefaggrmode = {
    aantalverdachten : 'avg'
}

prefvar = {
    delictsoorten : soort,
    buurtnamen : buurtnaam,
    gemeentenamen: gemeentenaam
}

orderedobjecttype = {
    delict : None,
    buurt : None,
    gemeente : None,
    datum : None
}

# lookup table

# lookup = {

# }

overridetarget = {
    delictsoorten : delict
}

# optimalpathhelper = {
# }

# streets
# with open('straatnamen.txt') as f:
#     for line in f:
#         c = Constant(name=line.rstrip(), codomain=straatnamen)
#         domainmodel.append(c)
#         lookup[line.rstrip().lower()] = c
        

if __name__ == '__main__':
    for k in lookupmaand.keys():
        for d in domainmodel:
            if lookupmaand[k] == d.name:
                lookup[k] = d
    for k in lookupscmcode.keys():
        for d in domainmodel:
            if lookupscmcode[k] == d.name:
                lookup[k] = d
    for k in lookupdm.keys():
        lookup[k] = lookupdm[k]
    for k in lookup.keys():
        if isinstance(k, tuple):
            for l in k:
                if not l in vocab:
                    vocab.append(l)
        else:
            if not k in vocab:
                vocab.append(k)

