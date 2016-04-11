__all__ = ["utils","get_data","modis_waterfrac","sgr_data"]

__author__ = 'van Dijk/Schellekens'
__version__ = '0.1'
__release__ = "2016"



import sys
import os

config = None

if hasattr(sys, "frozen"):
    _ROOT = os.path.abspath(os.path.dirname(__file__)).split("library.zip")[0]
    os.environ['GDAL_DATA'] = os.path.join(_ROOT,'gdal-data')
else:
    _ROOT = os.path.abspath(os.path.dirname(__file__))

import osgeo.gdal as gdal

def get_path_from_root(path):
    return os.path.join(_ROOT, path)
    
    