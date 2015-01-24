import xml.etree.ElementTree as ET
import glob
import urllib
from numberformat import renderFloat, renderText, notAvailableString
from flask import Flask, abort, render_template, send_from_directory


OEC_PATH = "open_exoplanet_catalogue/"
OEC_META_PATH = "oec_meta/"

print "Parsing OEC ..."
numconfirmedplanets = 0
numsystems = 0
planets = []
stars = []
binaries = []
planetXmlPairs = {}
systemXmlPairs = {}

# Loop over all files and  create new data
for filename in glob.glob(OEC_PATH + "systems/*.xml"):
    # Open file
    f = open(filename, 'rt')
    filename = filename[len(OEC_PATH):]
    # Try to parse file
    try:
        root = ET.parse(f).getroot()
        numsystems +=1
        for p in root.findall(".//planet"):
            for l in p.findall("./list"):
                if l.text == "Confirmed planets":
                    numconfirmedplanets += 1
            planets.append((root,p,filename))
            name = p.find("./name").text
            planetXmlPairs[name] = (root,p,filename)
        systemXmlPairs[root.find("./name").text] = (root,None,filename)
        stars += root.findall(".//star")
        binaries += root.findall(".//binary")
    except ET.ParseError as error:
        print '{}, {}'.format(filename, error)
        continue
    finally:
        f.close()

print "Parsing OEC done"

""" Array of title of propoerties """
title = {
    "name":                         "Primary planet name",
    "alternativenames":             "Alternative planet names",
    "starname":                     "Star name",
    "staralternativenames":         "Alternative star names",
    "systemname":                   "Primary system name",
    "systemalternativenames":       "Alternative system names",
    "distance":                     "Distance [parsec]",
    "distancelightyears":           "Distance [lightyears]",
    "numberofplanets":              "Number of planets in system",
    "numberofstars":                "Number of stars in system",
    "rightascension":               "Right ascension",
    "declination":                  "Declination",
    "image":                        "Image",
    "starmass":                     "Mass [M<sub>Sun</sub>]",
    "starradius":                   "Radius [R<sub>Sun</sub>]",
    "starage":                      "Age [Gyr]",
    "starmetallicity":              "Metallicity [Fe/H]",
    "starspectraltype":             "Spectral type",
    "startemperature":              "Temperature [K]",
    "starvisualmagnitude":          "Visual magnitude",
    "period":                       "Orbital period [days]",
    "semimajoraxis":                "Semi-major axis [AU]",
    "eccentricity":                 "Eccentricity",
    "temperature":                  "Equilibrium temperature [K]",
    "lists":                        "Lists",
    "description":                  "Description",
    "discoveryyear":                "Discovery year",
    "discoverymethod":              "Discovery method",
    "lastupdate":                   "Last updated [yy/mm/dd]",
    "mass":                         "Mass [M<sub>jup</sub>]",
    "radius":                       "Radius [R<sub>jup</sub>]",
    "massEarth":                    "Mass [M<sub>earth</sub>]",
    "radiusEarth":                  "Radius [R<sub>earth</sub>]"
}

def render(xmlPair,type):
    system, planet, filename = xmlPair
    if type=="numberofplanets":
        return "%d"%len(system.findall(".//planet"))
    if type=="numberofstars":
        return "%d"%len(system.findall(".//star"))
    if type=="distance":
        return renderFloat(system.find("./distance"))
    if type=="distancelightyears":
        return renderFloat(system.find("./distance"),3.2615638)
    if type=="massEarth":
        return renderFloat(planet.find("./mass"),317.8942)
    if type=="radiusEarth":
        return renderFloat(planet.find("./radius"),10.973299)
    # Text based object
    if type=="rightascension":
        return renderText(system.find("./rightascension"))
    if type=="declination":
        return renderText(system.find("./declination"))
    if type=="image":
        return renderText(planet.find("./image"))
    if type=="description":
        return renderText(planet.find("./description"))
    if type=="name":
        return renderText(planet.find("./name"))
    if type=="discoveryyear":
        return renderText(planet.find("./discoveryyear"))
    if type=="discoverymethod":
        return renderText(planet.find("./discoverymethod"))
    if type=="lastupdate":
        return renderText(planet.find("./lastupdate"))
    if type=="systemname":
        return renderText(system.find("./name"))
    if type=="alternativenames":
        alternativenames = notAvailableString 
        names = planet.findall("./name")
        for i,name in enumerate(names[1:]):
            if i==0:
                alternativenames = ""
            else:
                alternativenames += ", "
            alternativenames += name.text
        return alternativenames
    if type=="systemalternativenames":
        systemalternativenames = notAvailableString 
        systemnames = system.findall("./name")
        for i,name in enumerate(systemnames[1:]):
            if i==0:
                systemalternativenames = ""
            else:
                systemalternativenames += ", "
            systemalternativenames += name.text
        return systemalternativenames
    if type=="lists":
        lists = notAvailableString 
        ls = planet.findall("./list")
        for i,l in enumerate(ls):
            if i==0:
                lists = ""
            else:
                lists += "; "
            lists += l.text
        return lists
    # Host star fields
    if type[0:4]=="star":
        stars = system.findall("./star")
        star = None
        for s in stars:
            if planet in s:
                star = s
                break
        if star is None:
            return notAvailableString
        type = type[4:]
        # Text based object
        if type=="spectraltype":
            return renderText(star.find("./spectraltype"))
        if type=="name":
            return renderText(star.find("./name"))
        if type=="alternativenames":
            alternativenames = notAvailableString 
            names = star.findall("./name")
            for i,name in enumerate(names[1:]):
                if i==0:
                    alternativenames = ""
                else:
                    alternativenames += ", "
                alternativenames += name.text
            return alternativenames
        # Default: just search for the property in the planet xml. 
        return renderFloat(star.find("./"+type))
    # Long texts
    if type=="systemcategory":
        systemcategory = ""
        systemname = renderText(system.find("./name"))
        if len(system.findall(".//planet"))==1:
            systemcategory += "The planetary system "+systemname+" hosts at least one planet. "
        elif len(system.findall(".//planet"))>1:
            systemcategory += "The planetary system "+systemname+" hosts at least %d planets. " % len(system.findall(".//planet"))
        if len(system.findall(".//star"))>1:
            systemcategory += "Note that the system is a multiple star system. It hosts at least %d stellar components. "% len(system.findall(".//star"))
        elif len(system.findall(".//star"))==0:
            systemcategory += "The planet is a so called orphan planet and not associated with any star. "
        return systemcategory

    # Default: just search for the property in the planet xml. 
    return renderFloat(planet.find("./"+type))

app = Flask(__name__)

@app.route('/open_exoplanet_catalogue/<path:filename>')
def static_oec(filename):
    return send_from_directory('open_exoplanet_catalogue', filename)

@app.route('/oec_meta/<path:filename>')
def static_oec_meta(filename):
    return send_from_directory('oec_meta', filename)

@app.route('/')
@app.route('/index.html')
def page_main():
    return render_template("index.html",
            numplanets=len(planets),
            numsystems=numsystems,
            numconfirmedplanets=numconfirmedplanets,
            numbinaries=len(binaries),
        )

@app.route('/systems/')
def page_systems():
    p = []
    fields = ["systemname","name","mass","radius","massEarth","radiusEarth","numberofplanets","numberofstars"]
    lastfilename = ""
    for xmlPair in planets:
        system,planet,filename = xmlPair
        systemname = "&nbsp;"
        if lastfilename!=filename:
            lastfilename = filename
            systemname = render(xmlPair,"systemname")
            systemname = "<a href=\"/system/%s/\">%s</a>"%(urllib.quote(systemname),systemname)
        d = {}
        planetname = render(xmlPair,"name")
        d["fields"] = [systemname,"<a href=\"/planet/%s/\">%s</a>"%(urllib.quote(planetname),planetname)]
        for field in fields[2:]:
            d["fields"].append(render(xmlPair,field))
        p.append(d)
    return render_template("systems.html",columns=[title[field] for field in fields],planets=p)


@app.route('/planet/<planetname>')
@app.route('/planet/<planetname>/')
def page_planet(planetname):
    xmlPair = planetXmlPairs[planetname]
    system,planet,filename = xmlPair

    systemtable = []
    for row in ["systemname","systemalternativenames","rightascension","declination","distance","distancelightyears","numberofstars","numberofplanets"]:
        systemtable.append((title[row],render(xmlPair,row)))
    
    planettable = []
    for row in ["name","alternativenames","description","lists","mass","massEarth","radius","radiusEarth","period","semimajoraxis","eccentricity","temperature","discoverymethod","discoveryyear","lastupdate"]:
        planettable.append((title[row],render(xmlPair,row)))
    
    startable = []
    for row in ["starname","staralternativenames","starmass","starradius","starage","starmetallicity","startemperature","starspectraltype","starvisualmagnitude"]:
        startable.append((title[row],render(xmlPair,row)))

    references = []
    contributors = []
    with open(OEC_META_PATH+filename, 'rt') as f:
        root = ET.parse(f).getroot()
        for l in root.findall(".//link"):
            references.append(l.text) 
        for c in root.findall(".//contributor"):
            contributors.append((c.attrib["commits"],c.attrib["email"],c.text)) 


    return render_template("planet.html",
        planetname=planetname,
        systemname=render(xmlPair,"systemname"),
        systemtable=systemtable,
        planettable=planettable,
        startable=startable,
        filename=filename,
        references=references,
        contributors=contributors,
        systemcategory=render(xmlPair,"systemcategory"),
        )
    #abort(404)

@app.route('/system/<systemname>')
@app.route('/system/<systemname>/')
def page_system(systemname):
    xmlPair = systemXmlPairs[systemname]
    system,planet,filename = xmlPair
    
    systemtable = []
    for row in ["systemname","systemalternativenames","rightascension","declination","distance","distancelightyears","numberofstars","numberofplanets"]:
        systemtable.append((title[row],render(xmlPair,row)))

    return render_template("system.html",
        systemname=render(xmlPair,"systemname"),
        systemtable=systemtable,
        systemcategory=render(xmlPair,"systemcategory"),
        )

if __name__ == '__main__':
    app.run(debug=True)
