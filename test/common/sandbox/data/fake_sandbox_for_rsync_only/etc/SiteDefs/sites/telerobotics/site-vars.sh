# site specific environment variables

# destination directory for Depydoc generated docs
DEPYDOCS_DIR=/home/dlab/repo/www/DLabDocs/Python
export DEPYDOCS_DIR

# environment variables for doctest documentation generation
DOCTESTDOCS_DIR=/home/dlab/repo/www/DLabDocs/doctests
DOCTESTLIST=/home/atbe/sim-utils/repo/lib/doctestList.py
export DOCTESTDOCS_DIR
export DOCTESTLIST


VALGRIND_SUPP_FILE=/home/atbe/sim-utils/lib/valgrind-supp.file
export VALGRIND_SUPP_FILE

# vehicle graphics model files
CHARIOTROVER_IVDIR=/home/fornat/chariot1G/
export CHARIOTROVER_IVDIR
K10ROVER_IVDIR=/home/fornat/K10/ivFiles/
export K10ROVER_IVDIR

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
  WIND_REGISTRY=lorentz.jpl.nasa.gov

  PATH=${PATH}:${WIND_BASE}/host/${WIND_HOST_TYPE}/bin

  export VX_IPADDR
  export VX_TARGET_TYPE
fi

export GNOCL_VERSION
export GNOCL_LIBDIR

if [ "$YAM_TARGET" = "sparc-sunos5.7" ]; then
    GRAPHVIZ_VERSION=1.7.7
    GRAPHVIZ_LIBDIR=/home/atbe/pkgs/src/graphviz/graphviz-${GRAPHVIZ_VERSION}-sparc-sunos5.7/install/lib/graphviz
    export GRAPHVIZ_VERSION
    export GRAPHVIZ_LIBDIR
fi

if [ "$YAM_TARGET" = "sparc-sunos5.9" ]; then
    MATLAB_LIBDIR=/v/matlab/extern/lib/sol2
    export MATLAB_LIBDIR
    MATLAB_BINDIR=/v/matlab/bin
    export MATLAB_BINDIR
    GRAPHVIZ_VERSION=2.2
    GRAPHVIZ_LIBDIR=/home/atbe/pkgs/sparc-sunos5.9/stow/graphviz-${GRAPHVIZ_VERSION}/lib/graphviz
    export GRAPHVIZ_VERSION
    export GRAPHVIZ_LIBDIR

    GNOCL_VERSION=0.5.18
    if  [ "X$GNOCL_LIBDIR" = "X" ]; then
	GNOCL_LIBDIR=/home/atbe/pkgs/src/gtk/gnocl-0.5.18-sparc-sunos5.9/src
    fi
fi

if [ "$YAM_TARGET" = "sparc-sunos5.8" ]; then
    GRAPHVIZ_VERSION=1.7.7
    GRAPHVIZ_LIBDIR=/home/atbe/pkgs/src/graphviz/graphviz-${GRAPHVIZ_VERSION}-sparc-sunos5.7/install/lib/graphviz
    export GRAPHVIZ_VERSION
    export GRAPHVIZ_LIBDIR
fi

if [ "$YAM_TARGET" = "mips-irix6.5" ]; then
    GRAPHVIZ_VERSION=1.8.2
    GRAPHVIZ_LIBDIR=/home/atbe/pkgs/src/graphviz/graphviz-${GRAPHVIZ_VERSION}/mips-irix6.5/install/lib/graphviz
    export GRAPHVIZ_VERSION
    export GRAPHVIZ_LIBDIR
    export POVRAY_BIN
    POVRAY_BIN=/home/atbe/pkgs/mips-irix6.5/bin/povray
fi

if [ "$YAM_TARGET" = "i486-linux" ]; then
    GRAPHVIZ_VERSION=1.8.10
    GRAPHVIZ_LIBDIR=/usr/lib/graphviz
    export GRAPHVIZ_VERSION
    export GRAPHVIZ_LIBDIR
    GNOCL_VERSION=0.5.13
    GNOCL_LIBDIR=/home/atbe/pkgs/src/gtk/gnocl-$GNOCL_VERSION-i486-linux/src
fi

if [ "$YAM_TARGET" = "i486-rh80-linux" ]; then
    GRAPHVIZ_VERSION=1.8.10
    GRAPHVIZ_LIBDIR=/usr/lib/graphviz
    export GRAPHVIZ_VERSION
    export GRAPHVIZ_LIBDIR
fi

if [ "$YAM_TARGET" = "i486-rh9-linux" ]; then
    MATLAB_LIBDIR=/home/atbe/pkgs/src/matlab/matlab-12.1-linux/extern/lib/glnx86/mlabwrap
    export MATLAB_LIBDIR
    MATLAB_BINDIR=/home/atbe/pkgs/src/matlab/matlab-12.1-linux/bin
    export MATLAB_BINDIR
    GRAPHVIZ_VERSION=1.9
    GRAPHVIZ_LIBDIR=/usr/lib/graphviz
    export GRAPHVIZ_VERSION
    export GRAPHVIZ_LIBDIR

    export POVRAY_BIN
    POVRAY_BIN=/usr/local/bin/povray

    GNOCL_VERSION=0.5.18
    if  [ "X$GNOCL_LIBDIR" = "X" ]; then
#	GNOCL_LIBDIR=/home/atbe/pkgs/src/gtk/gnocl-0.5.17-released-linux/src
	GNOCL_LIBDIR=/home/atbe/pkgs/src/gtk/gnocl-0.5.18-i486-rh9-linux/src
    fi
fi


if [ "$YAM_TARGET" = "i486-fedora13-linux" ]; then
    LCM_DIR=/home/dlab/pkgs/${YAM_TARGET}/stow/lcm-trunk.2010.06.07

    LD_LIBRARY_PATH=/home/dlab/pkgs/${YAM_TARGET}/stow/boost_1_44_0-with_boostlog/lib:${LCM_DIR}/lib:/home/dlab/pkgs/${YAM_TARGET}/stow/ogre-1.6.5/lib:/home/dlab/pkgs/${YAM_TARGET}/stow/libkml-trunk.2009.12.14/lib:/home/dlab/pkgs/${YAM_TARGET}/stow/hdf5-1.8.4-patch1/lib:/home/dlab/pkgs/${YAM_TARGET}/stow/bullet-2.74/lib:/home/dlab/pkgs/${YAM_TARGET}/stow/liblbfgs-1.8/lib:/usr/lib:${LD_LIBRARY_PATH}:/home/dlab/pkgs/${YAM_TARGET}/stow/simage-1.6.1/lib:/home/dlab/pkgs/${YAM_TARGET}/stow/SoXt-1.2.2/lib:/home/dlab/pkgs/${YAM_TARGET}/stow/Coin-3.0.0/lib
    export LD_LIBRARY_PATH

    MATLAB_LIBDIR=/home/atbe/pkgs/src/matlab/matlab-7.1/bin/glnx86/mlabwrap
    export MATLAB_LIBDIR
    MATLAB_BINDIR=/home/atbe/pkgs/src/matlab/matlab-7.1/bin
    export MATLAB_BINDIR

    # uncomment the following with a path to the graphviz containing a
    # build of the "dlab" graphviz extension for interactive panels
    GRAPHVIZ_LIB=/usr/lib/graphviz/
    GAPHAS_LIB=/home/dlab/pkgs/src/gaphas/gaphas-svn-2009-06-24
    PYTHONPATH=${GRAPHVIZ_LIB}/python:${GAPHAS_LIB}:${PYTHONPATH}
    #DOTCMD=/home/dlab/pkgs/${YAM_TARGET}/stow/graphviz-2.20.2/bin/dot
    # DOTCMD=/usr/bin/dot
    export DOTCMD

    PYTHONPATH=/home/dlab/pkgs/${YAM_TARGET}/stow/libkml-trunk.2009.12.14/lib/python2.6/site-packages:${PYTHONPATH}
    export PYTHONPATH

    LCM_GEN_BIN=${LCM_DIR}/bin/lcm-gen
    export LCM_GEN_BIN

    LCM_CLASSPATH=${LCM_DIR}/share/java/lcm.jar
    export LCM_CLASSPATH

    PYTHONPATH=${LCM_DIR}/lib/python2.6/site-packages:${PYTHONPATH}
    export PYTHONPATH

    OGRE_RENDERING_SYSTEM_PLUGIN=/home/dlab/pkgs/${YAM_TARGET}/stow/ogre-1.6.5/lib/OGRE/RenderSystem_GL.so
    export OGRE_RENDERING_SYSTEM_PLUGIN
fi


if [ "$YAM_TARGET" = "x86_64-fedora13-linux" ]; then
    BOOST_DIR=/home/dlab/pkgs/${YAM_TARGET}/stow/boost-1.46.1-with_boostlog
    LCM_DIR=/home/dlab/pkgs/${YAM_TARGET}/stow/lcm-svn.2011.06.18
    OGRE_DIR=/home/dlab/pkgs/${YAM_TARGET}/stow/ogre-1.7.3
    BULLET_DIR=/home/dlab/pkgs/${YAM_TARGET}/stow/bullet-2.78
    CEGUI_DIR=/home/dlab/pkgs/${YAM_TARGET}/stow/cegui-0.7.5-with_ogre-1.7.3

    LD_LIBRARY_PATH=${BOOST_DIR}/lib:${LCM_DIR}/lib:${OGRE_DIR}/lib:${CEGUI_DIR}/lib:/home/dlab/pkgs/${YAM_TARGET}/stow/libkml-trunk.2009.12.14/lib:/home/dlab/pkgs/${YAM_TARGET}/stow/hdf5-1.8.4-patch1/lib:${BULLET_DIR}/lib:/home/dlab/pkgs/${YAM_TARGET}/stow/liblbfgs-1.8/lib:/usr/lib64:${LD_LIBRARY_PATH}:/usr/lib64/openmpi/lib:/usr/lib64/mpich2/lib:/home/dlab/pkgs/src/pathLCP/path_23.5.1_c86_64:/home/dlab/pkgs/x86_64-fedora13-linux/stow/cuda/lib64
    export LD_LIBRARY_PATH
    LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/home/dlab/pkgs/x86_64-fedora13-linux/stow/OpenMM2.0/lib
    #LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/home/dlab/pkgs/src/OpenMM/OpenMM1.1-Linux64/lib

    OPENMM_PLUGIN_DIR=/home/dlab/pkgs/x86_64-fedora13-linux/stow/OpenMM2.0/lib/plugins
    #OPENMM_PLUGIN_DIR=/home/dlab/pkgs/src/OpenMM/OpenMM1.1-Linux64/lib/plugins
    export OPENMM_PLUGIN_DIR

    MATLAB_LIBDIR=/home/dlab/pkgs/src/matlab/matlab7.1/bin/glnxa64
    export MATLAB_LIBDIR
    MATLAB_BINDIR=/home/dlab/pkgs/src/matlab/matlab7.1/bin
    export MATLAB_BINDIR
    MLABWRAP_PYTHON_PATH=/home/dlab/pkgs/x86_64-fedora13-linux/stow/mlabwrap-1.0/build/lib.linux-x86_64-2.6
    export MLABWRAP_PYTHON_PATH

    # uncomment the following with a path to the graphviz containing a
    # build of the "dlab" graphviz extension for interactive panels
    #GRAPHVIZ_LIB=/home/dlab/pkgs/x86_64-fedora9-linux/stow/graphviz-2.20.2/lib/graphviz
    GRAPHVIZ_LIB=/usr/lib64/graphviz/
    GAPHAS_LIB=/home/dlab/pkgs/src/gaphas/gaphas-svn-2009-06-24
    PYTHONPATH=:$MLABWRAP_PYTHON_PATH:${GRAPHVIZ_LIB}/python:${GAPHAS_LIB}:${PYTHONPATH}
    #DOTCMD=/home/dlab/pkgs/${YAM_TARGET}/stow/graphviz-2.20.2/bin/dot
    # DOTCMD=/usr/bin/dot
    export DOTCMD

    PYTHONPATH=/home/dlab/pkgs/${YAM_TARGET}/stow/libkml-trunk.2009.12.14/lib64/python2.6/site-packages:${PYTHONPATH}
    export PYTHONPATH

    LCM_GEN_BIN=${LCM_DIR}/bin/lcm-gen
    export LCM_GEN_BIN

    LCM_CLASSPATH=${LCM_DIR}/share/java/lcm.jar
    export LCM_CLASSPATH

    PYTHONPATH=${LCM_DIR}/lib64/python2.6/site-packages:${PYTHONPATH}
    export PYTHONPATH

    # PYTHONPATH to stow installation.
    PYTHONPATH=/home/dlab/pkgs/${YAM_TARGET}/lib/python2.6/site-packages:${PYTHONPATH}
    PYTHONPATH=/home/dlab/pkgs/${YAM_TARGET}/lib64/python2.6/site-packages:${PYTHONPATH}
    export PYTHONPATH

    export OGRE_RENDERING_SYSTEM_PLUGIN=${OGRE_DIR}/lib/OGRE/RenderSystem_GL.so
    export OGRE_PARTICLE_FX_PLUGIN=${OGRE_DIR}/lib/OGRE/Plugin_ParticleFX.so
fi

if [ "$YAM_TARGET" = "x86_64-fedora15-linux" ]; then
    BOOST_DIR=/home/dlab/pkgs/${YAM_TARGET}/stow/boost-1.46.1-with_boostlog
    LCM_DIR=/home/dlab/pkgs/${YAM_TARGET}/stow/lcm-svn.2011.06.18
    OGRE_DIR=/home/dlab/pkgs/${YAM_TARGET}/stow/ogre-1.7.3
    OIS_DIR=/home/dlab/pkgs/${YAM_TARGET}/stow/ois-1.3
    CEGUI_DIR=/home/dlab/pkgs/${YAM_TARGET}/stow/cegui-0.7.5
    BULLET_DIR=/home/dlab/pkgs/${YAM_TARGET}/stow/bullet-2.78
    JPLV_DIR=/home/dlab/pkgs/${YAM_TARGET}/stow/jplv-1.4.0
    KML_DIR=/home/dlab/pkgs/${YAM_TARGET}/stow/libkml-trunk.2009.12.14
    LIBLBFGS_DIR=/home/dlab/pkgs/${YAM_TARGET}/stow/liblbfgs-1.8
    PATHLCP_DIR=/home/dlab/pkgs/src/pathLCP/path_23.5.1_c86_64

    LD_LIBRARY_PATH=${BOOST_DIR}/lib:${LCM_DIR}/lib:${OGRE_DIR}/lib:${OIS_DIR}/lib:${KML_DIR}/lib:${BULLET_DIR}/lib:${LIBLBFGS_DIR}/lib:${OPENMM_DIR}/lib:/usr/lib64:/usr/lib64/openmpi/lib:/usr/lib64/mpich2/lib:${PATHLCP_DIR}:${LD_LIBRARY_PATH}

    # Least priority
    LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/home/dlab/pkgs/${YAM_TARGET}/lib
    LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/home/dlab/pkgs/${YAM_TARGET}/lib64

    export LD_LIBRARY_PATH

    OPENMM_PLUGIN_DIR=${OPENMM_PLUGIN_DIR}/lib/plugins
    export OPENMM_PLUGIN_DIR

    MATLAB_LIBDIR=/home/dlab/pkgs/src/matlab/matlab7.1/bin/glnxa64
    export MATLAB_LIBDIR
    MATLAB_BINDIR=/home/dlab/pkgs/src/matlab/matlab7.1/bin
    export MATLAB_BINDIR
    MLABWRAP_PYTHON_PATH=/home/dlab/pkgs/x86_64-fedora13-linux/stow/mlabwrap-1.0/build/lib.linux-x86_64-2.7
    export MLABWRAP_PYTHON_PATH

    # uncomment the following with a path to the graphviz containing a
    # build of the "dlab" graphviz extension for interactive panels
    GRAPHVIZ_LIB=/usr/lib64/graphviz
    PYTHONPATH=$MLABWRAP_PYTHON_PATH:${GRAPHVIZ_LIB}/python:${PYTHONPATH}

    PYTHONPATH=${LCM_DIR}/lib64/python2.7/site-packages:${PYTHONPATH}
    export PYTHONPATH

    LCM_GEN_BIN=${LCM_DIR}/bin/lcm-gen
    export LCM_GEN_BIN
    LCM_CLASSPATH=${LCM_DIR}/share/java/lcm.jar
    export LCM_CLASSPATH

    PYTHONPATH=${KML_DIR}/lib64/python2.7/site-packages:${PYTHONPATH}

    # PYTHONPATH to stow installation.
    PYTHONPATH=/home/dlab/pkgs/${YAM_TARGET}/lib/python2.7/site-packages:${PYTHONPATH}
    PYTHONPATH=/home/dlab/pkgs/${YAM_TARGET}/lib64/python2.7/site-packages:${PYTHONPATH}
    export PYTHONPATH

    export OGRE_RENDERING_SYSTEM_PLUGIN=${OGRE_DIR}/lib/OGRE/RenderSystem_GL.so
    export OGRE_PARTICLE_FX_PLUGIN=${OGRE_DIR}/lib/OGRE/Plugin_ParticleFX.so
fi

#======================================
# MSF  stuff
LD_LIBRARY_PATH=${GRAPHVIZ_LIBDIR}:${LD_LIBRARY_PATH}:${MATLAB_LIBDIR}
PATH=${MATLAB_BINDIR}:${PATH}
