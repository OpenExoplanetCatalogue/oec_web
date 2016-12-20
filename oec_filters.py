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

spectraltypes_temp_radii = {'O' : (40000,10.) , 'B': (20000,3.0), 'A' : (8500, 1.5), 'F' : (6500, 1.3), 'G' : (5500, 1.0), 'K': (4000, 0.8) , 'M' : (3000, 0.5) }

def isHabitable(xmlPair):
    system, planet, star, filename = xmlPair
    maxa = 0
    if star is None:
        return False # no binary systems (yet)
    spectralTypeMain = getText(star,"./spectraltype","G")[0]
    if spectralTypeMain not in spectraltypes_temp_radii :
        return False # unsupported spectral type 
    semimajoraxis = getFloat(planet,"./semimajoraxis")
    if semimajoraxis is None:
        hostmass = getFloat(star,"./mass",1.)
        period = getFloat(planet,"./period",265.25)
        semimajoraxis = pow(pow(period/6.283/365.25,2)*39.49/hostmass,1.0/3.0)

    temperature = getFloat(star,"./temperature")

    if temperature is None:
        temperature = spectraltypes_temp_radii[spectralTypeMain][0]

    rel_temp = temperature - 5700.

    stellarMass = getFloat(star,"./mass")
    if stellarMass is None:
        stellarMass = 1.

    stellarRadius = getFloat(star,"./radius")
    if stellarRadius is None or stellarRadius<0.01:
        stellarRadius = 1.
        if spectralTypeMain in spectraltypes_temp_radii:
            stellarRadius = spectraltypes_temp_radii[spectralTypeMain][1]


    if stellarMass>2.:
        luminosity = pow(stellarMass,3.5)
    else:
        luminosity = pow(stellarMass,4.)

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
