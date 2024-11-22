# Commands to set up the environment before running or building Dsends.
#
# This file is source'd by a top-level setup.sh
# (see the file "DsendsMASPkg.HowToBuild")
#

# Make sure all environment variables are defined

# Path to the Dsends Pkg
echo "Path to Dsends Package: ${DSENDS_ROOT}"

# Path to Base Package (if any)
echo "Path to Base Package: ${DSENDS_BASE_PKG}"

# Path to COTS
echo "Path to COTS: ${COTS_PATH}"

echo "Path to COTS Python libraries: ${COTS_PYTHONPATH}"

# Path to Dsends DTPS
echo "Path to DTPS: ${DTPS_PATH}"

# Path to extra Perl libraries
echo "Path to Perl libraries: ${PERL5LIB}"

# Path to HDF5 libraries
echo "Path to HDF5 libraries: ${HDF5_PATH}"

# Path to CSPICE libraries
echo "Path to CSPICE libraries: ${CSPICE_PATH}"


# Path to BOOST libraries
echo "Path to BOOST libraries: ${BOOST_PATH}"

# Path to OIS libraries
echo "Path to OIS libraries: ${OIS_PATH}"

# Path to LCM libraries
echo "Path to LCM libraries: ${LCM_PATH}"

# Path to OGRE libraries
echo "Path to OGRE libraries: ${OGRE_PATH}"

# Path to SWIG .i files
echo "Path to SWIG .i files: ${SWIG_INC_PATH}"


########################################################

# Path to DTPS python area (cheetah, configobj)
setenv DTPS_PYTHONPATH ${DTPS_PATH}/python

# Path to mlabwrap python area
setenv MLABWRAP_PATH ${DTPS_PATH}/mlabwrap-1.0/build/lib.linux-i686-2.6

setenv YAM_SITE  DsendsCompass
setenv YAM_TARGET i486-rh9-linux
setenv YAM_ROOT  ${DSENDS_ROOT}
