import numpy as np
import modis_waterfrac
import netCDF4

import sgr
import sgr.utils
import pandas



def signaltoq_pandas(signalframe,qnetcdf, signalnetcdf):
    """
    Retrieves Q estimates for all points in the pandas dataframe
    Column header are interpreted as station id's

    :param signal dataframe:
    :return pandas dateframe with Q and Q_h and Q_l:
    """

    sgrObj = sgr.sgr_data.SignalQCdf(qnetcdf, signalnetcdf)
    sgrObj.MKerrmodel(statids=signalframe.columns)

    # make room for hi and lo columns
    newcolumns = []
    for xcol in signalframe.columns:
        newcolumns.append(xcol)
        newcolumns.append(xcol + '_h')
        newcolumns.append(xcol + '_l')

    qdf = pandas.DataFrame(columns=newcolumns, index=signalframe.index)

    for col in signalframe.columns:
        for i in signalframe.index:
            qdf[col][i] = sgrObj.findqfromsignal(signalframe[col][i],int(col))
            err = sgrObj.geterrorfromqest(qdf[col][i],int(col))
            qdf[col +'_l'][i] = qdf[col][i] * (1 - err[0])
            qdf[col + '_h'][i] = qdf[col][i] * (1 + err[0])

    return qdf



def getcellloc(id,cellidlist):
    """
    get the cell x,y coordinates for a given reach id

    :param id:
    :param cellidlist: csv file with id's and x,y coordinates (8 per cell fro modis 4 per cell for gfds)
    :return:
    """
    # assume the id''s match the line numbers
    skipheader =  id
    idlst = np.genfromtxt(cellidlist,delimiter=',',skip_header=skipheader,max_rows=1)

    if not idlst[0] == id:
        raise ValueError("Id does not match ")

    if len(idlst) == 9: #gfds
        retval = idlst[1:].reshape((2, 4)).transpose()
    else:
        retval  = idlst[1:].reshape((2,8)).transpose()


    return retval



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
        self.QEST = np.zeros_like(self.Q) * np.nan
        self.relerror = {}
        self.yestHI ={}


    def MKerrmodel(self,nrintervals=5,statids=[]):
        """
        Creates the error model fro all stations. Uses Qest fro all Qobs
        in the database

        :param statid:
        :param nrintervals:
        :return:
        """

        if len(statids) ==0:
            statids = self.QID

        for statid in statids:
            id = int(statid) - 1

            cnt = 0
            for s in self.Signal[id,:]:
                self.QEST[id,cnt] = self.findqfromsignal(s,int(statid))
                cnt += 1

            q = self.Q[id, :]
            qest = self.QEST[id,:]

            # First extract the matching times
            qestvalid = np.isfinite(qest)
            qvalid = np.isfinite(q)
            validpoinst = np.logical_and(qvalid, qestvalid)

            percentiles = np.arange(1. / nrintervals, 1 + 1. / nrintervals, 1. / nrintervals)
            yestHI = np.zeros((nrintervals)) * np.nan
            relerror = np.zeros((nrintervals, 2)) * np.nan

            if sum(validpoinst) > 1:
                # Loop over the bins we use
                for i in np.arange(0, nrintervals):
                    lowboun = np.percentile(qest[validpoinst], (percentiles[i] - 1. / nrintervals) * 100.0)
                    highboun = np.percentile(qest[validpoinst], (percentiles[i]) * 100.0)
                    yestHI[i] = highboun
                    iunder = np.logical_and(np.logical_and(qest >= lowboun, qest <= highboun),
                                            np.logical_and(qest < q, q > 0.))
                    relerror[i, 0] = np.median(qest[iunder] / q[iunder] - 1)
                    iover = np.logical_and(np.logical_and(qest >= lowboun, qest <= highboun),
                                           np.logical_and(qest >= q, q > 0.))
                    relerror[i, 1] = np.median(qest[iover] / q[iover] - 1)


            self.relerror[int(statid)] = abs(relerror)
            self.yestHI[int(statid)] = yestHI




    def geterrorfromqest(self,qest,statid):


        id = statid -1
        nrintervals = len(self.yestHI[statid])

        relerrorTS = np.array([0.,0.]) * np.nan
        if np.isfinite(qest):
            iHB = np.searchsorted(self.yestHI[statid], qest)

            extrapolate = True if iHB > len(self.yestHI[statid]) - 1 else False
            atlowedge = True if iHB == 0 else False

            if not extrapolate and not atlowedge:
                slope = (self.relerror[statid][iHB, :] - self.relerror[statid][iHB - 1, :]) / (self.yestHI[statid][iHB] - self.yestHI[statid][iHB - 1])
                # slope(isinf(abs(slope)))=0;
                relerrorTS[:] = self.relerror[statid][iHB - 1, :] + slope * (qest - self.yestHI[statid][iHB - 1])

            if extrapolate:
                slope = (self.relerror[statid][nrintervals-1, :] - self.relerror[statid][nrintervals - 2, :]) / (
                    self.yestHI[statid][nrintervals-1] - self.yestHI[statid][nrintervals - 2])
                slope[np.isinf(abs(slope))] = 0.0
                relerrorTS[:] = self.relerror[statid][nrintervals-1, :] + slope * (qest - self.yestHI[statid][nrintervals-1])
                relerrorTS[:] = np.maximum(relerrorTS[:],
                                              self.relerror[statid][nrintervals-1, :])  # don't extrapolate to lesser values

            if atlowedge:
                slope = (self.relerror[statid][1, :] - self.relerror[statid][0, :]) / (self.yestHI[statid][1] - self.yestHI[statid][0])
                slope[np.isinf(abs(slope))] = 0.0
                relerrorTS[:] = self.relerror[statid][0, :] + slope * (qest - self.yestHI[statid][0])
                relerrorTS[:] = np.maximum(relerrorTS[:], self.relerror[statid][0,:])  # don't extrapolate to lesser value than calculated for nearest interval


        return  relerrorTS

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

        if len(a_qs) == 0: # no valid points
            return np.nan

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




def geterrorparameters(qobs,qsim,nrintervals=5):
    """

    :param Q: Measured Q
    :param Qest: Estimated Q
    :param nrintervals:
    :return:
    """

    for col in qsim.columns:
        qest = qsim[col].values
        q = qobs[col].values

        # First extract the matching times
        qestvalid = np.isfinite(qest)
        qvalid = np.isfinite(q)
        validpoinst = np.logical_and(qvalid, qestvalid)

        percentiles = np.arange(1. / nrintervals, 1 + 1. / nrintervals, 1. / nrintervals)
        yestHI = np.zeros((nrintervals)) * np.nan
        relerror = np.zeros((nrintervals, 2)) * np.nan

        # Loop over the bins we use
        for i in np.arange(0, nrintervals):
            lowboun = np.percentile(qest[validpoinst], (percentiles[i] - 1. / nrintervals) * 100.0)
            highboun = np.percentile(qest[validpoinst], (percentiles[i]) * 100.0)
            yestHI[i] = highboun
            iunder = np.logical_and(np.logical_and(qest >= lowboun, qest <= highboun), np.logical_and(qest < q, q > 0.))
            relerror[i, 0] = np.median(qest[iunder] / q[iunder] - 1)
            iover = np.logical_and(np.logical_and(qest >= lowboun, qest <= highboun), np.logical_and(qest >= q, q > 0.))
            relerror[i, 1] = np.median(qest[iover] / q[iover] - 1)

        relerror = abs(relerror)
        relerrorTS = np.zeros((len(qest), 2)) * np.nan
        for i in np.arange(0, len(qsim.values)):
            if np.isfinite(qest[i]):
                iHB = np.searchsorted(yestHI, qest[i])

                extrapolate = True if iHB > len(yestHI) - 1 else False
                atlowedge = True if iHB == 0 else False

                if not extrapolate and not atlowedge:
                    slope = (relerror[iHB, :] - relerror[iHB - 1, :]) / (yestHI[iHB] - yestHI[iHB - 1])
                    # slope(isinf(abs(slope)))=0;
                    relerrorTS[i, :] = relerror[iHB - 1, :] + slope * (qest[i] - yestHI[iHB - 1])

                if extrapolate:
                    slope = (relerror[nrintervals, :] - relerror[nrintervals - 1, :]) / (
                    yestHI[nrintervals] - yestHI[nrintervals - 1])
                    slope[np.isinf(abs(slope))] = 0.0
                    relerrorTS[i, :] = relerror[nrintervals, :] + slope * (qest[i] - yestHI[nrintervals])
                    relerrorTS[i, :] = np.maximum(relerrorTS[i, :],
                                               relerror[nrintervals, :])  # don't extrapolate to lesser values

                if atlowedge:
                    slope = (relerror[1, :] - relerror[0, :]) / (yestHI[1] - yestHI[0])
                    slope[np.isinf(abs(slope))] = 0.0
                    relerrorTS[i, :] = relerror[0, :] + slope * (qest[i] - yestHI[0])
                    relerrorTS[i, :] = np.maximum(relerrorTS[i, :], \
                                                  relerror[0,:])  # don't extrapolate to lesser value than calculated for nearest interval



def main():
    # for testing only

    logger = sgr.utils.setlogger('sgr.log','sgr')
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