
titles = {
    "confirmed":                    "Only confirmed planets",
    "multiplanet":                  "Only multi-planetary systems",
    "multistar":                    "Only multi-star systems",
    "nomultistar":                  "No multi-star systems",
    "transiting":                   "Only transiting planets",
    "discoveryrv":                  "Planets discovered by RV",
}

def isFiltered(xmlPair,filters):
    system, planet, filename = xmlPair
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
    return False
