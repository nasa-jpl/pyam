# Commands to set up the environment before running or building Dsends.
#
# This file is source'd by a top-level setup.sh
# (see the file "DsendsExternal.HowToBuild")
#

# Make sure all environment variables are defined

# Path to the Dsends package
echo "DsendsExternal: ${DSENDS_ROOT}"

# Path to COTS
echo "Path to COTS: ${COTS_PATH}"

echo "Path to COTS Python libraries: ${COTS_PYTHONPATH}"

# Path to Dsends DTPS
echo "Path to DTPS: ${DTPS_PATH}"

# Path to Matlab .so area
echo "Path to MatLab libraries: ${MATLAB_LIB_PATH}"

# Path to Matlab bin area
echo "Path to matlab executable: ${MATLAB_BINDIR}/matlab"

# Path to CSpice libraries
echo "Path to CSpice: ${CSPICE_DIR}"

# Path to mlabwrap libraries
echo "Path to mlabwrap: ${MLABWRAP_PATH}"

# Path to HDF5 libraries
echo "Path to HDF5: ${HDF5_DIR}"


########################################################

setenv YAM_SITE  DsendsExternal
setenv YAM_TARGET i486-rh9-linux

# Path to DTPS python area (cheetah, configobj)
setenv DTPS_PYTHONPATH ${DTPS_PATH}/python
