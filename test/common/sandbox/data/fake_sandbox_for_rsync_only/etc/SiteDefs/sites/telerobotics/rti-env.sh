. ${YAM_ROOT}/etc/SiteDefs/sites/rti-env.sh

if [ "$OS_ARCH" = "sparcSol2.5" ]; then
    STETHOSCOPEHOME=/home/atbe/pkgs/src/rti/scope.5.0d
    RTILIBHOME=/home/atbe/pkgs/src/rti/rtilib.3.7l
#    NDDSHOME=/home/rti/ndds.1.11q
#    PATH=${STETHOSCOPEHOME}/bin/${OS_ARCH}:${NDDSHOME}/bin/${OS_ARCH}:${PATH}
    PATH=${STETHOSCOPEHOME}/bin/${OS_ARCH}:${PATH}
fi

if [ "$OS_ARCH" = "sparcSol2.8" ]; then
#    STETHOSCOPEHOME=/home/atbe/pkgs/src/rti/scope.5.0d
    STETHOSCOPEHOME=/home/atbe/pkgs/src/rti/scope.7.0f
#    RTILIBHOME=/home/atbe/pkgs/src/rti/rtilib.3.7l
#    NDDSHOME=/home/rti/ndds.1.11q
#    PATH=${STETHOSCOPEHOME}/bin/${OS_ARCH}:${NDDSHOME}/bin/${OS_ARCH}:${PATH}
    PATH=${STETHOSCOPEHOME}/bin/${OS_ARCH}:${PATH}
    export PATH
    LD_LIBRARY_PATH=${STETHOSCOPEHOME}/bin/${OS_ARCH}:${LD_LIBRARY_PATH}
    LM_LICENSE_FILE=/v/licenses/RTID/license.dat
    export LM_LICENSE_FILE
fi

if [ "$OS_ARCH" = "mipsIRIX6.4" ]; then
    STETHOSCOPEHOME=/home/atbe/pkgs/src/rti/scope.5.3b-irix6.5
#    RTILIBHOME=/home/rti/rtilib.3.7l
#    NDDSHOME=/home/rti/ndds.1.11q
    PATH=${STETHOSCOPEHOME}/bin/${OS_ARCH}:${PATH}
fi

if [ "$OS_ARCH" = "mipsIRIX6.4" ]; then
    STETHOSCOPEHOME=/home/atbe/pkgs/src/rti/scope.5.3b-irix6.5
#    RTILIBHOME=/home/rti/rtilib.3.7l
#    NDDSHOME=/home/rti/ndds.1.11q
    PATH=${STETHOSCOPEHOME}/bin/${OS_ARCH}:${PATH}
fi

if [ "$OS_ARCH" = "i86Linux2.4" ]; then
    STETHOSCOPEHOME=/home/atbe/pkgs/src/rti/scope.7.0c
#    RTILIBHOME=/home/rti/rtilib.3.7l
#    NDDSHOME=/home/rti/ndds.1.11q
    PATH=${STETHOSCOPEHOME}/bin/${OS_ARCH}:${PATH}
    # need to do this for Scope 7.0c on Linux so it can find the
    # Qt libraries needed by the binary
    LD_LIBRARY_PATH=${STETHOSCOPEHOME}/bin/${OS_ARCH}:${LD_LIBRARY_PATH}
    LM_LICENSE_FILE=/v/licenses/RTID/license.dat
    export LM_LICENSE_FILE
fi
