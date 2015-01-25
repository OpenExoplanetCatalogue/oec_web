from math import *

width = 480
height= 200

def getRadius(planet):
    radiustag = planet.find("./radius")
    if radiustag:
        return float(radiustag.text)
    else:
        masstag = planet.find("./mass")
        if masstag is not None:
            m = float(masstag.text)*317.894
            if m>0.:
                # This is based on Lissauer et al 2011 b
                if m>30.:
                    return pow(m,1./3.)*0.0911302
                else:
                    return pow(m,1./2.06)*0.0911302
    return 0.

pl_i=0
pl_id=0
texty = 0.
space = 0.
earth = 1.
def plotplanet(radius,name,ss=True):
    global earth,pl_i,texty,pl_id, space
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
    pl_id +=1
    return svg

def size(xmlPair):
    global earth,pl_i,texty,pl_id, space
    system, planet, filename = xmlPair 
    planets = system.findall(".//planet")
    maxr = 0.
    for p in planets:
        r = getRadius(p)
        if r>maxr:
            maxr = r

    pl_i=0
    textx=0
    space=10


    earth 	= 1.0/ maxr*height*0.4
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
    svg += plotplanet(    1160.0/71490.0, "Pluto" ,True)
    svg += plotplanet(    2439.0/71490.0, "Mercury" ,True)
    svg += plotplanet(    3397.0/71490.0, "Mars" ,True)
    svg += plotplanet(    6052.0/71490.0, "Venus" ,True)
    svg += plotplanet(    6378.0/71490.0, "Earth" ,True)
    svg += plotplanet(   25269.0/71490.0, "Neptune" ,True)
    svg += plotplanet(   25559.0/71490.0, "Uranus" ,True)
    svg += plotplanet(   60268.0/71490.0, "Saturn"  ,True)
    svg += plotplanet(   71490.0/71490.0, "Jupiter" ,True)
    texty=0.0
    pl_i=0
    for p in planets:
        radius = getRadius(p)
        if radius>0.:
            svg += plotplanet(radius, p.find("./name").text, False)
    
    svg += " </g>"
    return svg
