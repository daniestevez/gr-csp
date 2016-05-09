INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_CSP csp)

FIND_PATH(
    CSP_INCLUDE_DIRS
    NAMES csp/api.h
    HINTS $ENV{CSP_DIR}/include
        ${PC_CSP_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    CSP_LIBRARIES
    NAMES gnuradio-csp
    HINTS $ENV{CSP_DIR}/lib
        ${PC_CSP_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(CSP DEFAULT_MSG CSP_LIBRARIES CSP_INCLUDE_DIRS)
MARK_AS_ADVANCED(CSP_LIBRARIES CSP_INCLUDE_DIRS)

