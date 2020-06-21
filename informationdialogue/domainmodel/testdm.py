from informationdialogue.term.trm import *
from informationdialogue.kind.knd import *

lookup = {}

# object types
persoon = ObjectType(name='persoon')
adres = ObjectType(name='adres')
gemeente = ObjectType(name='gemeente')
provincie = ObjectType(name='provincie')
bedrijf = ObjectType(name='bedrijf')
baan = ObjectType(name='baan')

# phenomena and quantities
getal = Quantity(name='getal')
datum = Quantity(name='datum')
tekst = Phenomenon(name='tekst')
gemeentenamen = Phenomenon(name='gemeentenamen')
provincienamen = Phenomenon(name='provincienamen')
straatnamen = Phenomenon(name='straatnamen')
geslachten = Phenomenon(name='geslachten')
huisnummers = Phenomenon(name='huisnummers')
namen = Phenomenon(name='namen')
identificator = Phenomenon(name='identificator')
activiteiten = Phenomenon(name='activiteiten')
beroepen = Phenomenon(name='beroepen')

# object type relations
woontop = ObjectTypeRelation(name='woont op', domain=persoon, codomain=adres)
ligtin = ObjectTypeRelation(name='ligt in', domain=adres, codomain=gemeente)
deelvan = ObjectTypeRelation(name='deel van', domain=gemeente, codomain=provincie)
werknemer = ObjectTypeRelation(name='werknemer', domain=baan, codomain=persoon)
werkgever = ObjectTypeRelation(name='werkgever', domain=baan, codomain=bedrijf)
gevestigdop = ObjectTypeRelation(name='gevestigd op', domain=bedrijf, codomain=adres)

# variables
leeftijd = Variable(name='leeftijd', domain=persoon, codomain=getal)
inkomen = Variable(name='inkomen', domain=persoon, codomain=getal)
lengte = Variable(name='lengte', domain=persoon, codomain=getal)
gewicht = Variable(name='gewicht', domain=persoon, codomain=getal)
geslacht = Variable(name='geslacht', domain=persoon, codomain=geslachten)
geboortedatum = Variable(name='geboortedatum', domain=persoon, codomain=datum)
naam = Variable(name='naam', domain=persoon, codomain=namen)
huisnummer = Variable(name='huisnummer', domain=adres, codomain=huisnummers)
straatnaam = Variable(name='straatnaam', domain=adres, codomain=straatnamen)
gemeentenaam = Variable(name='gemeentenaam', domain=gemeente, codomain=gemeentenamen)
provincienaam = Variable(name='provincienaam', domain=provincie, codomain=provincienamen)
functie = Variable(name='functie', domain=baan, codomain=beroepen)
salaris = Variable(name='salaris', domain=baan, codomain=getal)
omzet = Variable(name='omzet', domain=bedrijf, codomain=getal)
economischehoofdactiviteit = Variable(name='economische hoofdactiviteit', domain=bedrijf, codomain=activiteiten)

# keys and foreign keys
persoonid = Variable(name='persoon_id', domain=persoon, codomain=identificator)
adresid = Variable(name='adres_id', domain=adres, codomain=identificator)
gemeenteid = Variable(name='gemeente_id', domain=gemeente, codomain=identificator)
provincieid = Variable(name='provincie_id', domain=provincie, codomain=identificator)
persoonadresid = Variable(name='woont_op', domain=persoon, codomain=identificator)
adresgemeenteid = Variable(name='ligt_in', domain=adres, codomain=identificator)
gemeenteprovincieid = Variable(name='deel_van', domain=gemeente, codomain=identificator)
baanid = Variable(name='baan_id', domain=baan, codomain=identificator)
bedrijfid = Variable(name='bedrijf_id', domain=bedrijf, codomain=identificator)
baanpersoonid = Variable(name='werknemer', domain=baan, codomain=persoon)
baanbedrijfid = Variable(name='werkgever', domain=baan, codomain=persoon)
bedrijfadresid = Variable(name='gevestigd_op', domain=bedrijf, codomain=adres)

# nice to haves
eenpersoon = Variable(name='een(persoon)', domain=persoon, codomain=getal)
eenadres = Variable(name='een(adres)', domain=adres, codomain=getal)
eengemeente = Variable(name='een(gemeente)', domain=gemeente, codomain=getal)
eenbaan = Variable(name='een(baan)', domain=baan, codomain=getal)
eenbedrijf = Variable(name='een(bedrijf)', domain=bedrijf, codomain=getal)
allepersonen = Variable(name='alle(persoon)', domain=persoon, codomain=one)
allebanen = Variable(name='alle(baan)', domain=baan, codomain=one)

# constants
# cities
denhaag = Constant(name='Den Haag', codomain=gemeentenamen, code='Den Haag')
delft = Constant(name='Delft', codomain=gemeentenamen, code='Delft')
rotterdam = Constant(name='Rotterdam', codomain=gemeentenamen, code='Rotterdam')
utrecht = Constant(name='Utrecht', codomain=gemeentenamen, code='Utrecht')
leiden = Constant(name='Leiden', codomain=gemeentenamen, code='Leiden')

#provinces
zuidholland = Constant(name='Zuid-Holland', codomain=provincienamen, code='Zuid-Holland')

# streets
aartvanderleeuwlaan = Constant(name='Aart van der Leeuwlaan', codomain=straatnamen, code='Aart van der Leeuwlaan')
prinsmauritsstraat = Constant(name='Prins Mauritsstraat', codomain=straatnamen, code='Prins Mauritsstraat')
westlandseweg = Constant(name='Westlandseweg', codomain=straatnamen, code='Westlandseweg')
meppelerweg = Constant(name='Meppelerweg', codomain=straatnamen, code='Meppelerweg')
lutherseburgwal = Constant(name='Lutherse Burgwal', codomain=straatnamen, code='Lutherse Burgwal')
coolsingel = Constant(name='Coolsingel', codomain=straatnamen, code='Coolsingel')
blaak = Constant(name='Blaak', codomain=straatnamen, code='Blaak')
amsterdamsestraatweg = Constant(name='Amsterdamsestraatweg', codomain=straatnamen, code='Amsterdamsestraatweg')
europalaan = Constant(name='Europalaan', codomain=straatnamen, code='Europalaan')
josephhaydnlaan = Constant(name='Joseph Haydnlaan', codomain=straatnamen, code='Joseph Haydnlaan')
rapenburg = Constant(name='Rapenburg', codomain=straatnamen, code='Rapenburg')
wittesingel = Constant(name='Witte Singel', codomain=straatnamen, code='Witte Singel')
haagweg = Constant(name='Haagweg', codomain=straatnamen, code='Haagweg')
klikspaanweg = Constant(name='Klikspaanweg', codomain=straatnamen, code='Klikspaanweg')

# names
tjalling = Constant(name='Tjalling', codomain=namen, code='Tjalling')
maartje = Constant(name='Maartje', codomain=namen, code='Maartje')
emma = Constant(name='Emma', codomain=namen, code='Emma')
john = Constant(name='John', codomain=namen, code='John')
hans = Constant(name='Hans', codomain=namen, code='Hans')
mirjam = Constant(name='Mirjam', codomain=namen, code='Mirjam')
petra = Constant(name='Petra', codomain=namen, code='Petra')
karsten = Constant(name='Karsten', codomain=namen, code='Karsten')
thor = Constant(name='Thor', codomain=namen, code='Thor')
kirsten = Constant(name='Kirsten', codomain=namen, code='Kirsten')
marcel = Constant(name='Marcel', codomain=namen, code='Marcel')
irene = Constant(name='Irene', codomain=namen, code='Irene')
robert = Constant(name='Robert', codomain=namen, code='Robert')
ellen = Constant(name='Ellen', codomain=namen, code='Ellen')
chris = Constant(name='Chris', codomain=namen, code='Chris')
rachel = Constant(name='Rachel', codomain=namen, code='Rachel')
jacob = Constant(name='Jacob', codomain=namen, code='Jacob')
johanna = Constant(name='Johanna', codomain=namen, code='Johanna')
jeroen = Constant(name='Jeroen', codomain=namen, code='Jeroen')
david = Constant(name='David', codomain=namen, code='David')
esther = Constant(name='Esther', codomain=namen, code='Esther')
diana = Constant(name='Diana', codomain=namen, code='Diana')
mathilde = Constant(name='Mathilde', codomain=namen, code='Mathilde')
jeroen = Constant(name='Jeroen', codomain=namen, code='Jeroen')
henriette = Constant(name='Henriette', codomain=namen, code='Henriette')
sander = Constant(name='Sander', codomain=namen, code='Sander')
harry = Constant(name='Harry', codomain=namen, code='Harry')
barry = Constant(name='Barry', codomain=namen, code='Barry')
alex = Constant(name='Alex', codomain=namen, code='Alex')
samantha = Constant(name='Samantha', codomain=namen, code='Samantha')
bob = Constant(name='Bob', codomain=namen, code='Bob')
richard = Constant(name='Richard', codomain=namen, code='Richard')
jack = Constant(name='Jack', codomain=namen, code='Jack')
jill = Constant(name='Jill', codomain=namen, code='Jill')
sandra = Constant(name='Sandra', codomain=namen, code='Sandra')
peter = Constant(name='Peter', codomain=namen, code='Peter')
sabine = Constant(name='Sabine', codomain=namen, code='Sabine')
ronald = Constant(name='Ronald', codomain=namen, code='Ronald')
linda = Constant(name='Linda', codomain=namen, code='Linda')
tim = Constant(name='Tim', codomain=namen, code='Tim')
tom = Constant(name='Tom', codomain=namen, code='Tom')
selena = Constant(name='Selena', codomain=namen, code='Selena')
gerard = Constant(name='Gerard', codomain=namen, code='Gerard')
aart = Constant(name='Aart', codomain=namen, code='Aart')
marjan = Constant(name='Marjan', codomain=namen, code='Marjan')
erik = Constant(name='Erik', codomain=namen, code='Erik')
arnout = Constant(name='Arnout', codomain=namen, code='Arnout')
thea = Constant(name='Thea', codomain=namen, code='Thea')
jacobiene = Constant(name='Jacobiene', codomain=namen, code='Jacobiene')
ronaldo = Constant(name='Ronaldo', codomain=namen, code='Ronaldo')
gaby = Constant(name='Gaby', codomain=namen, code='Gaby')
guido = Constant(name='Guido', codomain=namen, code='Guido')

#sexes
man = Constant(name='man', codomain=geslachten, code='man')
vrouw = Constant(name='vrouw', codomain=geslachten, code='vrouw')

# occupations
kolonel = Constant(name='kolonel', codomain=beroepen, code='kolonel')
wethouder = Constant(name='wethouder', codomain=beroepen, code='wethouder')
griffier = Constant(name='griffier', codomain=beroepen, code='griffier')
seismoloog = Constant(name='seismoloog', codomain=beroepen, code='seismoloog')
watermanager = Constant(name='watermanager', codomain=beroepen, code='watermanager')
oogarts = Constant(name='oogarts', codomain=beroepen, code='oogarts')

# actitivities
industrie = Constant(name='industrie', codomain=activiteiten, code='industrie')
onderwijs = Constant(name='onderwijs', codomain=activiteiten, code='onderwijs')
bouwnijverheid = Constant(name='bouwnijverheid', codomain=activiteiten, code='bouwnijverheid')
openbaarbestuur = Constant(name='openbaar bestuur', codomain=activiteiten, code='openbaar bestuur')
zakelijkedienstverlening = Constant(name='zakelijke dienstverlening', codomain=activiteiten, code='zakelijke dienstverlening')
gezondheidszorg = Constant(name='gezondheidszorg', codomain=activiteiten, code='gezondheidszorg')

# operators
gedeelddoor = Operator(name='(/)', domain=Application(cartesian_product,[getal, getal]), codomain=getal)

# domain model
domainmodel = [persoon, adres, gemeente, provincie, baan, bedrijf, getal, datum, tekst, gemeentenamen, provincienamen, straatnamen, geslachten, huisnummers,
      namen, beroepen, activiteiten, woontop, ligtin, werknemer, werkgever, gevestigdop, leeftijd, inkomen, gewicht, lengte, geslacht, geboortedatum, naam, huisnummer, straatnaam, gemeentenaam,
      salaris, functie, omzet, economischehoofdactiviteit, man, vrouw, gedeelddoor, persoonid, adresid, gemeenteid, provincieid, baanid, bedrijfid]

#### persoonadresid, adresgemeenteid, bedrijfid, baanpersoonid, baanbedrijfid, bedrijfadresid

domainmodel.extend([denhaag, delft, rotterdam, utrecht,
      leiden, zuidholland, kolonel, wethouder, griffier, seismoloog, watermanager, oogarts, industrie, onderwijs, bouwnijverheid, openbaarbestuur,
      zakelijkedienstverlening, gezondheidszorg, tjalling, maartje, emma, john, hans, mirjam, petra, karsten, thor, kirsten,
      marcel, irene, robert, ellen, chris, rachel, jacob, johanna, david, esther, diana, mathilde, jeroen, henriette, sander,
      harry, barry, alex, samantha, bob, richard, jack, jill, sandra, peter, sabine, ronald, linda, tim, tom, selena, gerard,
      aart, marjan, erik, arnout, thea, jacobiene, ronaldo, gaby, aartvanderleeuwlaan, prinsmauritsstraat, westlandseweg,
      meppelerweg, lutherseburgwal, coolsingel, blaak, amsterdamsestraatweg, europalaan, josephhaydnlaan, rapenburg, wittesingel,
      haagweg, klikspaanweg])


# datasets
persoondata = DatasetDesign(name='persoon', constr=Application(product, [persoonid, naam, leeftijd, lengte, gewicht, geslacht, inkomen, persoonadresid]))
adresdata = DatasetDesign(name='adres', constr=Application(product, [adresid, straatnaam, huisnummer, adresgemeenteid]))
gemeentedata = DatasetDesign(name='gemeente', constr=Application(product, [gemeenteid, gemeentenaam, gemeenteprovincieid]))
provinciedata = DatasetDesign(name='provincie', constr=Application(product, [provincieid, provincienaam]))
baandata = DatasetDesign(name='baan', constr=Application(product, [baanid, functie, salaris, baanpersoonid, baanbedrijfid]))
bedrijfdata = DatasetDesign(name='bedrijf', constr=Application(product, [bedrijfid, economischehoofdactiviteit, omzet, bedrijfadresid]))

data = [persoondata, adresdata, gemeentedata, provinciedata, baandata, bedrijfdata]

# default variables
defaults = {
    persoon : [naam],
    adres : [straatnaam, huisnummer],
    gemeente : [gemeentenaam],
    baan : [baanid],
    bedrijf : [bedrijfid]
}

prefaggrmode = {
    leeftijd : 'avg',
    inkomen : 'sum',
    eenpersoon : 'sum',
    salaris : 'sum',
    omzet : 'sum'
}

prefvar = {
    namen : naam,
    huisnummers : huisnummer,
    geslachten : geslacht,
    gemeentenamen : gemeentenaam,
    straatnamen : straatnaam,
    beroepen : functie,
    activiteiten : economischehoofdactiviteit
}

orderedobjecttype = {
    adres : eenpersoon,
    gemeente : eenpersoon
}

# lookup table
lookup = {
    'naam' : naam,
    'namen' : naam,
    'heet' : naam,
    'heten' : naam,
    'wonen' : woontop,
    'woont' : woontop,
    'persoon' : persoon,
    'personen' : persoon,
    'mens' : persoon,
    'mensen' : persoon,
    'adres' : adres,
    'adressen' : adres,
    'gemeente' : gemeente,
    'gemeenten' : gemeente,
    'gemeentenaam' : gemeentenaam,
    'huisnummers' : huisnummer,
    'huisnummer' : huisnummer,
    'nummer' : huisnummer,
    'leeftijd' : leeftijd,
    'inkomen' : inkomen,
    'oud' : leeftijd,
    'oudst' : [leeftijd, 'desc'],
    'oudste' : [leeftijd, 'desc'],
    'jongst' : [leeftijd, 'asc'],
    'jongste' : [leeftijd, 'asc'],
    'gezin' : adres,
    'gezinnen' : adres,
    'inwoner' : ObjectTypeRelation(name='inwoner', constr=Application(composition, [ligtin, woontop])),
    'inwoners' : ObjectTypeRelation(name='inwoner', constr=Application(composition, [ligtin, woontop])),
    'bewoner' : woontop,
    'bewoners' : woontop,
    'geslacht' : geslacht,
    'geslachten' : geslacht,
    'man' : man,
    'mannen' : man,
    'mannelijk' : man,
    'mannelijke' : man,
    'vrouw' : vrouw,
    'vrouwen' : vrouw,
    'vrouwelijk' : vrouw,
    'vrouwelijke' : vrouw,
    'ligt' : ligtin,
    'verdien' : inkomen,
    'verdient' : inkomen,
    'verdienen' : inkomen,
    'verdiend' : inkomen,
    'den haag' : denhaag,
    "'s-Gravenhage" : denhaag,
    'delft' : delft,
    'rotterdam' : rotterdam,
    'utrecht' : utrecht,
    'leiden' : leiden,
    'kolonel' : kolonel,
    'kolonels' : kolonel,
    'kolonellen' : kolonel,
    'wethouder' : wethouder,
    'wethouders' : wethouder,
    'griffier' : griffier,
    'griffiers' : griffier,
    'seismoloog' : seismoloog,
    'seismologen' : seismoloog,
    'watermanager' : watermanager,
    'watermanagers' : watermanager,
    'oogarts' : oogarts,
    'oogartsen' : oogarts,
    'industrie' : industrie,
    'industrieel' : industrie,
    'industriele' : industrie,
    'onderwijs' : onderwijs,
    'onderwijsinstelling' : onderwijs,
    'onderwijsinstellingen' : onderwijs,
    'school' : onderwijs,
    'scholen' : onderwijs,
    'bouwnijverheid' : bouwnijverheid,
    'bouwbedrijf' : bouwnijverheid,
    'bouwbedrijven' : bouwnijverheid,
    'openbaar bestuur' : openbaarbestuur,
    'zakelijke dienstverlening' : zakelijkedienstverlening,
    'zakelijke dienst' : zakelijkedienstverlening,
    'zakelijke diensten' : zakelijkedienstverlening,
    'gezondheidszorg' : gezondheidszorg,
    'werken' : werkgever,
    'werkt' : werkgever,
    'baan' : baan,
    'banen' : baan,
    'tjalling' : tjalling,
    'maartje' : maartje,
    'emma' : emma,
    'john' : john,
    'hans' : hans,
    'mirjam' : mirjam,
    'petra' : petra,
    'karsten' : karsten,
    'thor' : thor,
    'kirsten' : kirsten,
    'marcel' : marcel,
    'irene' : irene,
    'robert' : robert,
    'ellen' : ellen,
    'chris' : chris,
    'rachel' : rachel,
    'jacob' : jacob,
    'johanna' : johanna,
    'david' : david,
    'esther' : esther,
    'diana' : diana,
    'mathilde' : mathilde,
    'jeroen' : jeroen,
    'henriette' : henriette,
    'sander' : sander,
    'harry' : harry,
    'barry' : barry,
    'alex' : alex,
    'samantha' : samantha,
    'bob' : bob,
    'richard' : richard,
    'jack' : jack,
    'jill' : jill,
    'sandra' : sandra,
    'peter' : peter,
    'sabine' : sabine,
    'ronald' : ronald,
    'linda' : linda,
    'tim' : tim,
    'tom' : tom,
    'selena' : selena,
    'gerard' : gerard,
    'aart' : aart,
    'marjan' : marjan,
    'erik' : erik,
    'arnout' : arnout,
    'thea' : thea,
    'jacobiene' : jacobiene,
    'ronaldo' : ronaldo,
    'gaby' : gaby,
    'aart van der leeuwlaan' : aartvanderleeuwlaan,
    'prins mauritsstraat' : prinsmauritsstraat,
    'westlandseweg' : westlandseweg,
    'meppelerweg' : meppelerweg,
    'lutherse burgwal' : lutherseburgwal,
    'coolsingel' : coolsingel,
    'blaak' : blaak,
    'amsterdamsestraatweg' : amsterdamsestraatweg,
    'europalaan' : europalaan,
    'joseph haydnlaan' : josephhaydnlaan,
    'rapenburg' : rapenburg,
    'witte singel' : wittesingel,
    'haagweg' : haagweg,
    'klikspaanweg' : klikspaanweg,
    'werken' : werkgever,
    'werkt' : werkgever,
    'bedrijf' : bedrijf,
    'bedrijven' : bedrijf,
    'gevestigd' : gevestigdop,
    'vestiging' : gevestigdop,
    'salaris' : salaris,
    'activiteit' : economischehoofdactiviteit,
    'hoofdactiviteit' : economischehoofdactiviteit,
    'beroep' : beroepen,
    'beroepen' : beroepen,
    'functie' : functie,
    'functies' : functie,
    'woongemeente' : gemeente,
    'omzet' : omzet,
    'werknemer' : werknemer,
    'werkgever' : werkgever
}

overridetarget = {
    beroepen : persoon,
    geslachten : persoon,
    activiteiten : bedrijf
}

optimalpathhelper = {
    werkgever : ["in", [gevestigdop]]
}

whichway = {
    baan : werkgever
}

interrogativepronouns = {
        persoon : 'wie',
        adres : 'waar',
        gemeente : 'waar'}





