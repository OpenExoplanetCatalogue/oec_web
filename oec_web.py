import xml.etree.ElementTree as ET
import glob
from flask import Flask, abort


OEC_PATH = "open_exoplanet_catalogue/"

print "Parsing OEC ..."
planet_names = {}

# Loop over all files and  create new data
for filename in glob.glob(OEC_PATH + "systems/*.xml"):
    # Open file
    f = open(filename, 'rt')

    # Try to parse file
    try:
        root = ET.parse(f).getroot()
        planets = root.findall(".//planet")
        stars = root.findall(".//star")
        binaries = root.findall(".//binary")
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
def hello_world():
    return 'Hello World!'

@app.route('/planet/<planetname>')
def hello_planet(planetname):
    try:
        with open(planet_names[planetname],'r') as f:
            return f.read()
    except KeyError, e:
        abort(404)
    abort(404)


if __name__ == '__main__':
    app.run()
