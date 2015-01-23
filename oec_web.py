import xml.etree.ElementTree as ET
import glob
from numberformat import renderFloat
from flask import Flask, abort, render_template


OEC_PATH = "open_exoplanet_catalogue/"

print "Parsing OEC ..."
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

def render(xmlPair,type):
    system, planet = xmlPair
    if type=="numberofplanets":
        return "%d"%len(system.findall(".//planet"))
    try:
        return renderFloat(planet.find("./"+type))
    except:
        pass

    return ""

app = Flask(__name__)
@app.route('/')
@app.route('/index.html')
def main_page():
    return render_template("index.html")

@app.route('/systems/')
def systems():
    p = []
    for xmlPair in planets:
        d = {}
        try:
            name = xmlPair[1].find("./name").text
        except:
            name = "None"
        d["name"] = name 
        f = []
        f.append(render(xmlPair,"mass"))
        f.append(render(xmlPair,"radius"))
        f.append(render(xmlPair,"numberofplanets"))
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
