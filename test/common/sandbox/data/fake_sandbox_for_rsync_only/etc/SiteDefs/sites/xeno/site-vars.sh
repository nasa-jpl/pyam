# This file is used by Drun
# If you edit this file, also edit the site-config* files which
# are used by gmake.

# PYTHONPATH=/usr/local/lib/python2.4/site-packages:/home/jain/python:${PYTHONPATH}

XENO_COTS_PATH=/home/hockney/COTS/0.9-20060120C
export XENO_COTS_PATH

LD_LIBRARY_PATH=${XENO_COTS_PATH}/lib:${LD_LIBRARY_PATH}

PYTHONPATH=${XENO_COTS_PATH}/lib/python2.4/site-packages:${PYTHONPATH}

# Path to altgraph
PYTHONPATH=${PYTHONPATH}:/home/cslim/Dsends/COTS0.9/python

# Path to configobj
PYTHONPATH=${PYTHONPATH}:/group/monte/development/rh8/tools.lim/lib/python2.4/site-packages/pythonutils

# Path to Cheetah
PYTHONPATH=${PYTHONPATH}:/group/monte/development/rh8/tools.lim/lib/python2.4/site-packages

# Path to mlabwrap python libs and Matlab .so area
PYTHONPATH=${PYTHONPATH}:/home/cslim/Dsends/COTS0.9/python/mlabwrap-0.9.1/build/lib.linux-i686-2.4
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/nav/common/sw/linux/redhat/8.0/matlab/14.2/bin/glnx86


QTDIR=${XENO_COTS_PATH}

PATH=${YAM_ROOT}/bin:${YAM_ROOT}/bin/${YAM_TARGET}:${XENO_COTS_PATH}/bin:${PATH}

MAS_LOAD_POINT=/nav/common/sw/linux/redhat/8.0/masl
export MAS_LOAD_POINT
