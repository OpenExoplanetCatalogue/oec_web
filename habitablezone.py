from numberformat import getFloat, getText
from math import *

spectralTypeTempRadius = {
    "O": (40000., 10.),
    "B": (20000., 3.0),
    "A": (8500., 1.5),
    "F": (6500., 1.3),
    "G": (5500., 1.0),
    "K": (4000., 0.8),
    "M": (3000., 0.5)
}

def hzLimits(xmlPair):
    system, planet, star, filename = xmlPair
    if star is None:
        return None

    temperature = getFloat(star,"./temperature")
    stellarRadius = getFloat(star,"./radius")
    if temperature is not None and stellarRadius is not None:
        if stellarRadius < 0.01:
            # no habitable zone for pulsars
            return None
        luminosity = (temperature/5778.)**4 * stellarRadius**2
    else:
        stellarMass = getFloat(star,"./mass")
        if stellarMass is None:
            return None
        elif stellarMass>2.:
            luminosity = pow(stellarMass,3.5)
        else:
            luminosity = pow(stellarMass,4.)

    spectralTypeMain = getText(star,"./spectraltype","")[:1]
    try:
        spTemperature, spRadius = spectralTypeTempRadius[spectralTypeMain]
        if temperature is None:
            temperature = spTemperature
        if stellarRadius is None:
            stellarRadius = spRadius
    except KeyError:
        if temperature is None:
            temperature = 5700.
        if stellarRadius is None:
            stellarRadius = 1.

    rel_temp = temperature - 5700.

    # Ref: http://adsabs.harvard.edu/abs/2007A%26A...476.1373S
    HZinner2 = (0.68-2.7619e-5*rel_temp-3.8095e-9*rel_temp*rel_temp) *sqrt(luminosity);
    HZinner = (0.95-2.7619e-5*rel_temp-3.8095e-9*rel_temp*rel_temp) *sqrt(luminosity);
    HZouter = (1.67-1.3786e-4*rel_temp-1.4286e-9*rel_temp*rel_temp) *sqrt(luminosity);
    HZouter2 = (1.95-1.3786e-4*rel_temp-1.4286e-9*rel_temp*rel_temp) *sqrt(luminosity);

    return HZinner2, HZinner, HZouter, HZouter2, stellarRadius
