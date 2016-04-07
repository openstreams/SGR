#-----------------------------------------------------------------------------
# H4H5 Version file for install directory
#-----------------------------------------------------------------------------

SET (PACKAGE_VERSION 2.2.2)

IF ("${PACKAGE_FIND_VERSION_MAJOR}" EQUAL 2)

  # exact match for version .2
  IF ("${PACKAGE_FIND_VERSION_MINOR}" EQUAL 2)

    # compatible with any version 2.2.x
    SET (PACKAGE_VERSION_COMPATIBLE 1) 
    
    IF ("${PACKAGE_FIND_VERSION_PATCH}" EQUAL 2)
      SET (PACKAGE_VERSION_EXACT 1)    

      IF ("${PACKAGE_FIND_VERSION_TWEAK}" EQUAL )
        # not using this yet
      ENDIF ("${PACKAGE_FIND_VERSION_TWEAK}" EQUAL )
      
    ENDIF ("${PACKAGE_FIND_VERSION_PATCH}" EQUAL 2)
    
  ENDIF ("${PACKAGE_FIND_VERSION_MINOR}" EQUAL 2)
ENDIF ("${PACKAGE_FIND_VERSION_MAJOR}" EQUAL 2)


