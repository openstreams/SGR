#!/usr/bin/python

# sgr is Free software, see below:
#
# Copyright (c) A.I.J.M. van Dijk and J. Schellekens 2016
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
sgr_main - command-line processing for satreach

usage:
    sgr_main -c inifile -M -G

    -h show this information
    -c inifile
    -G run the Microwave base algorithm from the Global Flood Detection Systems
    -M run the mods based algorithm

if both -G and -M are given the script wil also output a merged result

"""
import sgr
import sgr.get_data
import sgr.modis_waterfrac
import sgr.sgr_data
import sgr.utils
import sgr.fews
import pandas
import os, getopt, sys, glob
import numpy as np
import datetime


def usage(*args):
    """

    :param args:
    :return:
    """

    sys.stdout = sys.stderr
    for msg in args: print msg
    print __doc__
    sys.exit(0)



def downloadandprocess(years,logger,staging='not set'):
    """
    :param years: list of year to download e.g. [2014,2015,2016]
    :param logger:
    :return: list of file avaiable after downloading
    """
    localflist = {}
    logger.info('Getting modis file list..')

    lst = sgr.get_data.get_available_modis_files(years)
    if staging == 'not set':
        staging = sgr.get_data.stagingarea

    # Loop of list of modis files
    # NB This list is NOT sorted!
    for url, value in lst.iteritems():
        fname = os.path.basename(url)
        lfilename = os.path.join(staging, fname)
        if not os.path.exists(lfilename):
            logger.info('Getting modis file:' + url)
            sgr.get_data.httpdownloadurl(url,lfilename)
        else:
            logger.info('Skipping modis file: ' + url)
        h5fname = lfilename.split('hdf')[0] + 'h5'
        if not os.path.exists(h5fname):
            sgr.get_data.converttohdf5(lfilename,h5fname)
        else:
            logger.info('Skipping modis file conversion to h5: ' + h5fname)

        # create list of all available files
        localflist[h5fname] = value

    return localflist




def downloadandprocesslist(lst,logger,staging='not set'):
    """
    :param lst: list files to get
    :param logger:
    :return: list of file avaiable after downloading
    """
    localflist = {}
    # Loop of list of modis files
    # NB This list is NOT sorted!
    for url, value in lst.iteritems():
        fname = os.path.basename(url)
        lfilename = os.path.join(staging, fname)
        if not os.path.exists(lfilename):
            logger.info('Getting modis file:' + url)
            sgr.get_data.httpdownloadurl(url,lfilename)
        else:
            logger.info('Skipping modis file: ' + url)
        h5fname = lfilename.split('hdf')[0] + 'h5'
        if not os.path.exists(h5fname):
            sgr.get_data.converttohdf5(lfilename,h5fname)
        else:
            logger.info('Skipping modis file conversion to h5: ' + h5fname)

        # create list of all available files
        localflist[h5fname] = value

    return localflist



def downloadandprocesslistgdac(lst,logger,staging='not set'):
    """
    :param lst: list files to get
    :param logger:
    :return: list of file avaiable after downloading
    """
    localflist = {}
    # Loop of list of modis files
    # NB This list is NOT sorted!
    for url, value in lst.iteritems():
        fname = os.path.basename(url)
        lfilename = os.path.join(staging, fname)
        if not os.path.exists(lfilename):
            logger.info('Getting gdac file:' + url)
            sgr.get_data.httpdownloadurl(url,lfilename)
        else:
            logger.info('Skipping gdac file: ' + url)
        h5fname = lfilename.split('hdf')[0] + 'h5'


        # create list of all available files
        localflist[lfilename] = value

    return localflist


def getsignals(listofdates,QNC,SIGNALNC):
    """

    :param listofdates:
    :return:
    """

    #Initialize the databse lookup object
    sgrObj = sgr.sgr_data.SignalQCdf(QNC,SIGNALNC)


def whichdatestoget(modisdates,requesteddates):
    """
    Match modis data and requested dates and comes back with a list
    of modis file to process and matchging requested dates

    :param modisdates:
    :param requesteddates:
    :return:
    """

    datesandfiles = {}
    # Determine data range from the requested dates
    a = np.array(requesteddates.keys())
    firstdate = sorted(a[:,2])[0].date()
    lastdate= sorted(a[:,2])[-1].date()

    for key, val in modisdates.iteritems():
        if val <= lastdate and val >= (firstdate - datetime.timedelta(days=30)):
            datesandfiles[key] = val

    return datesandfiles




# TODO: Add csv/pandas output option
# TODO: Add switch to select MODIS/GFDS
# TODO: Add merging of MODIS/GFDS based on error



def main(argv=None):
    """
    :param argv:
    :return:
    """
    inifname = 'not set'
    logfname = 'sgr.log'
    domodis = False
    dogfds = False

    if argv is None:
        argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, 'hc:MG')
    except getopt.error, msg:
        usage(msg)

    for o, a in opts:
        if o == '-h': usage()
        if o == '-c': inifname = a
        if o == '-M': domodis = True
        if o == '-G': dogfds = True

    if 'not set' in inifname:
        print "-c inifile command-line option must be used"
        usage()

    # set logger and get settings from config file
    logger = sgr.utils.setlogger(logfname,'sgr')
    #get_gdac_file_by_date(skipifexists=True)
    logger.info("Starting up sgr...")
    #get_modis_file_by_date(thedatetime=datetime.datetime(2016,2,2),skipifexists=True)
    if os.path.exists(inifname):
        sgr.config = sgr.utils.iniFileSetUp(inifname)
    else:
        logger.error("Cannot open config file: " + inifname)
        exit(-1)
    qnetcdf = sgr.utils.configget(logger,sgr.config,'data','qdbase', sgr.get_path_from_root('data/Beck_Runoff_Database_v3.nc'))
    modissignalnetcdf = sgr.utils.configget(logger,sgr.config,'data','modissignaldbase',sgr.get_path_from_root('data/MODIS_SGR.nc'))
    gfdssignalnetcdf = sgr.utils.configget(logger, sgr.config, 'data', 'gfdssignaldbase',
                                            sgr.get_path_from_root('data/GFDS_SGR.nc'))
    modiscellidlist = sgr.utils.configget(logger,sgr.config,'data','modisidlist',sgr.get_path_from_root('data/MODIS_SGR_cells.csv'))
    gfdscellidlist = sgr.utils.configget(logger, sgr.config, 'data', 'gfdsidlist',
                                          sgr.get_path_from_root('data/GFDS_SGR_cells.csv'))

    staging=sgr.utils.configget(logger,sgr.config,'data','staging',sgr.get_path_from_root('staging/'))
    xmlinput = sgr.utils.configget(logger,sgr.config,'data','xmlinput',sgr.get_path_from_root('input/input.xml'))
    xmloutput_q = sgr.utils.configget(logger,sgr.config,'data','q_output',sgr.get_path_from_root('output/Q.xml'))
    xmloutput_s = sgr.utils.configget(logger, sgr.config, 'data', 'signal_output', sgr.get_path_from_root('output/Signal.xml'))

    # check the input data (requested output) from the XML
    xmlinputdates = sgr.fews.readpixml(xmlinput)
    keyar = np.array(xmlinputdates.keys())
    stations = np.unique(keyar[:,0])

    if dogfds:
        # Generate the list of 4day average gdac fils
        gdacfilelists =  sgr.get_data.get_available_gdac_files((sorted(xmlinputdates.keys())[0][2]),\
                                                               (sorted(xmlinputdates.keys())[-1][2]))

        localgdacfiles = downloadandprocesslistgdac(gdacfilelists, logger, staging=staging)
        # Inilialize the lookup database
        sgrObjgfds = sgr.sgr_data.SignalQCdf(qnetcdf,gfdssignalnetcdf)
        sgrObjgfds.MKerrmodel(statids=stations)

        resultss = []
        resultsq = []
        for key in sorted(localgdacfiles):
            logger.info("Reading GFDS tiff file: " + str(key))
            x,y, gfdssignal=sgr.get_data.readgfds(key)
            # Here a loop over all station ID's
            result_q = []
            result_q.append(localgdacfiles[key])
            result_s = []
            result_s.append(localgdacfiles[key])
            for stat in stations:
                gfdssigid = sgr.sgr_data.get_signal_ids(int(stat), y, x, gfdscellidlist)
                signal = gfdssignal[gfdssigid].mean()
                result_s.append(signal)
                result_q.append(sgrObjgfds.findqfromsignal(signal, int(stat)))

            resultss.append(result_s)
            resultsq.append(result_q)

        # make this into a pandas array
        # Column id is station id
        gfdsresultss = pandas.DataFrame(np.array(resultss)[:, 1:], index=pandas.DatetimeIndex(np.array(resultss)[:, 0]))
        gfdsresultss.columns = list(stations)

        gfdsresultsq = pandas.DataFrame(np.array(resultsq)[:, 1:], index=pandas.DatetimeIndex(np.array(resultsq)[:, 0]))
        gfdsresultsq.columns = list(stations)

        # name make into monthly average
        qavggfds = gfdsresultsq.resample('M').ffill()
        savggfds = gfdsresultss.resample('M').ffill()
        # Now rerun with monthly signal input
        qbest = sgr.sgr_data.signaltoq_pandas(savggfds, qnetcdf, gfdssignalnetcdf)

        sgr.fews.pandastopixml(savggfds, xmloutput_s + '_GFDS.xml', 'S')
        sgr.fews.pandastopixml(qavggfds, xmloutput_q+ '_GFDS.xml', 'Q')
        sgr.fews.pandastopixml(qbest, xmloutput_q + "_GFDS_best.xml", 'Q')
        sgr.fews.pandastopixml(gfdsresultss, xmloutput_s + "_GFDS_.xml", 'S')
        sgr.fews.pandastopixml(gfdsresultsq, xmloutput_q + "_GFDS_.xml", 'Q')


    if domodis:
        # Get modis data in batches of years
        lastyear = (sorted(xmlinputdates.keys())[-1][2]).year
        firstyear = (sorted(xmlinputdates.keys())[0][2]).year
        firstmonth = (sorted(xmlinputdates.keys())[0][2]).month
        if firstmonth ==1:
            firstyear = firstyear -1
        yrs = range(firstyear,lastyear+1)
        logger.info("Getting list of available modis files...")
        lst = sgr.get_data.get_available_modis_files(yrs)

        modisfilelist = whichdatestoget(lst,xmlinputdates)
        localfiles = downloadandprocesslist(modisfilelist, logger, staging=staging)

        #Initialize the databsse lookup object
        sgrObj = sgr.sgr_data.SignalQCdf(qnetcdf,modissignalnetcdf)
        # Run the error model in the object to fill it with the current stations nlu
        sgrObj.MKerrmodel(statids=stations)

        resultss = []
        resultsq = []
        for key in sorted(localfiles):
            logger.info('Reading modis file, converting to waterfrac: ' + key)
            x,y,swir21 = sgr.modis_waterfrac.readmodisswir21(key)

            wf = sgr.modis_waterfrac.detwfrac(swir21)
            # Here a loop over all station ID's
            result_q = []
            result_q.append(localfiles[key])
            result_s = []
            result_s.append(localfiles[key])
            # Extract data fro all stations
            for stat in stations:
                logger.info('Getting signal data for station: ' + str(stat))
                sngid = sgr.sgr_data.get_signal_ids(int(stat), y, x, modiscellidlist)
                signal = wf[sngid].mean()
                # now initialize the lookup object
                result_s.append(signal)
                q= sgrObj.findqfromsignal(signal,int(stat))
                result_q.append(q)

            resultss.append(result_s)
            resultsq.append(result_q)


        # make this into a pandas array
        # Column id is station id
        modresultss = pandas.DataFrame(np.array(resultss)[:, 1:], index=pandas.DatetimeIndex(np.array(resultss)[:, 0]))
        modresultss.columns= list(stations)

        modresultsq = pandas.DataFrame(np.array(resultsq)[:, 1:], index=pandas.DatetimeIndex(np.array(resultsq)[:, 0]))
        modresultsq.columns = list(stations)

        # name make into monthly average
        qavg =modresultsq.resample('M').ffill()
        savg = modresultss.resample('M').ffill()

        # Now rerun with monthly signal input
        qbest = sgr.sgr_data.signaltoq_pandas(savg,qnetcdf,modissignalnetcdf)

        sgr.fews.pandastopixml(savg,xmloutput_s,'S')
        sgr.fews.pandastopixml(qavg, xmloutput_q,'Q')
        sgr.fews.pandastopixml(qbest, xmloutput_q + "_best.xml", 'Q')
        sgr.fews.pandastopixml(modresultss,xmloutput_s + "_.xml",'S')
        sgr.fews.pandastopixml(modresultsq, xmloutput_q+ "_.xml",'Q')

    logger.info('sgr ended sucessfully')



if __name__ == "__main__":
    main()