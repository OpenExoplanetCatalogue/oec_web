from math import *
from numberformat import getFloat, getText, renderFloat
from habitablezone import hzLimits

width = 480
height= 200

def getRadius(planet):
    radius = getFloat(planet,"./radius")
    if radius is not None:
        return radius
    m = getFloat(planet,"./mass")
    if m is not None:
        m *= 317.894
        # This is based on Lissauer et al 2011 b
        if m>30.:
            return pow(m,1./3.)*0.0911302
        else:
            return pow(m,1./2.06)*0.0911302
    return None

pl_i=0
texty = 0.
space=10
earth = 1.
def plotplanet(radius,name,ss,todooooooo=1):
    global earth,pl_i,texty
    svg = ""
    size= 12
    textx=pl_i+2
    texty+=size+3
    if ss:
        y= height*3.0/2.0
    else:
        y= height*0.5

    if ss:
        style = "fill:url(#g2); stroke:none"
    else:
        if True:
            style = "fill:url(#g3); stroke:none"
        else:
            style = "fill:url(#g1); stroke:none"
    svg += '<circle cx="%f" cy="%f" r="%f" style="%s" />' %(
                pl_i+earth*radius+1,
                y,
                earth*radius,
                style)
    svg += '<line x1="%f" y1="%f" x2="%f" y2="%f" fill="none" stroke="lightgrey" />'%(
                textx,
                texty-size/2,
                textx,
                y)
    svg += '<text x="%f" y="%f" font-family="sans-serif" font-weight="normal"  font-size="%f" stroke="none" >%s</text>' %(
                textx,
                texty,
                size,
                name)
    pl_i += 2*earth*radius+2+space
    return svg

def size(xmlPair):
    global earth,pl_i,texty
    system, planet, star, filename = xmlPair
    planets = system.findall(".//planet")
    maxr = max(map(getRadius,planets))
    pl_i=0
    textx=0

    if maxr<=0.:
        return None

    earth     = 1.0/ maxr*height*0.4
    if space*8+earth*2.8257378 *2 > width:
        earth = (width - (space+2)*8 )/ (2.8257378 * 2.0  )


    svg = """
        <defs>
        <radialGradient id = "g1" cx = "50%" cy = "50%" r = "50%">
            <stop style="stop-color:rgb(20,20,20);" offset = "0%"/>
            <stop style="stop-color:rgb(100,100,100);" offset = "95%"/>
            <stop style="stop-color:rgb(250,250,250);" offset = "100%"/>
            </radialGradient>
        <radialGradient id = "g2" cx = "50%" cy = "50%" r = "50%">
            <stop style="stop-color:rgb(120,120,120);" offset = "0%"/>
            <stop style="stop-color:rgb(180,180,180);" offset = "95%"/>
            <stop style="stop-color:rgb(252,252,252);" offset = "100%"/>
            </radialGradient>
        <radialGradient id = "g3" cx = "50%" cy = "50%" r = "50%">
            <stop style="stop-color:rgb(120,80,80);" offset = "0%"/>
            <stop style="stop-color:rgb(180,100,100);" offset = "95%"/>
            <stop style="stop-color:rgb(252,202,202);" offset = "100%"/>
            </radialGradient>
        </defs>
        <g style="stroke:black;">
    """
    texty=height
    pl_i=0
    svg += plotplanet(    1160.0/71490.0, "Pluto" ,     True, 0)
    svg += plotplanet(    2439.0/71490.0, "Mercury" ,   True, 1)
    svg += plotplanet(    3397.0/71490.0, "Mars" ,      True, 2)
    svg += plotplanet(    6052.0/71490.0, "Venus" ,     True, 3)
    svg += plotplanet(    6378.0/71490.0, "Earth" ,     True, 4)
    svg += plotplanet(   25269.0/71490.0, "Neptune" ,   True, 5)
    svg += plotplanet(   25559.0/71490.0, "Uranus" ,    True, 6)
    svg += plotplanet(   60268.0/71490.0, "Saturn"  ,   True, 7)
    svg += plotplanet(   71490.0/71490.0, "Jupiter" ,   True, 8)
    texty=0.0
    pl_i=0
    for p in planets:
        radius = getRadius(p)
        if radius is not None:
            svg += plotplanet(radius, p.find("./name").text, False)

    svg += " </g>"
    return svg


def habitable(xmlPair):
    system, planet, star, filename = xmlPair

    stars = system.findall(".//star[planet]") # no binary systems yet
    visualizations = []
    for star in stars:
        hzdata = hzLimits(star)
        if hzdata is None:
            continue

        HZinner2, HZinner, HZouter, HZouter2, stellarRadius = hzdata

        planets = star.findall("./planet")

        maxa = 0
        for planet in planets:
            semimajoraxis = getFloat(planet,"./semimajoraxis")
            if semimajoraxis is None:
                hostmass = getFloat(star,"./mass",1.)
                period = getFloat(planet,"./period",265.25)
                semimajoraxis = pow(pow(period/6.283/365.25,2)*39.49/hostmass,1.0/3.0)
            if semimajoraxis>maxa:
                maxa = semimajoraxis

        width = 600
        height= 100
        au     = 2.0/ maxa*(width-100)*0.49
        last_text_y=12

        svg = """
            <defs>
                <radialGradient id="habitablegradient" >
                    <stop id="stops0" offset=".0" stop-color="lightgreen" stop-opacity="0"/>
                    <stop id="stops1" offset="%f" stop-color="lightgreen" stop-opacity="0"/>
                    <stop id="stops2" offset="%f" stop-color="lightgreen" stop-opacity="1"/>
                    <stop id="stops3" offset="%f" stop-color="lightgreen" stop-opacity="1"/>
                    <stop id="stops4" offset="1" stop-color="lightgreen" stop-opacity="0"/>
                </radialGradient>
            </defs>
            """ %(HZinner2/HZouter2, HZinner/HZouter2,HZouter/HZouter2 )
        if HZinner2<maxa*2:
            svg += '<ellipse cx="%f" cy="%f" rx="%f" ry="%f" fill="url(#habitablegradient)" />' %(
                    0.,
                    height/2,
                    au*HZouter2,
                    au*HZouter2)
            svg += '<text     x="%f"" y="%f" font-family="sans-serif" font-weight="normal"  font-size="12" stroke="none" style="fill:green">Habitable zone</text>' %(
                    au*HZinner2,
                    height-1)


        svg += '<ellipse cx="%f" cy="%f" rx="%f" ry="%f" style="fill:red" />' %(
                    0.,
                    height/2,
                    au*stellarRadius*0.0046524726,
                    au*stellarRadius*0.0046524726)

        svg += '<g style="stroke:black;">'
        for planet in planets:
            semimajoraxis = getFloat(planet,"./semimajoraxis")
            if semimajoraxis is None:
                hostmass = getFloat(star,"./mass",1.)
                period = getFloat(planet,"./period",265.25)
                semimajoraxis = pow(pow(period/6.283/365.25,2)*39.49/hostmass,1.0/3.0)
            size= 12
            textx=semimajoraxis*au+2
            texty=last_text_y+size
            last_text_y = texty

            svg += '<g>'
            svg += '<ellipse cx="%f" cy="%f" rx="%f" ry="%f" style="fill:none" />' %(
                        0.,
                        height/2,
                        semimajoraxis*au,
                        semimajoraxis*au)
            svg += '<text x="%f" y="%f" font-family="sans-serif" font-weight="normal"  font-size="%f" stroke="none" >%s</text>' %(
                        textx,
                        texty,
                        size,
                        getText(planet,"./name"))
            svg += '</g>'

        visualizations.append((getText(star,"./name",""),svg))

    return visualizations

def textArchitecture(o,stype=0):
    architecture = ""
    if stype==1:
        architecture += "<ul style=\"padding: 0; margin: 0;\">"
    else:
        architecture += "<ul style=\"padding-left: 1em; margin-left: 1em;\">"

    bs = o.findall("./binary")
    for b in bs:
        architecture += "<li><img src=\"/static/img/binary.png\" width=\"16\" height=\"16\" />&nbsp;Stellar binary";
        a = b.find("./semimajoraxis")
        if a is not None:
            architecture += ", semi-major axis: "+renderFloat(a)+" AU"
        period = b.find("./period")
        if period is not None:
            if period>1000.:
                 architecture += ", "+renderFloat(period,0.002737909)+" years"
            else:
                 architecture += ", "+renderFloat(period)+" days"
        architecture += textArchitecture(b,2)

    ss = o.findall("./star")
    for s in ss:
        architecture += "<li><img src=\"/static/img/star.png\" width=\"16\" height=\"16\" />&nbsp;"+s.find("./name").text+", stellar object"
        architecture += textArchitecture(s)

    ps = o.findall("./planet")
    for p in ps:
        architecture += "<li><img src=\"/static/img/planet.png\" width=\"16\" height=\"16\" />&nbsp;"+p.find("./name").text
        if stype==0:
            architecture += ", planet"
        if stype==1:
            architecture += ", orphan planet"
        if stype==2:
            architecture += ", circumbinary planet, P-type"
        a = getFloat(p,"./semimajoraxis")
        if a:
            architecture += ", semi-major axis: "+renderFloat(p.find("./semimajoraxis"))+" AU"
        architecture += textArchitecture(p)
    architecture += "</ul>"
    return architecture
