from numberformat import getFloat, getText
from habitablezone import hzLimits
from math import *

titles = {
    "confirmed":                    "Only confirmed planets",
    "multiplanet":                  "Only multi-planetary systems",
    "multistar":                    "Only multi-star systems",
    "nomultistar":                  "No multi-star systems",
    "transiting":                   "Only transiting planets",
    "habitable":                    "Only planets in the habitable zone",
    "discoveryrv":                  "Planets discovered by RV",
}

def isHabitable(xmlPair):
    system, planet, star, filename = xmlPair
    maxa = 0
    if star is None:
        return False # no binary systems (yet)

    hzData = hzLimits(star)
    if hzData is None:
        return False

    HZinner2, HZinner, HZouter, HZouter2, stellarRadius = hzData

    semimajoraxis = getFloat(planet,"./semimajoraxis")
    if semimajoraxis is None:
        hostmass = getFloat(star,"./mass",1.)
        period = getFloat(planet,"./period",265.25)
        semimajoraxis = pow(pow(period/6.283/365.25,2)*39.49/hostmass,1.0/3.0)

    if semimajoraxis>HZinner2 and semimajoraxis<HZouter2:
        return True
    return False

def isFiltered(xmlPair,filters):
    system, planet, star, filename = xmlPair
    for filter in filters:
        if filter=="confirmed":
            confirmed = False
            for list in planet.findall("./list"):
                if list.text =="Confirmed planets":
                    confirmed = True
            if confirmed == False:
                return True
        if filter=="multiplanet":
            if len(system.findall(".//planet"))<=1:
                return True
        if filter=="transiting":
            isTransiting = planet.find("./istransiting")
            if isTransiting is not None:
                if isTransiting.text!="1":
                    return True
            else:
                return True
        if filter=="discoveryrv":
            disc = planet.find("./discoverymethod")
            if disc is not None:
                if disc.text!="RV":
                    return True
            else:
                return True
        if filter=="multistar":
            if len(system.findall(".//star"))<=1:
                return True
        if filter=="nomultistar":
            if len(system.findall(".//star"))>1:
                return True
        if filter=="habitable":
            if not isHabitable(xmlPair):
                return True
    return False
