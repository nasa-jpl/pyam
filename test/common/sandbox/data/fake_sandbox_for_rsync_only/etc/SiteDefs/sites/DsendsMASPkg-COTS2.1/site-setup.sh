# Commands to set up the environment before running or building Dsends.
#
# This file is source'd by a top-level setup.sh
# (see the file "DsendsMASPkg.HowToBuild")
#

# Make sure all environment variables are defined

# Path to the DsendsMASPkg
echo "DsendsMASPkg-COTS2.1: ${DSENDS_ROOT}"

# Path to COTS
echo "Path to COTS: ${COTS_PATH}"

echo "Path to COTS Python libraries: ${COTS_PYTHONPATH}"

# Path to Dsends DTPS
echo "Path to DTPS: ${DTPS_PATH}"

# Path to Matlab .so area
echo "Path to MatLab libraries: ${MATLAB_LIB_PATH}"

# Path to Matlab bin area
echo "Path to matlab executable: ${MATLAB_BINDIR}/matlab"

# Path to MASL root directory
echo "Path to MASL root directory: ${MAS_LOAD_POINT}"

# Path to MASL libraries
echo "Path to MASL libraries: ${MASL_LIB_PATH}"




########################################################

# Path to DTPS python area (cheetah, configobj)
setenv DTPS_PYTHONPATH ${DTPS_PATH}/python

# Path to mlabwrap python area
setenv MLABWRAP_PATH ${DTPS_PATH}/mlabwrap-0.9.1/build/lib.linux-i686-2.5

setenv YAM_SITE  DsendsMASPkg-COTS2.1
setenv YAM_TARGET i486-rh9-linux
