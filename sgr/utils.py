# -*- coding: utf-8 -*-
"""
Created on Mon Jul 21 07:36:06 2014

@author: schelle
"""

from osgeo import gdal, gdalconst
import logging, netCDF4
import logging.handlers
import ConfigParser
import os
from numpy import *
import sys
import datetime
from scipy import interpolate

try:
    import netCDF4.utils
except:
    import netCDF4_utils

import netcdftime

class ncdatset():
    """
    Wrapper around the nc object to simplify things

    Opens the dataset and determines the number of dimensions
    3 = T, Lat Lon
    4 = T heigth, Lat Lon
    """
    def __init__(self,ncurl,logger):
        self.logger = logger
        try:
            self.nc = netCDF4.Dataset(ncurl)
        except:
            self.logger.error("Failed to open remote file: " + ncurl)
            sys.exit(12)

        self.lat = self.getlat(self.nc)
        if self.lat == None:
            self.logger.error("No lat information found!")
        self.lon = self.getlon(self.nc)
        if self.lon == None:
            self.logger.error("No lon information found!")

        self.heigth = self.getheigth(self.nc)
        self.dimensions = 3 if self.heigth == None else 4
        self.time =   self.gettime(self.nc)
        #self.timesteps = self.time.shape[0]
        self.logger.debug(self.nc)


    def __del__(self):
        self.nc.close()


    def getlat(self,ncdataset):
        """
        Check for standard name latitude. If that is not present assume the variable name
        """

        for a in self.nc.variables:
            if hasattr(self.nc.variables[a],'standard_name'):
                if  self.nc.variables[a].standard_name == 'latitude':
                    return self.nc.variables[a]
            else:
                if a == 'latitude':
                    return self.nc.variables[a]

        return None

    def getvarbyname(self,name):
        """
        Check for standard name. If that is not present assume the variable name
        """

        for a in self.nc.variables:
            if hasattr(self.nc.variables[a],'standard_name'):
                if  self.nc.variables[a].standard_name == name:
                    return self.nc.variables[a]
            else:
                if  a  == name:
                    return self.nc.variables[a]


        return None

    def gettime(self,ncdataset):
        """
        Check for standard name. If that is not present assume the variable name
        """

        for a in ncdataset.variables:
            if hasattr(self.nc.variables[a],'standard_name'):
                if 'time' in ncdataset.variables[a].standard_name:
                    return ncdataset.variables[a]
            elif hasattr(self.nc.variables[a],'units'):
                if 'since' in ncdataset.variables[a].units:
                    return ncdataset.variables[a]

        return None


    def getlon(self,ncdataset):
        """
        Check for standard name. If that is not present assume the variable name
        """

        for a in self.nc.variables:
            if hasattr(self.nc.variables[a],'standard_name'):
                if  self.nc.variables[a].standard_name == 'longitude':
                    return self.nc.variables[a]
            else:
                if a == 'longitude':
                    return self.nc.variables[a]

        return None


    def getheigth(self,ncdataset):
        """
        """

        for a in self.nc.variables:
            if hasattr(self.nc.variables[a],'standard_name'):
                if  self.nc.variables[a].standard_name == 'height':
                    return self.nc.variables[a]
            else:
                if a == 'height':
                    return self.nc.variables[a]

        return None


def readMap(fileName, fileFormat,logger):
    """
    ead geographical file into memory

    :param fileName: Name of the file to read
    :param fileFormat: Gdal format string
    :param logger: logger object
    :return: resX, resY, cols, rows, x, y, data, FillVal
    """


    #Open file for binary-reading

    mapFormat = gdal.GetDriverByName(fileFormat)
    mapFormat.Register()
    ds = gdal.Open(fileName)
    if ds is None:
        logger.error('Could not open ' + fileName + '. Something went wrong!! Shutting down')
        sys.exit(1)
    # Retrieve geoTransform info
    geotrans = ds.GetGeoTransform()
    originX = geotrans[0]
    originY = geotrans[3]
    resX    = geotrans[1]
    resY    = geotrans[5]
    cols = ds.RasterXSize
    rows = ds.RasterYSize
    x = linspace(originX+resX/2,originX+resX/2+resX*(cols-1),cols)
    y = linspace(originY+resY/2,originY+resY/2+resY*(rows-1),rows)
    # Retrieve raster
    RasterBand = ds.GetRasterBand(1) # there's only 1 band, starting from 1
    data = RasterBand.ReadAsArray(0,0,cols,rows)
    FillVal = RasterBand.GetNoDataValue()
    RasterBand = None
    del ds
    return resX, resY, cols, rows, x, y, data, FillVal


def writeMap(fileName, fileFormat, x, y, data, FillVal):
    """
    Write geographical data into file. Also replace NaN by FillVall

    :param fileName:
    :param fileFormat:
    :param x:
    :param y:
    :param data:
    :param FillVal:
    :return:
    """


    verbose = False
    gdal.AllRegister()
    driver1 = gdal.GetDriverByName('GTiff')
    driver2 = gdal.GetDriverByName(fileFormat)

    data[isnan(data)] = FillVal
    # Processing
    if verbose:
        print 'Writing to temporary file ' + fileName + '.tif'
        print "Output format: " + fileFormat
    # Create Output filename from (FEWS) product name and date and open for writing
    TempDataset = driver1.Create(fileName + '.tif',data.shape[1],data.shape[0],1,gdal.GDT_Float32)
    # Give georeferences
    xul = x[0]-(x[1]-x[0])/2
    yul = y[0]+(y[0]-y[1])/2

    TempDataset.SetGeoTransform( [ xul, x[1]-x[0], 0, yul, 0, y[1]-y[0] ] )
    # get rasterband entry
    TempBand = TempDataset.GetRasterBand(1)
    # fill rasterband with array
    TempBand.WriteArray(data,0,0)
    TempBand.FlushCache()
    TempBand.SetNoDataValue(FillVal)

    # Create data to write to correct format (supported by 'CreateCopy')
    if verbose:
        print 'Writing to ' + fileName + '.map'
    if fileFormat == 'GTiff':
        outDataset = driver2.CreateCopy(fileName, TempDataset, 0 ,options = ['COMPRESS=LZW'])
    else:
        outDataset = driver2.CreateCopy(fileName, TempDataset, 0)
    TempDataset = None
    outDataset = None
    if verbose:
        print 'Removing temporary file ' + fileName + '.tif'
    os.remove(fileName + '.tif');

    if verbose:
        print 'Writing to ' + fileName + ' is done!'



def configget(log,config,section,var,default):
    """   
    Gets a string from a config file (.ini) and returns a default value if
    the key is not found. If the key is not found it also sets the value 
    with the default in the config-file
    
    Input:
        - config - python ConfigParser object
        - section - section in the file
        - var - variable (key) to get
        - default - default string
        
    Returns:
        - string - either the value from the config file or the default value
    """
    

    try:
        ret = config.get(section, var)
    except:
        ret = default
        log.info( "returning default (" + str(default) + ") for " + section + ":" + var)
        configset(config,section,var,str(default), overwrite=False)
    

    return ret       

def configset(config,section,var,value, overwrite=False):
    """   
    Sets a string in the in memory representation of the config object
    Deos NOT overwrite existing values if overwrite is set to False (default)
    
    Input:
        - config - python ConfigParser object
        - section - section in the file
        - var - variable (key) to set
        - value - the value to set
        - overwrite (optional, default is False)
   
    Returns:
        - nothing
        
    """
    
    if not config.has_section(section):
        config.add_section(section)
        config.set(section,var,value)
    else:     
        if not config.has_option(section,var):
            config.set(section,var,value)
        else:
            if overwrite:
                config.set(section,var,value)

def iniFileSetUp(configfile):
    """
    Reads .ini file and sets default values if not present
    """
    # TODO: clean up wflwo specific stuff
    #setTheEnv(runId='runId,caseName='caseName)
    # Try and read config file and set default options
    config = ConfigParser.SafeConfigParser()
    config.optionxform = str
    config.read(configfile)
    return config

def setlogger(logfilename,loggername, level=logging.INFO):
    """
    Set-up the logging system and return a logger object. Exit if this fails
    """

    try:
        #create logger
        logger = logging.getLogger(loggername)
        if not isinstance(level, int):
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(level)
        ch = logging.FileHandler(logfilename,mode='w')
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)
        #create formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        #add formatter to ch
        ch.setFormatter(formatter)
        console.setFormatter(formatter)
        #add ch to logger
        logger.addHandler(ch)
        logger.addHandler(console)
        logger.debug("File logging to " + logfilename)
        return logger
    except IOError:
        print "ERROR: Failed to initialize logger with logfile: " + logfilename
        sys.exit(2)

def closeLogger(logger, ch):
    """
    Closes the logger
    """
    logger.removeHandler(ch)
    ch.flush()
    ch.close()
    return logger, ch



def resample_grid(gridZ_in,Xin,Yin,Xout,Yout,method='nearest',FillVal=1E31):
    """
    Resample a regular grid be supplying original and new x, y row,col coordinates
    Missing values is set to 1E31, the PCRaster standard. If the output grid
    has a lower resolution the interpolation is done in two steps by first applying
    a moving window.

    :param gridZ_in: datablock of original data (e.g. from readMap)
    :param Xin: X-coordinates of all columns (e.g. from readMap)
    :param Yin: Y-coordinates of all columns (e.g. from readMap)
    :param Xout: X-coordinates of all columns in the new map (e.g. from readMap)
    :param Yout: Y-coordinates of all columns in the new map (e.g. from readMap)
    :param method: linear, nearest, [cubic, quintic <- switched off for now]
    :param FillVal: Value for the missing values

    :return: datablock of new grid.
    """
    
    # we need to sort the y data (must be ascending)
    # and thus flip the image
    Ysrt = sort(Yin)

    # First average if the output has a lower resolution than the input grid
    insize = min(diff(Xin))
    outsize = min(diff(Xout))
    #if insize < outsize:
    #    xsize = outsize/insize
    #    gridZ_in = ndimage.filters.percentile_filter(gridZ_in,50,size=xsize)

    if method in 'nearest linear':
        interobj = interpolate.RegularGridInterpolator((Ysrt,Xin), flipud(gridZ_in), method=method ,bounds_error=False,fill_value=float32(FillVal))
        _x, _y = meshgrid(Xout, Yout)
        yx_outpoints = transpose([_y.flatten(), _x.flatten()])

        # interpolate
        res = interobj(yx_outpoints)
        result = reshape(res, (len(Yout), len(Xout)))
        result[isnan(result)] = FillVal
    # elif method in 'cubic quintic':
    #     interobj = interpolate.interp2d(Xin, Ysrt, gridZ_in,  kind=method, bounds_error=False)
    #     res = interobj(Xout, Yout)
    #     result = reshape(res, (len(Yout), len(Xout)))
    #     result[isnan(result)] = FillVal
    #     res = flipud(res)
    else:
        raise ValueError("Interpolation method " + method + " not known.")

    #reshape to the new grid

    
    return result
