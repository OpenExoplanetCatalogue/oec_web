#import xml.etree.ElementTree as ET
import lxml.etree as ET
import glob
import os
import time
import urllib
import difflib
import copy
import json
import visualizations
import oec_filters
import datetime
import oec_fields
from bson.objectid import ObjectId
from functools import wraps
#import oec_plots
from numberformat import renderFloat, renderText, notAvailableString
from flask import Flask, abort, render_template, send_from_directory, request, redirect, Response, make_response
#from flask.ext.pymongo import PyMongo
import threading

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
with open(APP_ROOT+"/recaptcha.txt") as f: # read in secret from file.
	content = f.readlines()
captchasecret = "".join(content).strip()
with open(APP_ROOT+"/adminpassword.txt") as f: # read in secret from file.
	content = f.readlines()
adminpassword = "".join(content).strip()


class MyOEC:
    OEC_PATH = APP_ROOT+"/open_exoplanet_catalogue/"
    OEC_META_PATH = APP_ROOT+"/oec_meta/"
    def __init__(self):
        print "Parsing OEC ..."
        self.fullxml = "<systems>\n"
        self.planets = []
        self.systems = []
        self.planetXmlPairs = {}
        self.planetnames = {}

        # Loop over all files and  create new data
        for filename in glob.glob(self.OEC_PATH + "systems/*.xml"):
            # Open file
            f = open(filename, 'rt')
            xml = f.read()
            f.close()
            self.fullxml+=xml
            filename = filename[len(self.OEC_PATH):]
            # Try to parse file
            root = ET.fromstring(xml)
            self.systems.append(root)
            pstars = root.findall("./star")
            for p in root.findall(".//planet"):
                star = None
                parent = p.getparent()
                if parent.tag=="star":
                    star = parent
                xmlPair = (root,p,star,filename)
                self.planets.append(xmlPair)
                name = p.find("./name").text
                self.planetXmlPairs[name] = xmlPair
                for n in p.findall("./name"):
                    self.planetnames[n.text] = name
        self.fullxml += "</systems>\n"

        print "Parsing OEC META ..."
        with open(self.OEC_META_PATH+"statistics.xml", 'rt') as f:
            self.oec_meta_statistics = ET.parse(f).getroot()

        print "Parsing done."



class FlaskApp(Flask):
    def __init__(self, *args, **kwargs):
        super(FlaskApp, self).__init__(*args, **kwargs)
        self.oec = self.getOEC()

    def getOEC(self):
        mydata = threading.local()
        if not hasattr(mydata, "oec"):
            mydata.oec = MyOEC()
        return mydata.oec

app = FlaskApp(__name__)
#try:
#    mongo = PyMongo(app)
#except:
#    print("Mongo DB not correctly initialized.")
mongo = None

def isList(value):
    return isinstance(value, list)
def getFirst(value):
    if isList(value):
        return value[0]
    return value
app.jinja_env.filters['islist'] = isList
app.jinja_env.filters['getFirst'] = getFirst


#################

@app.route('/system.html')
@app.route('/search/')
def page_planet_redirect():
    oec = app.oec
    planetname = request.args.get("id")
    if planetname not in oec.planetXmlPairs:
        if planetname in oec.planetnames:
            planetname = oec.planetnames[planetname]
        else:
            abort(404)

    return redirect("planet/"+planetname, 301)

#################

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and password == adminpassword
def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route('/plot/<plotname>/')
@app.route('/plot/<plotname>')
@app.route('/plot/<plotname>.svg')
def page_plot(plotname):
#    oec = app.oec
#    if plotname=="discoveryyear":
#        return  Response(oec_plots.discoveryyear(oec.oec_meta_statistics),  mimetype='image/svg+xml')
#    if plotname=="skypositions":
#        return  Response(oec_plots.skypositions(oec.systems),  mimetype='image/svg+xml')
    abort(404)

@app.route('/')
@app.route('/index.html')
def page_main():
    oec = app.oec
    contributors = []
    for c in oec.oec_meta_statistics.findall(".//contributor"):
        contributors.append(c.text)
    commitdate = datetime.datetime.fromtimestamp(int(oec.oec_meta_statistics.find(".//lastcommittimestamp").text))

    return render_template("index.html",
            numplanets=len(oec.planets),
            numsystems=int(oec.oec_meta_statistics.find("./systems").text),
            numconfirmedplanets=int(oec.oec_meta_statistics.find("./confirmedplanets").text),
            numbinaries=int(oec.oec_meta_statistics.find("./binaries").text),
            lastupdate=commitdate.strftime("%c"),
            numcommits=int(oec.oec_meta_statistics.find("./commits").text),
            contributors=contributors,
        )


@app.route('/kiosk/')
def page_kiosk():
    oec = app.oec
    commitdate = datetime.datetime.fromtimestamp(int(oec.oec_meta_statistics.find(".//lastcommittimestamp").text))
    data_x = ""
    data_y = ""
    sum_y = 0
    for y in oec.oec_meta_statistics.find("./discoveryyear"):
        data_x += y.tag[1:] + ","
        sum_y+=int(y.text)
        data_y += "%d," % sum_y


    return render_template("kiosk.html",
            numconfirmedplanets=int(oec.oec_meta_statistics.find("./confirmedplanets").text),
            lastupdate=commitdate.strftime("%A, %-d %B %Y, %X"),
            loaddate=time.strftime("%A, %-d %B %Y, %X"),
            discoverynumbers= data_y[:-1],
            discoveryyears= data_x[:-1],
        )

@app.route('/systems/',methods=["POST","GET"])
def page_systems():
    oec = app.oec
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
            if field in oec_fields.titles and field!="namelink":
                fields.append(field)
    else:
        fields += ["mass","radius","massEarth","radiusEarth","numberofplanets","numberofstars"]
    lastfilename = ""
    tablecolour = 0
    for xmlPair in oec.planets:
        if oec_filters.isFiltered(xmlPair,filters):
            continue
        system,planet,star,filename = xmlPair
        if lastfilename!=filename:
            lastfilename = filename
            tablecolour = not tablecolour
        d = {}
        d["fields"] = [tablecolour]
        for field in fields:
            d["fields"].append(oec_fields.render(xmlPair,field,editbutton=False))
        p.append(d)
    return render_template("systems.html",
        columns=[oec_fields.titles[field] for field in fields],
        planets=p,
        available_fields=oec_fields.titles,
        available_filters=oec_filters.titles,
        fields=fields,
        filters=filters,
        debugtxt=debugtxt)


@app.route('/webgl.html')
def page_webgl():
    return render_template("webgl.html")


@app.route('/planet/<planetname>')
@app.route('/planet/<planetname>/')
@app.route('/system/<planetname>/')
def page_planet(planetname):
    oec = app.oec
    try:
        xmlPair = oec.planetXmlPairs[planetname]
    except:
        abort(404)
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
        if len(set(rowdata)) <= 1 and row!="name" and rowdata[0]!=notAvailableString: # all fields identical:
            rowdata = rowdata[0]
        planettable.append(rowdata)

    startable = []
    startablefields = []
    for row in ["starname","staralternativenames","starmass","starradius","starage","starmetallicity","startemperature","starspectraltype","starmagV"]:
        startablefields.append(oec_fields.titles[row])
        rowdata = []
        for s in stars:
            rowdata.append(oec_fields.render((system,planet,s,filename),row))
        if len(set(rowdata)) <= 1 and row!="starname" and rowdata[0]!=notAvailableString: # all fields identical:
            rowdata = rowdata[0]
        startable.append(rowdata)

    references = []
    contributors = []
    try:
        with open(oec.OEC_META_PATH+filename, 'rt') as f:
            root = ET.parse(f).getroot()
            for l in root.findall(".//link"):
                references.append(l.text)
            for c in root.findall(".//contributor"):
                contributors.append((c.attrib["commits"],c.attrib["email"],c.text))
    except IOError:
        pass

    vizsize = visualizations.size(xmlPair)
    vizhabitable = visualizations.habitable(xmlPair)
    vizarchitecture = visualizations.textArchitecture(system)


    return render_template("planet.html",
        system=system,
        planet=planet,
        filename=filename,
        planetname=planetname,
        vizsize=vizsize,
        vizhabitable=vizhabitable,
        architecture=vizarchitecture,
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

def getAttribText(o,a):
    if a in o.attrib:
        return o.attrib[a]
    else:
        return ""

# form disabled
#@app.route('/edit/form/<path:fullpath>')
def page_planet_edit_form(fullpath):
    path = fullpath.split(".xml/")
    if len(path)!=2:
        abort(404)
    urlfilename = path[0]+".xml"
    xmlpath = path[1]
    oec = app.oec
    for key in oec.planetXmlPairs:
        system,planet,star,filename = oec.planetXmlPairs[key]
        if filename==urlfilename:
            break
    if filename!=urlfilename:
        abort(404)
    planetname = planet.find("./name").text
    o = system.find(xmlpath)
    title = ""
    tag = o.tag
    if o.getparent().tag == "star":
        tag = "star"+tag
    if tag in oec_fields.titles:
        title = oec_fields.titles[tag]
    if tag in ["description"]:
        # Text
        return render_template("edit_form_text.html",
            title=title,
            value=o.text,
            filename=filename,
            xmlpath=xmlpath,
            )
    # Default float
    return render_template("edit_form_float.html",
        title=title,
        value=o.text,
        filename=filename,
        errorminus=getAttribText(o,"errorminus"),
        errorplus=getAttribText(o,"errorplus"),
        lowerlimit=getAttribText(o,"lowerlimit"),
        upperlimit=getAttribText(o,"upperlimit"),
        xmlpath=xmlpath,
        )

# Nicely indents the XML output
def indent(elem, level=0):
    i = "\n" + level * "\t"
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "\t"
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


# form disabled
#@app.route('/edit/submit/<path:fullpath>',methods=["POST"])
def page_planet_edit_submit(fullpath):
    path = fullpath.split(".xml/")
    if len(path)!=2:
        abort(404)
    urlfilename = path[0]+".xml"
    xmlpath = path[1]

    if "g-recaptcha-response" not in request.form:
        return json.dumps({'success': False, 'message': "Captcha failed. Please try again."})
    url = "https://www.google.com/recaptcha/api/siteverify?secret="+captchasecret+"&response="+request.form["g-recaptcha-response"]+""
    captcharesponse = json.load(urllib.urlopen(url))
    if captcharesponse["success"]!=True:
        return json.dumps({'success': False, 'message': "Captcha failed. Please try again."})
    if len(request.form["name"])<2:
        return json.dumps({'success': False, 'message': "Please enter your name."})
    if len(request.form["paper"])<10:
        return json.dumps({'success': False, 'message': "Please enter a valid link to a scientific publication."})




    oec = app.oec
    for key in oec.planetXmlPairs:
        system,planet,star,filename = oec.planetXmlPairs[key]
        if filename==urlfilename:
            break
    if filename!=urlfilename:
        return json.dumps({'success': False, 'message': "Cannot find system."})
    new_system = copy.deepcopy(system)
    o = new_system.find(xmlpath)

    tag = o.tag
    if o.getparent().tag == "star":
        tag = "star"+tag
    if tag in ["desription"]:
        # Text
        if "value" in request.form:
            o.text = request.form["value"]
    else:
        # Float
        attribs = ["errorplus", "errorminus","upperlimit", "lowerlimit"]
        for attrib in attribs:
            if attrib in request.form:
                newv = request.form[attrib]
                if len(newv)==0:
                    if attrib in o.attrib:
                        o.attrib.pop(attrib)
                else:
                    o.attrib[attrib] = newv
        if "value" in request.form:
            o.text = request.form["value"]


    indent(new_system)
    diff = difflib.unified_diff(
            ET.tostring(system, encoding="UTF-8", xml_declaration=False).strip().split("\n"),
            ET.tostring(new_system, encoding="UTF-8", xml_declaration=False).strip().split("\n"),
            fromfile=filename,
            tofile=filename,
            lineterm='')


    # Just for testing. Needs a proper backend.
    d = {}
    d["patch"]  = '\n'.join(diff)
    d["paper"]  = request.form["paper"]
    d["name"]   = request.form["name"]
    d["ip"]     = request.remote_addr
    d["date"]   = time.time()

    mongo.db.edits.insert(d)

    return json.dumps({'success': True, 'message': "Thanks for your contribution. We're checking your commit now."})


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
    oec = app.oec
    return oec.fullxml

@app.route('/robots.txt')
def page_robots_txt():
    return "User-agent: *\nDisallow:\n"

@app.route('/edits/',methods=["POST","GET"])
@requires_auth
def page_edits():
    if "approve" in request.form:
        edit = mongo.db.edits.find_one( {"_id": ObjectId(request.form["approve"])} )
        response = make_response(edit["patch"])
        response.headers["Content-Disposition"] = "attachment; filename=oec.patch"
        response.headers["Content-Type"] = "application/patch"
        return response
    else:
        if "delete" in request.form:
            print mongo.db.edits.remove( {"_id": ObjectId(request.form["delete"])} )
        edits = mongo.db.edits.find()
        return render_template("edits.html",
            edits=edits,
            )

if __name__ == '__main__':
    app.run(debug=True,threaded=True)
