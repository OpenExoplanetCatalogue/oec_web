import xml.etree.ElementTree as ET
import glob
import numberformat
from flask import Flask, abort, render_template
from math import *


OEC_PATH = "open_exoplanet_catalogue/"

print "Parsing OEC ..."
planet_names = {}
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
        planets += root.findall(".//planet")
        stars += root.findall(".//star")
        binaries += root.findall(".//binary")
    except ET.ParseError as error:
        print '{}, {}'.format(filename, error)
        continue
    finally:
        f.close()

    for planet in planets:
        names = planet.findall("./name")
        for name in names:
            planet_names[name.text] = filename

print "Parsing OEC done"


app = Flask(__name__)
@app.route('/')
@app.route('/index.html')
def main_page():
    return render_template("index.html")

@app.route('/systems/')
def systems():
    p = []
    for planet in planets:
        d = {}
        try:
            name = planet.find("./name").text
        except:
            name = "None"
        d["name"] = name 
        f = []
        mass = renderFloat(planet.find("./mass"))
        f.append(mass)
        d["fields"] = f
        p.append(d)
    return render_template("systems.html",planets=p)


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
