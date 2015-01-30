import StringIO
import matplotlib.pyplot as plt
from matplotlib import rcParams

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
