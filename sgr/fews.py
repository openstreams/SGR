# Test version of wflow Delft-FEWS adapter
#
# Wflow is Free software, see below:
#
# Copyright (c) J. Schellekens 2005-2011
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
wflow_adapt.py: Simple wflow Delft-FEWS adapter in python. This file can be run
as a script from the command-line or be used as a module that provides (limited)
functionality for converting PI-XML files to .tss and back.

*Usage pre adapter:*

**wflow_adapt** -M Pre -t InputTimeseriesXml -I inifile -T timestepInSeconds

*Usage postadapter:*

**wflow_adapt**-M Post -t InputTimeseriesXml -s inputStateFile -I inifile
              -o outputStateFile -r runinfofile -w workdir -C case -T timestepInSeconds [-R runId]

Issues:

- Delft-Fews exports data from 0 to timestep. PCraster starts to count at 1.
  Renaming the files is not desireable. The solution is the add a delay of 1
  timestep in the GA run that exports the mapstacks to wflow.
- Not tested very well.
- There is a considerable amount of duplication (e.g. info in the runinfo.xml and
  the .ini file that you need to specify again :-())

 .. todo::

     rewrite and simplify

$Author: schelle $
$Id: wflow_adapt.py 915 2014-02-10 07:33:56Z schelle $
$Rev: 915 $

"""

import getopt, sys, os

from xml.etree.ElementTree import *

from datetime import *
import time
import string

import shutil
import re
from glob import *
import logging
import logging.handlers
import ConfigParser





outMaps = ["run.xml","lev.xml"]
iniFile = "wflow_sbm.ini"
case = "not_set"
runId="run_default"

logfile = "wflow_adapt.log"

def make_uniek(seq, idfun=None):
    # Order preserving
    return list(_f10(seq, idfun))

def _f10(seq, idfun=None):
    seen = set()
    if idfun is None:
        for x in seq:
            if x in seen:
                continue
            seen.add(x)
            yield x
    else:
        for x in seq:
            x = idfun(x)
            if x in seen:
                continue
            seen.add(x)
            yield x


fewsNamespace="http://www.wldelft.nl/fews/PI"



def log2xml(logfile,xmldiag):
    """
    Converts a wflow log file to a Delft-Fews XML diag file

    """

    trans = {'WARNING': '2', 'ERROR': '1', 'INFO': '3','DEBUG': '4'}
    if os.path.exists(logfile):
        ifile = open(logfile,"r")
        ofile = open(xmldiag,"w")
        all = ifile.readlines()

        ofile.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        ofile.write("<Diag xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" \n")
        ofile.write("xmlns=\"http://www.wldelft.nl/fews/PI\" xsi:schemaLocation=\"http://www.wldelft.nl/fews/PI \n")
        ofile.write("http://fews.wldelft.nl/schemas/version1.0/pi-schemas/pi_diag.xsd\" version=\"1.2\">\n")
        for aline in all:
            alineesc = aline.translate(None,"><&\"\'")
            lineparts = alineesc.strip().split(" - ")
            ofile.write("<line level=\"" + trans[lineparts[2]] + "\" description=\"" + lineparts[3] + " [" + lineparts[0] + "]\"/>\n")
        ofile.write("</Diag>\n")




def pixml_totss_dates (nname,outputdir):
    """
    Gets Date/time info from XML file and creates .tss files with:

        - Day of year
        - Hour of day
        - Others may follow

    """

    if os.path.exists(nname):
        file = open(nname, "r")
        tree = parse(file)
        PItimeSeries = tree.getroot()
        series = PItimeSeries.findall('.//{' + fewsNamespace + '}series')

        events = series[0].findall('.//{' + fewsNamespace + '}event')
        f = open(outputdir + '/YearDay.tss','w')
        ff = open(outputdir + '/Hour.tss','w')
        # write the header
        f.write('Parameter YearDay taken from ' + nname + '\n')
        ff.write('Parameter Hour taken from ' + nname + '\n')
        f.write('2\n')
        ff.write('2\n')
        for i in range(1,3):
            f.write('Data column ' + str(i) + '\n')
            ff.write('Data column ' + str(i) + '\n')
        i=1
        for ev in events:
            dt = datetime.strptime(ev.attrib['date'] + ev.attrib['time'],'%Y-%m-%d%H:%M:%S')
            f.write(str(i) +'\t' + dt.strftime('%j\n'))
            ff.write(str(i) +'\t' + dt.strftime('%H\n'))
            i = i+1
    else:
        print nname + " does not exists."


def readpixml(nname):
    """
    assumptions:
    - only one parameter (Q) allowed
    - date/time for all events and all locations shouls be the same

    """

    if os.path.exists(nname):
        file = open(nname, "r")
        tree = parse(file)
        PItimeSeries = tree.getroot()
        seriesStationList=PItimeSeries.findall('.//{' + fewsNamespace + '}stationName')
        LocList=[]
        for station in seriesStationList:
            LocList.append(station.text)

        Parameters=PItimeSeries.findall('.//{' + fewsNamespace + '}parameterId')
        ParList=[]
        for par in Parameters:
            ParList.append(par.text)

        uniqueParList=make_uniek(ParList)

        colsinfile=len(ParList)

        series = PItimeSeries.findall('.//{' + fewsNamespace + '}series')

        # put whole lot in a dictionary
        val = {}
        parlocs = {}
        i = 0
        for par in uniqueParList:
            parlocs[par] = 1


        for thisS in series:
            par = thisS.find('.//{' + fewsNamespace + '}parameterId').text
            events = thisS.findall('.//{' + fewsNamespace + '}event')
            locs = thisS.findall('.//{' + fewsNamespace + '}locationId')
            loc =  locs[0].text

            i=0;
            for ev in events:
                parlocs[par] = 1
                dt = datetime.strptime(ev.attrib['date'] + ev.attrib['time'],'%Y-%m-%d%H:%M:%S')
                if val.has_key((loc,par,dt)):
                    theval = val[loc,par,dt] + '\t' + ev.attrib['value']
                    val[loc,par,dt] = theval
                    parlocs[par] = parlocs[par] + 1
                else:
                    val[loc,par,dt] = ev.attrib['value']
                i = i+1
        nrevents = i
    else:
        print "cannot open xml file: " + nname
        exit(-1)


    return val





def pandastopixml(p_dataframe,xmlfile,parametername):
    """

    """
    missval = "-999.0"

    pavg =p_dataframe.resample('M').ffill()
    pavg.to_csv(xmlfile)


    #return None

    Sdate = pavg.index.date[0]
    Edate = pavg.index.date[-1]



    trange = Edate - Sdate

    Sdatestr = Sdate.strftime('%Y-%m-%d')
    Stimestr = Sdate.strftime('%H:%M:%S')

    Edatestr = Edate.strftime('%Y-%m-%d')
    Etimestr = Edate.strftime('%H:%M:%S')
    ofile = open(xmlfile,'w')
    ofile.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
    ofile.write("<TimeSeries xmlns=\"http://www.wldelft.nl/fews/PI\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://www.wldelft.nl/fews/PI http://fews.wldelft.nl/schemas/version1.0/pi-schemas/pi_timeseries.xsd\" version=\"1.2\">\n")
    ofile.write("<timeZone>0.0</timeZone>\n")
    count = 0

    for col in pavg.columns:
        count = count + 1
        ofile.write("<series>\n")
        ofile.write("<header>\n")
        ofile.write("<type>instantaneous</type>\n")
        ofile.write("<locationId>" + str(col) + "</locationId>\n")
        ofile.write("<parameterId>" + parametername + "</parameterId>\n")
        ofile.write("<timeStep unit=\"nonequidistant\"/>\n")
        ofile.write("<startDate date=\"" + Sdatestr +"\" time=\""+ Stimestr + "\"/>\n")
        ofile.write("<endDate date=\"" + Edatestr + "\" time=\"" + Etimestr + "\"/>\n")
        ofile.write("<missVal>"+str(missval)+"</missVal>\n")
        ofile.write("<stationName>" + str(col) +  "</stationName>\n")
        ofile.write("</header>\n")
        # add data here
        xdate = Sdate
        xcount = 0
        for pt in pavg[col].values:
            xdate = pavg.index[xcount].date()
            Ndatestr = xdate.strftime('%Y-%m-%d')
            Ntimestr = xdate.strftime('%H:%M:%S')
            ofile.write("<event date=\"" + Ndatestr + "\" time=\"" + Ntimestr + "\" value=\"" + str(pt) + "\" />\n")
            xcount = xcount + 1
        ofile.write("</series>\n")

    ofile.write("</TimeSeries>\n")
    ofile.close()

    return None


def getTimeStepsfromRuninfo(xmlfile,timestepsecs):
    """
        Gets the number of  timesteps from the FEWS runinfo file.
    """
    if os.path.exists(xmlfile):
        file = open(xmlfile, "r")
        tree = parse(file)
        runinf = tree.getroot()
        sdate=runinf.find('.//{' + fewsNamespace + '}startDateTime')
        ttime = sdate.attrib['time']
        if len(ttime) ==  12: # Hack for milliseconds in testrunner runifo.xml...
            ttime = ttime.split('.')[0]

        edate=runinf.find('.//{' + fewsNamespace + '}endDateTime')
        sd = datetime.strptime(sdate.attrib['date'] + ttime,'%Y-%m-%d%H:%M:%S')
        ed = datetime.strptime(edate.attrib['date'] + edate.attrib['time'],'%Y-%m-%d%H:%M:%S')
        diff = ed - sd


        if timestepsecs < 86400: # assume hours
            return (diff.seconds + diff.days * 86400)/timestepsecs +1
        else:
            return diff.days  + 1# Should actually be + 1 but fews starts at 0!
    else:
        print xmlfile + " does not exists."



def getEndTimefromRuninfo(xmlfile):
    """
    Gets the endtime of the run from the FEWS runinfo file
    """
    if os.path.exists(xmlfile):
        file = open(xmlfile, "r")
        tree = parse(file)
        runinf = tree.getroot()
        edate=runinf.find('.//{' + fewsNamespace + '}endDateTime')
        ed = datetime.strptime(edate.attrib['date'] + edate.attrib['time'],'%Y-%m-%d%H:%M:%S')
    else:
        print xmlfile + " does not exists."
        ed = None

    return ed

def getStartTimefromRuninfo(xmlfile):
    """
    Gets the starttime from the FEWS runinfo file
    """

    #TODO: return the timezone information...
    if os.path.exists(xmlfile):
        file = open(xmlfile, "r")
        tree = parse(file)
        runinf = tree.getroot()
        edate=runinf.find('.//{' + fewsNamespace + '}startDateTime')
        ttime = edate.attrib['time']
        if len(ttime) ==  12: # Hack for millisecons in testrunner runinfo.xml...
            ttime = ttime.split('.')[0]
        ed = datetime.strptime(edate.attrib['date'] + ttime,'%Y-%m-%d%H:%M:%S')
        # ed = pa
    else:
        return None

    return ed


#test = readpixml("c:/repos/satreach/sgr/input/input.xml")

