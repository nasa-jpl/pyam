. ${YAM_ROOT}/etc/SiteDefs/sites/rti-env.sh

# add site specific customization and overrides below
#RTIHOME=/afs/jpl.nasa.gov/group/msa/private/v3/seq/cm/archive/hsslib
RTIHOME=/home/cm/CM/hsslib
STETHOSCOPEHOME=${RTIHOME}/scope.5.0d
RTILIBHOME=${RTIHOME}/rtilib.3.7l
RTI_LICENSE_FILE=${RTIHOME}/lm.1.2b/bin/sparcSol2.5/license.dat

PATH=${STETHOSCOPEHOME}/bin/${OS_ARCH}:${PATH}
