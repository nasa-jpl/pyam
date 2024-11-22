# This file is used by Drun
# If you edit this file, also edit the site-config* files which
# are used by gmake.


PATH=${YAM_ROOT}/bin:${YAM_ROOT}/bin/${YAM_TARGET}:${COTS_PATH}/bin:${PATH}
PYTHONPATH=${DTPS_PYTHONPATH}:${MLABWRAP_PATH}:${PYTHONPATH}:${COTS_PYTHONPATH}
LD_LIBRARY_PATH=${COTS_PATH}/lib:${LD_LIBRARY_PATH}:${MATLAB_LIB_PATH}
