# This file is used by Drun
# If you edit this file, also edit the site-config* files which
# are used by gmake.

# Dsends Package Major Version
# This is used by EDL/python/Dsends.py to determine which version
# of Dsends is being used. Should match value in site-config*
DSENDS_VERSION=R4
export DSENDS_VERSION

PATH=${YAM_ROOT}/bin:${YAM_ROOT}/bin/${YAM_TARGET}:${COTS_PATH}/bin:${PATH}

PYTHONPATH=${DTPS_PYTHONPATH}:${MLABWRAP_PATH}:${PYTHONPATH}:${COTS_PYTHONPATH}

LD_LIBRARY_PATH=${COTS_PATH}/lib:${LD_LIBRARY_PATH}:${MATLAB_LIB_PATH}:${HDF5_PATH}/lib:${BOOST_PATH}/lib


#PATH=${YAM_ROOT}/bin:${YAM_ROOT}/bin/${YAM_TARGET}:${DSENDS_BASE_PKG}/bin:${DSENDS_BASE_PKG}/bin/${YAM_TARGET}:${COTS_PATH}/bin:${PATH}

#PYTHONPATH=${DSENDS_BASE_PKG}/lib/${YAM_TARGET}/PYTHON:${DSENDS_BASE_PKG}/lib/PYTHON:${DTPS_PYTHONPATH}:${MLABWRAP_PATH}:${PYTHONPATH}:${COTS_PYTHONPATH}

#LD_LIBRARY_PATH=${DSENDS_BASE_PKG}/lib/${YAM_TARGET}:${DSENDS_BASE_PKG}/lib/${YAM_TARGET}/TCLPKG:${DSENDS_BASE_PKG}/lib/${YAM_TARGET}/PYTHON:${COTS_PATH}/lib:${LD_LIBRARY_PATH}:${MATLAB_LIB_PATH}:${HDF5_PATH}/lib
