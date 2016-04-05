import numpy as np
import modis_waterfrac

def getcelllocs(id):
    """
    get the cell x,y coordinates for a given reach id

    :param id:
    :return:
    """

    return [[1,0],
            [-1,-89],
            [-15,52],
            [-180,52],
            [10,52],
            [11,52],
            [12,52],
            [13,52],
            ]


def extract_signal(id,y_array, x_array):
    """

    :return:
    """
    cols = []
    xx = []
    yy = []
    def find_index_of_nearest_xy(y_array, x_array, y_point, x_point):
        distance = (y_array-y_point)**2 + (x_array-x_point)**2
        idy,idx = np.where(distance==distance.min())
        return idy[0],idx[0]

    cels = getcelllocs(id)
    for pt in cels:
        y, x = find_index_of_nearest_xy(y_array, x_array,pt[1],pt[0])
        cols.append([x,y])
        xx.append(x)
        yy.append(y)


    return [yy, xx]




fname = 'MCD43C4.A2016033.005.2016050202316.h5'
outfname = fname[0:16] + ".tif"
x, y, swir21 = modis_waterfrac.readmodisswir21(fname)
wf = modis_waterfrac.detwfrac(swir21)

xmat, ymat = np.meshgrid(x, y)

print xmat
print ymat
#zz = extract_signal(2,wf,x,y)
zzx = extract_signal(2,ymat,xmat)

print x.min()
print zzx

print swir21[zzx].mean()