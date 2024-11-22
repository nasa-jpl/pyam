# Commands to set up the environment before running or building Dsends.
#
# This file is source'd by a top-level setup.sh
# (see the file "DsendsMASPkg.HowToBuild")
#

# Make sure all environment variables are defined

# Path to the DsendsMASPkg
echo "Path to Dsends Package: ${DSENDS_ROOT}"

# Path to Base Package (if any)
echo "Path to Base Package: ${DSENDS_BASE_PKG}"

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
#echo "Path to MASL root directory: ${MAS_LOAD_POINT}"

# Path to MASL libraries
echo "Path to MASL libraries: ${MASL_LIB_PATH}"

# Path to extra Perl libraries
echo "Path to Perl libraries: ${PERL5LIB}"

# Path to HDF5 libraries
echo "Path to HDF5 libraries: ${HDF5_PATH}"

# Path to CSPICE libraries
echo "Path to CSPICE libraries: ${CSPICE_PATH}"


# Path to BOOST libraries
echo "Path to BOOST libraries: ${BOOST_PATH}"

########################################################

# Path to DTPS python area (cheetah, configobj)
setenv DTPS_PYTHONPATH ${DTPS_PATH}/python

# Path to mlabwrap python area
setenv MLABWRAP_PATH ${DTPS_PATH}/mlabwrap-1.0/build/lib.linux-i686-2.6

setenv YAM_SITE  DsendsMASPkg-COTS3.0
setenv YAM_TARGET i486-rh9-linux
setenv YAM_ROOT  ${DSENDS_ROOT}
