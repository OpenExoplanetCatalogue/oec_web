import xml.etree.ElementTree as ET
import glob
import os
import urllib
import visualizations 
import oec_filters
import oec_fields
from numberformat import renderFloat, renderText, notAvailableString
from flask import Flask, abort, render_template, send_from_directory, request

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
OEC_PATH = APP_ROOT+"/open_exoplanet_catalogue/"
OEC_META_PATH = APP_ROOT+"/oec_meta/"

print "Parsing OEC ..."
fullxml = "<systems>\n"
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
    xml = f.read()
    f.close()
    fullxml+=xml
    filename = filename[len(OEC_PATH):]
    # Try to parse file
    root = ET.fromstring(xml)
    numsystems +=1
    pstars = root.findall("./star")
    for p in root.findall(".//planet"):
        for l in p.findall("./list"):
            if l.text == "Confirmed planets":
                numconfirmedplanets += 1
        star = None
        for s in pstars:
            if p in s:
                star = s
                break
        xmlPair = (root,p,star,filename)
        planets.append(xmlPair)
        name = p.find("./name").text
        planetXmlPairs[name] = xmlPair
    systemXmlPairs[root.find("./name").text] = (root,None,filename)
    stars += pstars
    binaries += root.findall(".//binary")
fullxml += "</systems>\n"

print "Parsing OEC META ..."
with open(OEC_META_PATH+"statistics.xml", 'rt') as f:
    oec_meta_statistics = ET.parse(f).getroot()

app = Flask(__name__)
def is_list(value):
    return isinstance(value, list)
app.jinja_env.filters['islist'] = is_list


@app.route('/open_exoplanet_catalogue/<path:filename>')
def static_oec(filename):
    return send_from_directory('open_exoplanet_catalogue', filename)

@app.route('/oec_meta/<path:filename>')
def static_oec_meta(filename):
    return send_from_directory('oec_meta', filename)

@app.route('/oec_outreach/<path:filename>')
def static_oec_outreach(filename):
    return send_from_directory('oec_outreach', filename)


@app.route('/')
@app.route('/index.html')
def page_main():
    contributors = []
    for c in oec_meta_statistics.findall(".//contributor"):
        contributors.append(c.text)
    return render_template("index.html",
            numplanets=len(planets),
            numsystems=numsystems,
            numconfirmedplanets=numconfirmedplanets,
            numbinaries=len(binaries),
            numcommits=int(oec_meta_statistics.find("./commits").text),
            contributors=contributors,
        )

@app.route('/systems/',methods=["POST","GET"])
def page_systems():
    p = []
    debugtxt = ""
    fields = ["namelink"]
    filters = []
    if "filters" in request.args:
        listfilters = request.args.getlist("filters")
        for filter in listfilters:
            if filter in oec_filters.titles:
                filters.append(filter) 
    if "fields" in request.args:
        listfields = request.args.getlist("fields")
        for field in listfields:
            if field in oec_fields.titles:
                fields.append(field) 
    else:
        fields += ["mass","radius","massEarth","radiusEarth","numberofplanets","numberofstars"]
    lastfilename = ""
    tablecolour = 0
    for xmlPair in planets:
        if oec_filters.isFiltered(xmlPair,filters):
            continue
        system,planet,star,filename = xmlPair
        if lastfilename!=filename:
            lastfilename = filename
            tablecolour = not tablecolour
        d = {}
        d["fields"] = [tablecolour]
        for field in fields:
            d["fields"].append(oec_fields.render(xmlPair,field))
        p.append(d)
    return render_template("systems.html",
        columns=[oec_fields.titles[field] for field in fields],
        planets=p,
        available_fields=oec_fields.titles,
        available_filters=oec_filters.titles,
        fields=fields,
        filters=filters,
        debugtxt=debugtxt)


@app.route('/planet/<planetname>')
@app.route('/planet/<planetname>/')
def page_planet(planetname):
    xmlPair = planetXmlPairs[planetname]
    system,planet,star,filename = xmlPair
    planets=system.findall(".//planet")
    stars=system.findall(".//star")

    systemtable = []
    for row in ["systemname","systemalternativenames","rightascension","declination","distance","distancelightyears","numberofstars","numberofplanets"]:
        systemtable.append((oec_fields.titles[row],oec_fields.render(xmlPair,row)))
    
    planettable = []
    planettablefields = []
    for row in ["name","alternativenames","description","lists","mass","massEarth","radius","radiusEarth","period","semimajoraxis","eccentricity","temperature","discoverymethod","discoveryyear","lastupdate"]:
        planettablefields.append(oec_fields.titles[row])
        rowdata = []
        for p in planets:
            rowdata.append(oec_fields.render((system,p,star,filename),row))
        if len(set(rowdata)) <= 1: # all fields identical:
            rowdata = rowdata[0]
        planettable.append(rowdata)
    
    startable = []
    startablefields = []
    for row in ["starname","staralternativenames","starmass","starradius","starage","starmetallicity","startemperature","starspectraltype","starvisualmagnitude"]:
        startablefields.append(oec_fields.titles[row])
        rowdata = []
        for s in stars:
            rowdata.append(oec_fields.render((system,planet,s,filename),row))
        if len(set(rowdata)) <= 1: # all fields identical:
            rowdata = rowdata[0]
        startable.append(rowdata)

    references = []
    contributors = []
    with open(OEC_META_PATH+filename, 'rt') as f:
        root = ET.parse(f).getroot()
        for l in root.findall(".//link"):
            references.append(l.text) 
        for c in root.findall(".//contributor"):
            contributors.append((c.attrib["commits"],c.attrib["email"],c.text)) 

    vizsize = visualizations.size(xmlPair)
    vizhabitable = visualizations.habitable(xmlPair)

    return render_template("planet.html",
        system=system,
        planet=planet,
        filename=filename,
        planetname=planetname,
        vizsize=vizsize,
        vizhabitable=vizhabitable,
        systemname=oec_fields.render(xmlPair,"systemname"),
        systemtable=systemtable,
        image=(oec_fields.render(xmlPair,"image"),oec_fields.render(xmlPair,"imagedescription")),
        planettablefields=planettablefields,
        planettable=planettable,
        startablefields=startablefields,
        startable=startable,
        references=references,
        contributors=contributors,
        systemcategory=oec_fields.render(xmlPair,"systemcategory"),
        )

@app.route('/correlations/')
@app.route('/correlations.html')
def page_correlations():
    return render_template("correlations.html")

@app.route('/histogram/')
@app.route('/histogram.html')
def page_histogram():
    return render_template("histogram.html",)

@app.route('/systems.xml')
def page_systems_xml():
    return fullxml

#abort(404)
# Implement later
#@app.route('/system/<systemname>')
#@app.route('/system/<systemname>/')
#def page_system(systemname):
#    xmlPair = systemXmlPairs[systemname]
#    system,planet,filename = xmlPair
#    
#    systemtable = []
#    for row in ["systemname","systemalternativenames","rightascension","declination","distance","distancelightyears","numberofstars","numberofplanets"]:
#        systemtable.append((fieldtitles[row],render(xmlPair,row)))
#
#    return render_template("system.html",
#        systemname=render(xmlPair,"systemname"),
#        systemtable=systemtable,
#        systemcategory=render(xmlPair,"systemcategory"),
#        )

if __name__ == '__main__':
    app.run(debug=True)
