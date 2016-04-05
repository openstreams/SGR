#
# To be used by projects that make use of Cmakeified h4toh5 tools 2.2.2
#

#
# Find the H4H5 includes and get all installed H4H5 library settings from
# H4H5-config.cmake file : Requires a CMake compatible H4H5-1.8.5 or later 
# for this feature to work. The following vars are set if H4H5 is found.
#
# H4H5_FOUND               - True if found, otherwise all other vars are undefined
# H4H5_INCLUDE_DIR         - The include dir for main *.h files
# H4H5_VERSION_STRING      - full version (e.g. 2.2.2)
# H4H5_VERSION_MAJOR       - major part of version (e.g. 2.2)
# H4H5_VERSION_MINOR       - minor part (e.g. 2)
# 
# The following boolean vars will be defined
# H4H5_ENABLE_PARALLEL - 1 if H4H5 parallel supported
# H4H5_BUILD_TOOLS     - 1 if H4H5 was compiled with tools on
# 
# Target names that are valid (depending on enabled options)
# will be the following
#
# H4H5              : H4H5 C library
# H4H5_tools        : the tools library
# 
# To aid in finding H4H5 as part of a subproject set
# H4H5_ROOT_DIR_HINT to the location where h4h5-config.cmake lies

INCLUDE (SelectLibraryConfigurations)
INCLUDE (FindPackageHandleStandardArgs)

# The HINTS option should only be used for values computed from the system.
SET (_H4H5_HINTS
    $ENV{HOME}/.local
    $ENV{H4H5_ROOT}
    $ENV{H4H5_ROOT_DIR_HINT}
)
# Hard-coded guesses should still go in PATHS. This ensures that the user
# environment can always override hard guesses.
SET (_H4H5_PATHS
    $ENV{HOME}/.local
    $ENV{H4H5_ROOT}
    $ENV{H4H5_ROOT_DIR_HINT}
    /usr/lib/h4h5
    /usr/share/h4h5
    /usr/local/h4h5
    /usr/local/h4h5/share
)

FIND_PATH (H4H5_ROOT_DIR "h4h5-config.cmake"
    HINTS ${_H4H5_HINTS}
    PATHS ${_H4H5_PATHS}
    PATH_SUFFIXES
        cmake/h4h5
        lib/cmake/h4h5
        share/cmake/h4h5
)

MESSAGE(STATUS "H4H5_ROOT_DIR is ${H4H5_ROOT_DIR}")
FIND_PATH (H4H5_INCLUDE_DIRS "h4toh5.h"
    HINTS ${_H4H5_HINTS}
    PATHS ${_H4H5_PATHS}
    PATH_SUFFIXES
        include
        Include
)
MESSAGE(STATUS "H4H5_INCLUDE_DIRS is ${H4H5_INCLUDE_DIRS}")

# For backwards compatibility we set H4H5_INCLUDE_DIR to the value of
# H4H5_INCLUDE_DIRS
SET ( H4H5_INCLUDE_DIR "${H4H5_INCLUDE_DIRS}" )

IF (H4H5_INCLUDE_DIR)
  SET (H4H5_FOUND "YES")
  INCLUDE (${H4H5_ROOT_DIR}/h4h5-config.cmake)
  MESSAGE(STATUS "H4H5_FOUND is ${H4H5_FOUND}")
ENDIF (H4H5_INCLUDE_DIR)
