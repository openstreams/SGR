import numpy as np
import modis_waterfrac

def getcelllocs(id):
    """
    get the cell x,y coordinates for a given reach id

    :param id:
    :return:
    """

    #0.29795020818710327

    return [[30.7045945412, 28.4631393118,0.8365073204040527],
            [31.5640043408, 22.2543419844,0.9556962251663208],

            ]


def extract_signal(id,y_array, x_array):
    """

    :return:
    """
    cols = []
    xx = []
    yy = []

    cels = getcelllocs(id)
    for pt in cels:
        intx = abs(np.diff(x_array).mean())
        inty = abs(np.diff(y_array).mean())

        x = int((pt[0] - x_array.min())/intx)
        # array is in decending order
        y = len(y_array) - int((pt[1] - y_array.min())/inty) -1
        xx.append(x)
        yy.append(y)


    return [yy,xx]


fname = 'MCD43C4.A2016033.005.2016050202316.h5'
outfname = fname[0:16] + ".tif"
x, y, swir21 = modis_waterfrac.readmodisswir21(fname)
wf = modis_waterfrac.detwfrac(swir21)


zz = extract_signal(2,y,x)


print x.min()

print zz
#print swir21[zzx]
print wf[zz]