import h5py
import numpy as np
from scipy.ndimage import filters
import utils


def detwfrac(swir21):
    """

    :param swir21:
    :return:
    """
    water_ref=0.008 # assumed
    kernel=7
    mbuffer=(kernel-1)/2
    row = swir21.shape[0]
    col = swir21.shape[1]
    target=np.zeros((row+2*mbuffer,col+2*mbuffer))
    row = target.shape[0]
    col = target.shape[1]
    target[mbuffer-1:row-1-mbuffer,mbuffer-1:col-1-mbuffer] = swir21
    perc=round(0.95*(kernel)**2.0) - 2 # finds perc value
    dry_ref = filters.rank_filter(np.maximum(0,target),int(perc),footprint=np.ones((kernel,kernel)))
    watf = np.minimum(1.0,np.maximum(0.0, (target - dry_ref)/(water_ref - dry_ref)))
    watf[target < 0.01] = 1.0
    waterfrac = watf[mbuffer-1:row-1-mbuffer,mbuffer-1:col-1-mbuffer]

    return waterfrac



def readmodisswir21(fname):

    bands = {1: 'red',2: 'NIR',3: 'blue',4: 'green',5: 'SWIR12',6: 'SWIR16',7: 'SWIR21'}
    bandnames =[]
    f = h5py.File(fname,'r')

    swir21name = 'MCD_CMG_BRDF_0.05Deg/Data Fields/Nadir_Reflectance_Band' + str(7)
    result = f[swir21name][:].astype(float)
    result[result == 32767] = np.nan
    result = result * 0.0001
    lon = np.arange(-180,180,0.05)
    lat = np.arange(-90,90,0.05)

    return lon,lat[::-1], result




fname = 'MCD43C4.A2016033.005.2016050202316.h5'
outfname = fname[0:16] + ".tif"
lon,lat,swir21 = readmodisswir21(fname)
wf = detwfrac(swir21)

utils.writeMap(outfname,'GTiff',lon,lat,wf,np.nan)