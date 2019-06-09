#!/usr/bin/python3



from pyhamtools import LookupLib, Callinfo

my_lookuplib = LookupLib(lookuptype="countryfile")
cic = Callinfo(my_lookuplib)
print(cic.get_all("DK9MBS"))

