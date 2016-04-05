

# http://www.gdacs.org/flooddetection/data/ALL/AvgSignalTiffs/
import urllib
import datetime
import os
import re
from bs4 import BeautifulSoup
import subprocess





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
    subprocess()
    return fn



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


def get_available_modis_dates():
    """

    :return: list of availble dates
    """

    listofdates = []

    return listofdates


def main(argv=None):
    #get_gdac_file_by_date(skipifexists=True)
    get_modis_file_by_date(thedatetime=datetime.datetime(2016,2,2),skipifexists=True)


if __name__ == "__main__":
    main()