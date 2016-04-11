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


    -h show this information
    -o run offline, only use the data available in the locate database

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


def getsignals(listofdates,QNC,SIGNALNC):
    """

    :param listofdates:
    :return:
    """

    #Initialize the databse lookup object
    sgrObj = sgr.sgr_data.SignalQCdf(QNC,SIGNALNC)


def mergedates(modisdates,requesteddates):
    """
    Match modis data and requested dates and comes back with a list
    of modis file to process and matchging requested dates

    :param modisdates:
    :param requesteddates:
    :return:
    """


def main(argv=None):
    """


    :param argv:
    :return:
    """


    inifname = 'sgr.ini'
    logfname = 'sgr.log'
    stations = [1,4,295,300]


    if argv is None:
        argv = sys.argv[1:]
        if len(argv) == 0:
            usage()
            return

    try:
        opts, args = getopt.getopt(argv, 'ho')
    except getopt.error, msg:
        usage(msg)


    for o, a in opts:
        if o == '-h': usage()
        if o == '-o': offline = True



    logger = sgr.utils.setlogger(logfname,'sgr')
    #get_gdac_file_by_date(skipifexists=True)
    #get_modis_file_by_date(thedatetime=datetime.datetime(2016,2,2),skipifexists=True)
    sgr.config = sgr.utils.iniFileSetUp(inifname)
    qnetcdf = sgr.utils.configget(logger,sgr.config,'data','qdbase', sgr.get_path_from_root('data/Beck_Runoff_Database_v3.nc'))
    modissignalnetcdf = sgr.utils.configget(logger,sgr.config,'data','modissignaldbase',sgr.get_path_from_root('data/MODIS_SGR.nc'))
    modiscellidlist = sgr.utils.configget(logger,sgr.config,'data','modisidlist',sgr.get_path_from_root('data/MODIS_SGR_cells.csv'))
    staging= sgr.utils.configget(logger,sgr.config,'data','staging',sgr.get_path_from_root('staging/'))


    #url,fname = sgr.get_data.get_last_available_modis_file()

    #lst = sgr.get_data.get_available_modis_files([2014,2015,2016],logger)

    requesteddats = sgr.fews.readpixml('input/input.xml')

    localfiles = downloadandprocess([2014,2015,2016],logger, staging=staging)


    #Initialize the databse lookup object
    sgrObj = sgr.sgr_data.SignalQCdf(qnetcdf,modissignalnetcdf)

    #getsignals(xxx,qnetcdf,modissignalnetcdf)
    #now loop over all files
    results = []
    for key in sorted(localfiles):
        logger.info('Reading modis file, converting to waterfrac: ' + key)
        x,y,swir21 = sgr.modis_waterfrac.readmodisswir21(key)

        wf = sgr.modis_waterfrac.detwfrac(swir21)
        # Her a loop over all station ID's
        result = []
        for stat in stations:
            logger.info('Getting signal data for station: ' + str(stat))
            sngid = sgr.sgr_data.get_signal_ids(stat, y, x, modiscellidlist)
            signal = wf[sngid].mean()
            # now initialize the lookup object
            q= sgrObj.findqfromsignal(signal,stat)
        results.append([localfiles[key],signal,q])

        print str(localfiles[key]) + "," + str(q)

    #get_stationfrombeck('Beck_Runoff_Database_v3.nc',2)


if __name__ == "__main__":
    main()