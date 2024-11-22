# site specific environment variables

# set up variables for running VxSim
if [ "X$VXWORKS_HOST_TARGET" = "Xvxsim0" ]; then
  WIND_BASE=/home/atbe/pkgs/src/vxWorks/wind2.0_sim
  VX_IPADDR=127.0.1.0
  VX_TARGET_TYPE=sun4-vxsim2.0
elif [ "X$VXWORKS_HOST_TARGET" = "Xdlab0" ]; then
  WIND_BASE=/home/atbe/pkgs/src/vxWorks/wind-2.0.2-ppc
  VX_IPADDR=128.149.110.49
  VX_TARGET_TYPE=ppc-vxworks5.4
fi

if [ "X$VXWORKS_HOST_TARGET" != "X" ]; then
  export WIND_BASE
  export WIND_HOST_TYPE
  WIND_HOST_TYPE=sun4-solaris2
  export WIND_REGISTRY
  WIND_REGISTRY=tara.jpl.nasa.gov

  PATH=${PATH}:${WIND_BASE}/host/${WIND_HOST_TYPE}/bin

  VX_TCL_LIBRARY=/home/atbe/pkgs/src/vxTcl/vxTcl8.0-sun4-vxsim2.0/library
  export VX_TCL_LIBRARY

  export VX_IPADDR
  export VX_TARGET_TYPE
fi

TK_PKGLIBRARY=/home/atbe/pkgs/lib/${YAM_TARGET}-shared/libtk8.3.so
TIX_PKGLIBRARY=/home/atbe/pkgs/lib/${YAM_TARGET}-shared/libtix8.2.so
export TK_PKGLIBRARY
export TIX_PKGLIBRARY

if [ "$YAM_TARGET" = "sparc-sunos5.7" ]; then
    export GRAPHVIZ_VERSION
    GRAPHVIZ_VERSION=1.7.7
    export GRAPHVIZ_LIBDIR
    GRAPHVIZ_LIBDIR=/home/atbe/pkgs/src/graphviz/graphviz-${GRAPHVIZ_VERSION}-sparc-sunos5.7/install/lib/graphviz
fi

if [ "$YAM_TARGET" = "sparc-sunos5.8" ]; then
    export GRAPHVIZ_VERSION
    GRAPHVIZ_VERSION=1.7.7
    export GRAPHVIZ_LIBDIR
    GRAPHVIZ_LIBDIR=/home/atbe/pkgs/src/graphviz/graphviz-${GRAPHVIZ_VERSION}-sparc-sunos5.7/install/lib/graphviz
fi

if [ "$YAM_TARGET" = "mips-irix6.5" ]; then
    export GRAPHVIZ_VERSION
    GRAPHVIZ_VERSION=1.8.2
    export GRAPHVIZ_LIBDIR
    GRAPHVIZ_LIBDIR=/home/atbe/pkgs/src/graphviz/graphviz-${GRAPHVIZ_VERSION}/mips-irix6.5/install/lib/graphviz
fi

if [ "$YAM_TARGET" = "i486-linux" ]; then
    export GRAPHVIZ_VERSION
    GRAPHVIZ_VERSION=1.8.10
    export GRAPHVIZ_LIBDIR
    GRAPHVIZ_LIBDIR=/usr/lib/graphviz
    TK_PKGLIBRARY=/usr/lib/libtk8.3.so
    TIX_PKGLIBRARY=/usr/lib/libtix.so
fi

if [ "$YAM_TARGET" = "i486-rh80-linux" ]; then
    export GRAPHVIZ_VERSION
    GRAPHVIZ_VERSION=1.8.10
    export GRAPHVIZ_LIBDIR
    GRAPHVIZ_LIBDIR=/usr/lib/graphviz
    TK_PKGLIBRARY=/usr/lib/libtk8.3.so
    TIX_PKGLIBRARY=/usr/lib/libtix.so
fi

if [ "$YAM_TARGET" = "i486-rh9-linux" ]; then
    export GRAPHVIZ_VERSION
    GRAPHVIZ_VERSION=1.9
    export GRAPHVIZ_LIBDIR
    GRAPHVIZ_LIBDIR=/usr/lib/graphviz
    TK_PKGLIBRARY=/usr/lib/libtk8.3.so
	TIX_PKGLIBRARY=/usr/lib/libtix8.1.8.3.so
fi

if [ "$YAM_TARGET" = "i486-suse73-linux" ]; then
    export GRAPHVIZ_VERSION
    GRAPHVIZ_VERSION=1.9
    export GRAPHVIZ_LIBDIR
    GRAPHVIZ_LIBDIR=/usr/lib/graphviz
    TK_PKGLIBRARY=/usr/lib/libtk8.3.so
	TIX_PKGLIBRARY=/usr/lib/libtix8.1.8.3.so
	LD_LIBRARY_PATH=/opt/experimental/lib:${LD_LIBRARY_PATH}
fi

if [ "$YAM_TARGET" = "i486-cygwin" ]; then
    TK_PKGLIBRARY=/usr/local/tcl8.3/bin/tk83.dll
    TIX_PKGLIBRARY=/usr/local/tcl8.3/bin/tix8183.dll
fi

# tcl-sql (tcl interface to MySQL)
if [ "$YAM_TARGET" = "i486-linux" ]; then
  export TCLSQL_LIBDIR
  TCLSQL_LIBDIR=/home/atbe/pkgs/src/tcl-sql/tcl-sql-200000114
fi

#======================================
# HLA stuff

RTI_RID_FILE=${YAM_ROOT}/src/MsfRoamsComponent/RTI.rid
if [ "$USER" = "wagnermd" ]; then
  RTI_RID_FILE=${YAM_ROOT}/src/MsfRoamsComponent/RTI.rid-wagnermd
fi
if [ "$USER" = "cneukom" ]; then
  RTI_RID_FILE=/home/cneukom/MSF/RTI.rid.chris
fi
export RTI_RID_FILE

export HLA_RTI_HOME=/home/wagnermd/HLA/RTI-1.3NGv6
export HLA_RTI_BUILD_TYPE=Linux-rh7.2-i386-gcc-3.0.2-opt-mt
export MSF_HOME=/home/wagnermd/MSF2/MSF
export MSF_FEDFILE_PATH=${MSF_HOME}/COMv2

LD_LIBRARY_PATH=${MSF_HOME}/lib/Linux:${HLA_RTI_HOME}/${HLA_RTI_BUILD_TYPE}/lib:${LD_LIBRARY_PATH}
