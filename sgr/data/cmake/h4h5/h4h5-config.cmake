#-----------------------------------------------------------------------------
# H4H5 Config file for compiling against H4H5 install directory
#-----------------------------------------------------------------------------
GET_FILENAME_COMPONENT (SELF_DIR "${CMAKE_CURRENT_LIST_FILE}" PATH)
GET_FILENAME_COMPONENT(_IMPORT_PREFIX "${SELF_DIR}" PATH)
GET_FILENAME_COMPONENT(_IMPORT_PREFIX "${_IMPORT_PREFIX}" PATH)
IF (NOT WIN32)
  GET_FILENAME_COMPONENT(_IMPORT_PREFIX "${_IMPORT_PREFIX}" PATH)
ENDIF (NOT WIN32)

#-----------------------------------------------------------------------------
# User Options
#-----------------------------------------------------------------------------
SET (HDF_ENABLE_PARALLEL OFF)
SET (HDF_BUILD_TOOLS     ON)
SET (HDF_ENABLE_JPEG_LIB_SUPPORT ON)
SET (HDF_ENABLE_Z_LIB_SUPPORT ON)
SET (HDF_ENABLE_SZIP_SUPPORT  ON)
SET (HDF_ENABLE_SZIP_ENCODING ON)
SET (BUILD_SHARED_LIBS    OFF)
SET (HDF_PACKAGE_EXTLIBS ON)

#-----------------------------------------------------------------------------
# Directories
#-----------------------------------------------------------------------------
SET (H4H5_INCLUDE_DIRS "${_IMPORT_PREFIX}/include")

IF (HDF_BUILD_TOOLS)
  SET (H4H5_INCLUDE_DIR_TOOLS "${_IMPORT_PREFIX}/include")
ENDIF (HDF_BUILD_TOOLS)

#-----------------------------------------------------------------------------
# Version Strings
#-----------------------------------------------------------------------------
SET (H4H5_VERSION_STRING 2.2.2)
SET (H4H5_VERSION_MAJOR  2.2)
SET (H4H5_VERSION_MINOR  2)

#-----------------------------------------------------------------------------
# Don't include targets if this file is being picked up by another
# project which has already build H4H5 as a subproject
#-----------------------------------------------------------------------------
IF (NOT TARGET "h4h5")
  IF (HDF_ENABLE_JPEG_LIB_SUPPORT AND HDF_PACKAGE_EXTLIBS AND NOT TARGET "jpeg")
    INCLUDE (${SELF_DIR}/../JPEG/jpeg-targets.cmake)
  ENDIF (HDF_ENABLE_JPEG_LIB_SUPPORT AND HDF_PACKAGE_EXTLIBS AND NOT TARGET "jpeg")
  IF (HDF_ENABLE_Z_LIB_SUPPORT AND HDF_PACKAGE_EXTLIBS AND NOT TARGET "zlib")
    INCLUDE (${SELF_DIR}/../ZLIB/zlib-targets.cmake)
  ENDIF (HDF_ENABLE_Z_LIB_SUPPORT AND HDF_PACKAGE_EXTLIBS AND NOT TARGET "zlib")
  IF (HDF_ENABLE_SZIP_SUPPORT AND HDF_PACKAGE_EXTLIBS AND NOT TARGET "szip")
    INCLUDE (${SELF_DIR}/../SZIP/szip-targets.cmake)
  ENDIF (HDF_ENABLE_SZIP_SUPPORT AND HDF_PACKAGE_EXTLIBS AND NOT TARGET "szip")
  IF (HDF_PACKAGE_EXTLIBS AND NOT TARGET "hdf")
    INCLUDE (${SELF_DIR}/../hdf4/hdf4-targets.cmake)
  ENDIF (HDF_PACKAGE_EXTLIBS AND NOT TARGET "hdf")
  IF (HDF_PACKAGE_EXTLIBS AND NOT TARGET "hdf5")
    INCLUDE (${SELF_DIR}/../hdf5/hdf5-targets.cmake)
  ENDIF (HDF_PACKAGE_EXTLIBS AND NOT TARGET "hdf5")
  INCLUDE (${SELF_DIR}/h4h5-targets.cmake)
  SET (H4H5_LIBRARIES "h4toh5")
ENDIF (NOT TARGET "h4h5")
