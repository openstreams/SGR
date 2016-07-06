from distutils.core import setup
from bbfreeze import Freezer
import sgr
import ctypes,glob,os,shutil, matplotlib

def dependencies_for_freeezing():
	import netCDF4_utils


nrbits = str(ctypes.sizeof(ctypes.c_voidp) * 8)


thename = "sgr"+ '-'+nrbits
f = Freezer("sgr"+'-'+nrbits,includes = ['h5py','h5py.*','scipy', 'scipy.integrate', 'scipy.special.*',\
                                         'scipy.linalg.*','scipy.special._ufuncs_cxx',\
                                         'scipy.sparse.csgraph._validation'])
f.addScript("sgr/__init__.py")
f.addScript("sgr/sgr_main.py")

f()    # starts the freezing process


data_files=matplotlib.get_py2exe_datafiles()
gdaldata = os.getenv("GDAL_DATA")
data_files.append(("./gdal-data", glob.glob(gdaldata + "/*.*")))

data_files.append(("./sgr/convert", glob.glob('sgr/convert' + "/*.*")))
data_files.append(("./sgr/data", glob.glob('sgr/data' + "/*.*")))

print data_files
print "Copying extra data files..."
for dirr in data_files:
    timake = os.path.join(thename ,dirr[0])
    print timake
    if not os.path.exists(timake):
        os.makedirs(timake)
    for tocp in dirr[1]:
        print tocp
        shutil.copy(tocp,timake)
