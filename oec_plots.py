import StringIO
import matplotlib.pyplot as plt
import math
import numpy as np
from numberformat import getCoordinates, getText
from matplotlib import rcParams
import matplotlib.cm as cm

def discoveryyear(oec_meta_statistics):
    data_x = []
    data_y = []
    sum_y = 0
    for y in oec_meta_statistics.find("./discoveryyear"):
        data_x.append(int(y.tag[1:]))
        sum_y+=int(y.text)
        data_y.append(sum_y)

    rcParams.update({'figure.autolayout': True})

    fig = plt.figure(figsize=(700./96.,230./96.))
    plt.xlabel('Year')
    plt.ylabel('Confirmed planets')
    plt.plot(data_x,data_y,linestyle='-', marker='o')
    imgdata = StringIO.StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    svg_dta = imgdata.buf
    return svg_dta

def skypositions(systems):
    data_x = {} 
    data_y = {} 
    for s in systems:
        c = getCoordinates(s)
        if c is not None:
            ra, dec = c
            dm = s.find(".//discoverymethod")
            if dm is not None:
                dm = dm.text
            else:
                dm = "other"
            if dm not in data_x:
                data_x[dm] = []
                data_y[dm] = []
            data_x[dm].append(ra*180./math.pi)
            data_y[dm].append(dec*180./math.pi)

    rcParams.update({'figure.autolayout': True})

    fig = plt.figure(figsize=(700./96.,400./96.))
    plt.xlabel('right ascension [deg]')
    plt.ylabel('declination [deg]')
    plt.xlim(0., 360.)
    plt.ylim(-90., 90.)
    colors = iter(cm.gist_rainbow(np.linspace(0, 1, len(data_x))))
    for key in data_x:
        plt.scatter(data_x[key], data_y[key], s=20., edgecolor=(0,0,0,0.5), alpha=0.5, label=key, color=next(colors))
    plt.legend(loc='upper left',fontsize=12,scatterpoints=1)

    imgdata = StringIO.StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    svg_dta = imgdata.buf
    return svg_dta
    
