

# http://www.gdacs.org/flooddetection/data/ALL/AvgSignalTiffs/
import urllib
import datetime
import os
import sys
from bs4 import BeautifulSoup
import subprocess
import netCDF4
import re
import sgr
import sgr.utils
import numpy as np


stagingarea = sgr.get_path_from_root('staging')


def get_modis_file_by_date(thedatetime=None,skipifexists=True):
    """
    gets a file for a date. If date is not given the
    current date is used.

    :return: local file name None if unsuccessfull
    """

    producstr = "http://e4ftl01.cr.usgs.gov/MOTA/MCD43C4.005/"
    # fname MCD43C4.A2015281.005.2015302014313.hdf

    if thedatetime == None:
        now = datetime.datetime.now()
    else:
        now = thedatetime

    curyear = "%4d" % now.year
    curmonth= "%02d" % now.month
    curday = "%02d" % now.day
    yday = "%03d" % now.timetuple().tm_yday
    localfname = curyear + curmonth + curday + ".tif"

    fname = producstr + curyear + "." + curmonth + "." + curday +\
                    "/MCD43C4.A" + curyear + yday
    remotedir = producstr + curyear + "." + curmonth + "." + curday
    urlpath = urllib.urlopen(remotedir)
    dirs = BeautifulSoup(urlpath.read(),'lxml')
    fn = dirs.select('a[href*=hdf]')
    thename = str(fn[0]).split('\"')[1]

    fn, head = urllib.urlretrieve(remotedir + "/" +  thename, thename)

    return fn


def httpdownloadurl(url,localdir):
    """

    :param url:
    :param localdir:
    :return:
    """

    if os.path.exists(os.path.dirname(localdir)):
        try:
            fn, head = urllib.urlretrieve(url, localdir)
        except:
            try:
                 fn, head = urllib.urlretrieve(url, localdir)
            except:
                try:
                     fn, head = urllib.urlretrieve(url, localdir)
                except:
                    print "download failed after three tries..."
    else:
        print "Directory for local data does not exists: " + os.path.dirname(localdir)
        raise IOError




def converttohdf5(fname,h5name):
    """

    :param fname:
    :return:
    """

    converter = sgr.get_path_from_root(os.path.join('sgr','convert','bin','h4toh5convert.exe'))
    try:
        subprocess.call([converter,fname,h5name])
    except OSError as e:
        print "OS error({0}): {1}".format(e.errno, e.strerror)
        raise
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise



def get_gdac_file_by_date(thedatetime=None):
    """
    gets a file for a date. If date is not given the
    current date is used.

    :return: local file name None if unsuccessfull
    """

    if thedatetime == None:
        now = datetime.datetime.now()
    else:
        now = thedatetime

    curyear = "%4d" % now.year
    curmonth= "%02d" % now.month
    curday = "%02d" % now.day
    localfname = curyear + curmonth + curday + ".tif"


    fname = "http://www.gdacs.org/flooddetection/data/ALL/AvgSignalTiffs/" + curyear +\
                    "/" + curmonth + "/signal_4days_avg_4days_"+ curyear + curmonth + curday + ".tif"

    return fname


def readgfds(fname):
    """

    :param fname:
    :return:
    """
    resX, resY, cols, rows, x, y, data, FillVal = sgr.utils.readMap(fname, 'GTiff',None)
    ret = data.astype(float)
    ret[data==32000] = np.nan
    ret[data<=0] = np.nan
    ret = ret /1.0E6
    ret = 2.43 * (1-ret)

    x = np.arange(-180,180,0.09)
    y = np.arange(-90,90,0.09)[::-1]

    return x,y, ret


def get_available_gdac_files(datestart,dateend):

    datelist =  [datestart + datetime.timedelta(days=x) for x in range(0, (dateend-datestart).days)]

    ret = {}

    for thedate in datelist:
        urll = get_gdac_file_by_date(thedate)
        ret[urll] = thedate

    return ret


def get_available_modis_files(years):
    """
    input list of year

    :return: list of all available dates
    """
    url_date = {}
    remotedir = "http://e4ftl01.cr.usgs.gov/MOTA/MCD43C4.005"
    now = datetime.datetime.now()
    urlpath = urllib.urlopen(remotedir)
    dirlisthtml =BeautifulSoup(urlpath.read(),'lxml')

    lst = dirlisthtml.findAll('a',text=re.compile(str(years[0])))
    for year in years[1:len(years)]:
        lst.extend(dirlisthtml.findAll('a',text=re.compile(str(year))))
    lst.sort()

    # last one is the dir with the most recent file
    for f in lst:
        filedir = str(f).split('"')[1]
        urlpath = urllib.urlopen(remotedir + '/' + filedir)
        dirlisthtml =BeautifulSoup(urlpath.read(),"lxml")
        res = dirlisthtml.findAll('a',text=re.compile(".hdf"))
        fn = str(res[0]).split('"')[1]
        filelocation = remotedir + '/' + filedir + '/' + fn
        yrstr = filelocation.split('/')[5].split('.')
        thedate = datetime.date(int(yrstr[0]),int(yrstr[1]),int(yrstr[2]))
        url_date[filelocation] = thedate

    return url_date


def get_last_available_modis_file():
    """

    :return: list of availble dates
    """

    remotedir = "http://e4ftl01.cr.usgs.gov/MOTA/MCD43C4.005"
    now = datetime.datetime.now()
    urlpath = urllib.urlopen(remotedir)
    dirlisthtml =BeautifulSoup(urlpath.read(),'lxml')

    lst = dirlisthtml.findAll('a',text=re.compile(str(now.year -1)))
    lst.extend(dirlisthtml.findAll('a',text=re.compile(str(now.year))))
    lst.sort()

    # last one is the dir with the most recent file
    filedir = str(lst[-1]).split('"')[1]
    urlpath = urllib.urlopen(remotedir + '/' + filedir)
    dirlisthtml =BeautifulSoup(urlpath.read(),'lxml')
    res = dirlisthtml.findAll('a',text=re.compile(".hdf"))
    lastfile = str(res[0]).split('"')[1]

    lastfilelocation = remotedir + '/' + filedir + '/' + lastfile

    return lastfilelocation, lastfile


def get_stationfrombeck(fname,id):
    """
    Gets the Q data from a back station id

    :param fname:
    :param id:
    :return:
    """
    bd = netCDF4.Dataset(fname,mode='r')
    print bd.variables['ID'][:]


def main(argv=None):
    #get_gdac_file_by_date(skipifexists=True)
    #get_modis_file_by_date(thedatetime=datetime.datetime(2016,2,2),skipifexists=True)
    s = datetime.datetime(2016,4,1)
    e = datetime.datetime(2016,4,10)

    lst = get_available_gdac_files(s,e)
    print lst
    #url,fname = get_last_available_modis_file()
    #lfilename = os.path.join(stagingarea, fname)

    #if not os.path.exists(lfilename):
    #    httpdownloadurl(url,lfilename)

    #h5fname = converttohdf5(lfilename)

    #get_stationfrombeck('Beck_Runoff_Database_v3.nc',2)

if __name__ == "__main__":
    main()

