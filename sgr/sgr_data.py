import numpy as np
import modis_waterfrac
import netCDF4

import sgr
import sgr.utils
import sgr.sgr_data



def getcellloc(id,cellidlist):
    """
    get the cell x,y coordinates for a given reach id

    :param id:
    :return:
    """
    # assume the id''s match the line numbers
    skipheader =  id
    idlst = np.genfromtxt(cellidlist,delimiter=',',skip_header=skipheader,max_rows=1)

    if not idlst[0] == id:
        raise ValueError("Id does not match ")

    return idlst[1:].reshape((2,8)).transpose()




def get_signal_ids(id,y_array, x_array,cellidlist):
    """
    get the array id's if the signal for reach id "id"

    :return:
    """
    cols = []
    xx = []
    yy = []


    cels = getcellloc(id,cellidlist)

    for pt in cels:
        intx = abs(np.diff(x_array).mean())
        inty = abs(np.diff(y_array).mean())

        x = int((pt[1] - x_array.min())/intx)
        # array is in decending order
        y = len(y_array) - int((pt[0] - y_array.min())/inty) -1
        xx.append(x)
        yy.append(y)

    return [yy,xx]


class SignalQCdf():

    def __init__(self,qnetcdf,signalnetcdf):
        """

        :param qnetcdf:
        :param signalnetcdf:
        :return:
        """

        self.qnc = netCDF4.Dataset(qnetcdf)
        self.snc = netCDF4.Dataset(signalnetcdf)

        self.Q = self.qnc.variables['Discharge'][:]
        self.QID =  self.qnc.variables['ID'][:]
        self.QTime = self.qnc.variables['time'][:]

        self.Signal = self.snc.variables['SGRS'][:]
        self.SID =  self.snc.variables['ID'][:]
        self.STime = self.snc.variables['time'][:]

    def findqfromsignal(self,signal,statid):
        """
        Does cdf matching on Q and signal

        :param signal:
        :return:
        """
        id = statid -1
        # First extract the matching times
        q = self.Q[id,:]
        s = self.Signal[id,:]
        qvalid = np.isfinite(q)
        svalid = np.isfinite(s)
        validpoinst = np.logical_and(qvalid, svalid)
        a_qs = np.sort(self.Q[id,validpoinst])
        a_ss = np.sort(self.Signal[id,validpoinst])
        signalpos = np.searchsorted(a_ss,signal)

        extrapolate = True if signalpos > len(a_qs) - 1 else False
        if not extrapolate:
            perfectmatch = True if a_ss[signalpos] ==  signal else False
        else:
            perfectmatch = False

        atlowedge = True if signalpos == 0 else False
        # In this case we can safely return the matching Q value
        if perfectmatch and not extrapolate:
            return a_qs[signalpos]

        # interpolate
        if not extrapolate and not atlowedge:
            slope = (a_qs[signalpos] - a_qs[signalpos -1])/(a_ss[signalpos]-a_ss[signalpos -1])
            yest = a_qs[signalpos -1] + slope * (signal - a_ss[signalpos -1])
            return yest

        if extrapolate:
            slope = (a_qs[len(a_qs)-1] - a_qs[len(a_qs) -2])/(a_ss[len(a_qs)-1]-a_ss[len(a_qs) -2])
            yest = a_qs[len(a_qs)-1] + slope * (signal - a_ss[len(a_qs)-1])
            return yest

        if atlowedge:
            slope = (a_qs[1] - a_qs[0])/(a_ss[1]-a_ss[0])
            yest = a_qs[0] + slope * (signal - a_ss[0])
            yest = max(yest,0.0)
            return yest



def main():

    logger = sgr.utils.setlogger('tt.log','sgr')
    #get_gdac_file_by_date(skipifexists=True)
    #get_modis_file_by_date(thedatetime=datetime.datetime(2016,2,2),skipifexists=True)
    sgr.config = sgr.utils.iniFileSetUp('bbb.ini')
    qnetcdf = sgr.utils.configget(logger,sgr.config,'data','qdbase', sgr.get_path_from_root('data/Beck_Runoff_Database_v3.nc'))
    modissignalnetcdf = sgr.utils.configget(logger,sgr.config,'data','modissignaldbase',sgr.get_path_from_root('data/MODIS_SGR.nc'))
    modiscellidlist = sgr.utils.configget(logger,sgr.config,'data','modisidlist',sgr.get_path_from_root('data/MODIS_SGR_cells.csv'))
    staging=sgr.utils.configget(logger,sgr.config,'data','staging',sgr.get_path_from_root('staging/'))

    sgrObj = sgr.sgr_data.SignalQCdf(qnetcdf,modissignalnetcdf)

    tt = sgrObj.findqfromsignal(0.9,295)
    print tt

if __name__ == "__main__":
    main()