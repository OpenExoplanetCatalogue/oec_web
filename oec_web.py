import xml.etree.ElementTree as ET
import glob
from numberformat import renderFloat
from flask import Flask, abort, render_template


OEC_PATH = "open_exoplanet_catalogue/"

print "Parsing OEC ..."
systems = []
planets = []
stars = []
binaries = []

# Loop over all files and  create new data
for filename in glob.glob(OEC_PATH + "systems/*.xml"):
    # Open file
    f = open(filename, 'rt')
    # Try to parse file
    try:
        root = ET.parse(f).getroot()
        systems += root
        for p in root.findall(".//planet"):
            planets.append((root,p))
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
    "name":             "Primary planet name",
    "numberofplanets":  "Number of planets in system",
    "numberofstars":    "Number of stars in system",
    "mass":             "Mass [M<sub>jup</sub>]",
    "radius":           "Radius [R<sub>jup</sub>]",
    "massEarth":        "Mass [M<sub>earth</sub>]",
    "radiusEarth":      "Radius [R<sub>earth</sub>]"
}

def render(xmlPair,type):
    system, planet = xmlPair
    if type=="numberofplanets":
        return "%d"%len(system.findall(".//planet"))
    if type=="numberofstars":
        return "%d"%len(system.findall(".//star"))
    if type=="name":
        return planet.find("./name").text
    if type=="massEarth":
        return renderFloat(planet.find("./mass"),317.8942)
    if type=="radiusEarth":
        return renderFloat(planet.find("./radius"),10.973299)
    # Default: just search for the property in the planet xml. 
    return renderFloat(planet.find("./"+type))

app = Flask(__name__)
@app.route('/')
@app.route('/index.html')
def main_page():
    return render_template("index.html")

@app.route('/systems/')
def systems():
    p = []
    fields = ["name","mass","radius","massEarth","radiusEarth","numberofplanets","numberofstars"]
    for xmlPair in planets:
        system,planet = xmlPair
        d = {}
        d["fields"] = []
        for field in fields:
            d["fields"].append(render(xmlPair,field))
        p.append(d)
    return render_template("systems.html",columns=[title[field] for field in fields],planets=p)


@app.route('/planet/<planetname>')
def hello_planet(planetname):
    try:
        with open(planet_names[planetname],'r') as f:
            return f.read()
    except KeyError, e:
        abort(404)
    abort(404)


if __name__ == '__main__':
    app.run(debug=True)
