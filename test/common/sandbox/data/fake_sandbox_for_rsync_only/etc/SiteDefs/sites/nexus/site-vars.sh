# This file is used by Drun
# If you edit this file, also edit the site-config* files which
# are used by gmake.

# PYTHONPATH=/usr/local/lib/python2.4/site-packages:/home/jain/python:${PYTHONPATH}


NEXUS_COTS_PATH=/home/jrevans/local/COTS/0.9-20060120B
export NEXUS_COTS_PATH

LD_LIBRARY_PATH=${NEXUS_COTS_PATH}/lib:${LD_LIBRARY_PATH}

# PYTHONPATH=${NEXUS_COTS_PATH}/lib/python2.4/site-packages:${PYTHONPATH}
PYTHONPATH=${NEXUS_COTS_PATH}/lib/python2.4/site-packages:${PYTHONPATH}

# Path to altgraph
PYTHONPATH=${PYTHONPATH}:/nav/common/sw/linux/redhat/8.0/Dsends/python

# Path to configobj
PYTHONPATH=${PYTHONPATH}:/group/monte/development/rh8/tools.lim/lib/python2.4/site-packages/pythonutils

# Path to Cheetah
PYTHONPATH=${PYTHONPATH}:/group/monte/development/rh8/tools.lim/lib/python2.4/site-packages

# Path to mlabwrap python libs and Matlab .so area
PYTHONPATH=${PYTHONPATH}:/nav/common/sw/linux/redhat/8.0/Dsends/python/mlabwrap-0.9.1/build/lib.linux-i686-2.4
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/nav/common/sw/linux/redhat/8.0/matlab/14.2/bin/glnx86


QTDIR=${NEXUS_COTS_PATH}

# PATH=${NEXUS_COTS_PATH}/bin:${PATH}
PATH=${YAM_ROOT}/bin:${YAM_ROOT}/bin/${YAM_TARGET}:${NEXUS_COTS_PATH}/bin:${PATH}
