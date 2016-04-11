import os
import sgr

try:
    from setuptools import setup
except ImportError:
    from distutils.core import   setup
from setuptools import find_packages
here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()


try:
    import netCDF4
except:
    print("Could not import netCDF4, make sure it is installed")

try:
    import hdf5
except:
    print("Could not import hdf5, make sure it is installed")

datadir = os.path.join('sgr','data')
datafiles = [(d, [os.path.join(d,f) for f in files])
    for d, folders, files in os.walk(datadir)]

print datafiles

# Source dist
setup(name='sgr',
      version= sgr.__version__ + '-' + sgr.__release__,
      packages=['sgr'],
      package_dir={'sgr': 'sgr'},
      author='A.I.J.M. van Dijk/J. Schellekens',
      author_email='albert.vandijk@anu.edu.au/jaap.schellekens@deltares.nl',
      url='http://not yet',
      license="GPL",
      scripts=[''],
      description='Satellite Gauging Reaches',
      data_files = datafiles,
)