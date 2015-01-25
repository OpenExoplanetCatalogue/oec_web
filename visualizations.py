from math import *
from numberformat import getFloat, getText

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
    system, planet, filename = xmlPair 
    planets = system.findall(".//planet")
    maxr = max(map(getRadius,planets))

    pl_i=0
    textx=0


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
        if radius>0.:
            svg += plotplanet(radius, p.find("./name").text, False)
    
    svg += " </g>"
    return svg


def habitable(xmlPair):
    system, planet, filename = xmlPair 

    stars = system.findall(".//star")
    star = None
    for s in stars:
        if planet in s:
            star = s
            break
    if star is None:
        return None # cannot draw diagram for binary systems yet

    planets = system.findall(".//planet")

    maxa = 0
    for planet in planets:
        semimajoraxis = getFloat(planet,"./semimajoraxis")
        if semimajoraxis is None:
            hostmass = getFloat(star,"./mass",1.)
            period = getFloat(planet,"./period",265.25)
            semimajoraxis = pow(pow(period/6.283/365.25,2)*39.49/hostmass,1.0/3.0) 
        if semimajoraxis>maxa:
            maxa = semimajoraxis



    spectraltype = getText(star,"./spectraltype","O")[0]
    stellarr = getFloat(star,"./stellarr")
    if stellarr is None or stellarr<0.01:
        stellarr = 1.
        if spectraltype=='O': stellarr=10.
        if spectraltype=='B': stellarr=3.0
        if spectraltype=='A': stellarr=1.5
        if spectraltype=='F': stellarr=1.3
        if spectraltype=='G': stellarr=1.0
        if spectraltype=='K': stellarr=0.8
        if spectraltype=='M': stellarr=0.5
        
    temperature = getFloat(star,"./temperature")
    if temperature is None:
        temperature=5500
        if spectraltype=='O': temperature=40000
        if spectraltype=='B': temperature=20000
        if spectraltype=='A': temperature=8500
        if spectraltype=='F': temperature=6500
        if spectraltype=='G': temperature=5500
        if spectraltype=='K': temperature=4000
        if spectraltype=='M': temperature=3000
    
    temperature -= 5700
        
        
    linsun2  = 0.68	
    linsun1  = 0.95
    loutsun1 = 1.67
    loutsun2 = 1.95


    _stellarMass = getFloat(star,"./mass",1.)
    if _stellarMass>2.:
        luminosity = pow(_stellarMass,3.5)
    else:
        luminosity = pow(_stellarMass,4.)

    HZinner2 = (linsun2 -2.7619e-9*temperature-3.8095e-9*temperature*temperature) *sqrt(luminosity)
    HZouter2 = (loutsun2-1.3786e-4*temperature-1.4286e-9*temperature*temperature) *sqrt(luminosity)
    HZinner  = (linsun1 -2.7619e-9*temperature-3.8095e-9*temperature*temperature) *sqrt(luminosity)
    HZouter  = (loutsun1-1.3786e-4*temperature-1.4286e-9*temperature*temperature) *sqrt(luminosity)

    idnum=0


    width = 600
    height= 100
    au 	= 2.0/ maxa*(width-100)*0.49
    last_text_y=12

    svg = """
        <defs>
            <radialGradient id="habitablegradient" > 
                <stop id="stops0" offset=".0" stop-color="lightgreen" stop-opacity="0"/>
                <stop id="stops1" offset="<?=($HZinner2)/($HZouter2)?>" stop-color="lightgreen" stop-opacity="0"/>
                <stop id="stops2" offset="<?=($HZinner)/($HZouter2)?>" stop-color="lightgreen" stop-opacity="1"/>
                <stop id="stops3" offset="<?=($HZouter)/($HZouter2)?>" stop-color="lightgreen" stop-opacity="1"/>
                <stop id="stops4" offset="1" stop-color="lightgreen" stop-opacity="0"/>
            </radialGradient> 
        </defs>
        """
    if HZinner2<maxa*2:
        svg += '<ellipse cx="%f" cy="%f" rx="%f" ry="%f" fill="url(#habitablegradient)" />' %(
                0.,
                height/2,
                au*HZouter2,
                au*HZouter2)
        svg += '<text 	x="%f"" y="%f" font-family="sans-serif" font-weight="normal"  font-size="12" stroke="none" style="fill:green">Habitable zone</text>' %(
                au*HZinner2,
                height-1)

        
    svg += '<ellipse cx="%f" cy="%f" rx="%f" ry="%f" style="fill:red" />' %(
                0.,
                height/2,
                au*stellarr*0.0046524726,
                au*stellarr*0.0046524726)
    
    svg += '<g style="stroke:black;">'
    for planet in planets:
        name = getText(planet,"./name")
        semimajoraxis = getFloat(planet,"./semimajoraxis")
        if semimajoraxis is None:
            hostmass = getFloat(star,"./mass",1.)
            period = getFloat(planet,"./period",265.25)
            semimajoraxis = pow(pow(period/6.283/365.25,2)*39.49/hostmass,1.0/3.0) 
        idnum += 1
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
                    name)
        svg += '</g>'
    
    return svg
