from numberformat import getFloat, getText
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

    semimajoraxis = getFloat(planet,"./semimajoraxis")
    temperature = getFloat(star,"./temperature")
    stellarMass = getFloat(star,"./mass")
    stellarRadius = getFloat(star,"./radius")
    period = getFloat(planet,"./period")
    
    if semimajoraxis is None and stellarMass is not None and period is not None:
        semimajoraxis = pow(pow(period/6.283/365.25,2)*39.49/stellarMass,1.0/3.0) 

    if semimajoraxis is None or temperature is None or stellarRadius is None:
        return False # insufficient information to determine habitability
        
    rel_temp = temperature - 5700.
    luminosity = pow(stellarRadius, 2.) * pow(temperature / 5780., 4.)
    
    # Ref: http://adsabs.harvard.edu/abs/2007A%26A...476.1373S
    HZinner2 = (0.68-2.7619e-5*rel_temp-3.8095e-9*rel_temp*rel_temp) *sqrt(luminosity);
    HZouter2 = (1.95-1.3786e-4*rel_temp-1.4286e-9*rel_temp*rel_temp) *sqrt(luminosity);

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
