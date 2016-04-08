

# http://www.gdacs.org/flooddetection/data/ALL/AvgSignalTiffs/
import urllib
import datetime
import os
import re
from bs4 import BeautifulSoup
import subprocess
import netCDF4
import re
import sgr


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
    dirs = BeautifulSoup(urlpath.read())
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

    fn, head = urllib.urlretrieve(url, localdir)







def converttohdf5(fname):
    """

    :param fname:
    :return:
    """

    h5name = fname.split('hdf')[0] + 'h5'
    converter = sgr.get_path_from_root(os.path.join('convert','bin','h4toh5convert.exe'))
    subprocess.call([converter,fname,h5name])

    return h5name


def get_gdac_file_by_date(thedatetime=None,skipifexists=True):
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

    if not os.path.exists(localfname):
        try:
            fname = "http://www.gdacs.org/flooddetection/data/ALL/AvgSignalTiffs/" + curyear +\
                    "/" + curmonth + "/signal_4days_avg_4days_"+ curyear + curmonth + curday + ".tif"
            fn, head = urllib.urlretrieve(fname, localfname)
        except:
            return None

    return localfname



def get_available_modis_files(years):
    """
    input list of year

    :return: list of all availble dates
    """
    url_date = {}
    remotedir = "http://e4ftl01.cr.usgs.gov/MOTA/MCD43C4.005"
    now = datetime.datetime.now()
    urlpath = urllib.urlopen(remotedir)
    dirlisthtml =BeautifulSoup(urlpath.read())

    lst = dirlisthtml.findAll('a',text=re.compile(str(years[0])))
    for year in years[1:len(years)]:
        lst.extend(dirlisthtml.findAll('a',text=re.compile(str(year))))
    lst.sort()

    # last one is the dir with the most recent file

    for f in lst:
        filedir = str(f).split('"')[1]
        urlpath = urllib.urlopen(remotedir + '/' + filedir)
        dirlisthtml =BeautifulSoup(urlpath.read())
        res = dirlisthtml.findAll('a',text=re.compile(".hdf"))
        fn = str(res[0]).split('"')[1]
        filelocation = remotedir + '/' + filedir + '/' + fn
        url_date[filelocation] = datetime.datetime.now()

    return url_date


def get_last_available_modis_file():
    """

    :return: list of availble dates
    """

    remotedir = "http://e4ftl01.cr.usgs.gov/MOTA/MCD43C4.005"
    now = datetime.datetime.now()
    urlpath = urllib.urlopen(remotedir)
    dirlisthtml =BeautifulSoup(urlpath.read())

    lst = dirlisthtml.findAll('a',text=re.compile(str(now.year -1)))
    lst.extend(dirlisthtml.findAll('a',text=re.compile(str(now.year))))
    lst.sort()

    # last one is the dir with the most recent file
    filedir = str(lst[-1]).split('"')[1]
    urlpath = urllib.urlopen(remotedir + '/' + filedir)
    dirlisthtml =BeautifulSoup(urlpath.read())
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

    lst = get_available_modis_files([2014,2015,2016])
    print lst
    #url,fname = get_last_available_modis_file()
    #lfilename = os.path.join(stagingarea, fname)

    #if not os.path.exists(lfilename):
    #    httpdownloadurl(url,lfilename)

    #h5fname = converttohdf5(lfilename)

    #get_stationfrombeck('Beck_Runoff_Database_v3.nc',2)

if __name__ == "__main__":
    main()

