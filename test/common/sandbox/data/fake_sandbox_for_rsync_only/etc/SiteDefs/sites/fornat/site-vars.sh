# site specific environment variables

# destination directory for Depydoc generated docs
DEPYDOCS_DIR=/home/dlab/repo/www/DLabDocs/Python
export DEPYDOCS_DIR

# environment variables for doctest documentation generation
DOCTESTDOCS_DIR=/home/dlab/repo/www/DLabDocs/doctests
DOCTESTLIST=/home/dlab/sim-utils/repo/lib/doctestList.py
export DOCTESTDOCS_DIR
export DOCTESTLIST


VALGRIND_SUPP_FILE=/home/dlab/sim-utils/lib/valgrind-supp.file
export VALGRIND_SUPP_FILE

# vehicle graphics model files
CHARIOTROVER_IVDIR=/home/fornat/chariot1G/
export CHARIOTROVER_IVDIR
K10ROVER_IVDIR=/home/fornat/K10/ivFiles/
export K10ROVER_IVDIR



# set up variables for running VxSim

if [ "$YAM_TARGET" = "i486-fedora6-linux" ]; then
    MATLAB_LIBDIR=/home/dlab/pkgs/src/matlab/matlab-7.1/bin/glnx86/mlabwrap
    export MATLAB_LIBDIR
    MATLAB_BINDIR=/home/dlab/pkgs/src/matlab/matlab-7.1/bin
    export MATLAB_BINDIR

    export POVRAY_BIN
    POVRAY_BIN=/usr/local/bin/povray

    # for Coin 2.5
    LD_LIBRARY_PATH=/home/dlab/pkgs/src/qwt/qwt-5.0.2/lib:/home/dlab/pkgs/i486-fedora6-linux/stow/Coin-2.5-svn/lib:/home/dlab/pkgs/i486-fedora6-linux/stow/simage-1.6.1/lib:/home/dlab/pkgs/i486-fedora6-linux/stow/SoXt-1.2.2/lib:/usr/lib64:${LD_LIBRARY_PATH}

#    GRAPHVIZ_LIB=/home/dlab/pkgs/i486-fedora4-linux/stow/graphviz-2.7.20060131.0540/lib/graphviz
    GRAPHVIZ_LIB=/home/dlab/pkgs/i486-fedora4-linux/stow/graphviz-2.9.20060305.0540/lib/graphviz
    # PYTHONPATH=/home/dlab/pkgs/src/Python/installs/i486-fedora4-linux/2.4.1/lib/python:${GRAPHVIZ_LIB}/python:${PYTHONPATH}
    # PYTHONPATH=/home/dlab/pkgs/i486-fedora6-linux/lib/pythonPkgs/lib/python:/home/dlab/pkgs/src/Python/installs/i486-fedora4-linux/2.4.1/lib/python:${GRAPHVIZ_LIB}/python:${PYTHONPATH}
    PYTHONPATH=/home/dlab/pkgs/i486-fedora6-linux/lib/pythonPkgs/lib/python:${GRAPHVIZ_LIB}/python:${PYTHONPATH}
    export PYTHONPATH

    TK_VERSION=8.4
    TK_LIBRARY=/usr/lib/tk8.4
	if  [ "X$TK_PKGLIBRARY" = "X" ]; then
		 TK_PKGLIBRARY=/usr/lib/libtk8.4.so
	fi

    HIPPO_PYTHON_PATH=/home/dlab/pkgs/i486-fedora4-linux/stow/HippoDraw-1.16.2/lib/python2.4/site-packages/HippoDraw
    export HIPPO_PYTHON_PATH

    GNOCL_VERSION=0.5.18
	if  [ "X$GNOCL_LIBDIR" = "X" ]; then
#		GNOCL_LIBDIR=/home/dlab/pkgs/src/gtk/gnocl-0.5.17-released-linux/src
	    GNOCL_LIBDIR=/home/dlab/pkgs/src/gtk/gnocl-0.5.18-i486-rh9-linux/src
	 fi
fi


if [ "$YAM_TARGET" = "i486-fedora7-linux" ]; then
    MATLAB_LIBDIR=/home/dlab/pkgs/src/matlab/matlab-7.1/bin/glnx86/mlabwrap
    export MATLAB_LIBDIR
    MATLAB_BINDIR=/home/dlab/pkgs/src/matlab/matlab-7.1/bin
    export MATLAB_BINDIR

    export POVRAY_BIN
    POVRAY_BIN=/usr/local/bin/povray

#    GRAPHVIZ_LIB=/home/dlab/pkgs/i486-fedora4-linux/stow/graphviz-2.7.20060131.0540/lib/graphviz
    GRAPHVIZ_LIB=/home/dlab/pkgs/i486-fedora4-linux/stow/graphviz-2.9.20060305.0540/lib/graphviz
    PYTHONPATH=/home/dlab/pkgs/src/Python/installs/i486-fedora4-linux/2.4.1/lib/python:${GRAPHVIZ_LIB}/python:${PYTHONPATH}
    export PYTHONPATH

    TK_VERSION=8.4
    TK_LIBRARY=/usr/lib/tk8.4
	if  [ "X$TK_PKGLIBRARY" = "X" ]; then
		 TK_PKGLIBRARY=/usr/lib/libtk8.4.so
	fi

    HIPPO_PYTHON_PATH=/home/dlab/pkgs/i486-fedora4-linux/stow/HippoDraw-1.16.2/lib/python2.4/site-packages/HippoDraw
    export HIPPO_PYTHON_PATH

fi


if [ "$YAM_TARGET" = "i486-fedora8-linux" ]; then
    export POVRAY_BIN
    POVRAY_BIN=/usr/local/bin/povray

    # for Coin 2.5
    LD_LIBRARY_PATH=/home/dlab/pkgs/src/qwt/qwt-5.0.2/lib:/home/dlab/pkgs/i486-fedora6-linux/stow/Coin-2.5/lib:/home/dlab/pkgs/i486-fedora6-linux/stow/simage-1.6.1/lib:/home/dlab/pkgs/i486-fedora6-linux/stow/SoXt-1.2.2/lib:${LD_LIBRARY_PATH}


fi


if [ "$YAM_TARGET" = "x86_64-fedora9-linux" ]; then
    export POVRAY_BIN
    POVRAY_BIN=/usr/local/bin/povray

    # for Coin 2.5
    #LD_LIBRARY_PATH=/home/dlab/pkgs/${YAM_TARGET}/stow/simage-1.6.1/lib:/home/dlab/pkgs/${YAM_TARGET}/stow/SoXt-1.2.2-asis/lib:/home/dlab/pkgs/${YAM_TARGET}/stow/hdf5-1.6.5/lib:${LD_LIBRARY_PATH}
    LD_LIBRARY_PATH=/home/dlab/pkgs/${YAM_TARGET}/stow/simage-1.6.1/lib:/home/dlab/pkgs/${YAM_TARGET}/stow/SoXt-1.2.2-Coin-3.0.0/lib:/home/dlab/pkgs/${YAM_TARGET}/stow/Coin-3.0.0/lib:${LD_LIBRARY_PATH}
    export LD_LIBRARY_PATH
fi


if [ "$YAM_TARGET" = "x86_64-fedora11-linux" ]; then

    export POVRAY_BIN
    POVRAY_BIN=/usr/local/bin/povray

    LD_LIBRARY_PATH=/home/dlab/pkgs/${YAM_TARGET}/stow/simage-1.6.1/lib:/home/dlab/pkgs/${YAM_TARGET}/stow/libkml-1.0.0/lib:/home/dlab/pkgs/${YAM_TARGET}/stow/SoXt-1.2.2/lib:/home/dlab/pkgs/${YAM_TARGET}/stow/Coin-3.0.0/lib:/usr/lib64:${LD_LIBRARY_PATH}
    export LD_LIBRARY_PATH

    PYTHONPATH=/home/dlab/pkgs/x86_64-fedora11-linux/stow/libkml-1.0.0/lib64/python2.6/site-packages:${PYTHONPATH}
    export PYTHONPATH

    LCM_GEN_BIN=/home/dlab/pkgs/${YAM_TARGET}/stow/lcm-0.3.0/bin/lcm-gen
    export LCM_GEN_BIN

fi
















if [ "$YAM_TARGET" = "x86_64-fedora13-linux" ]; then
    LCM_DIR=/home/dlab/pkgs/${YAM_TARGET}/stow/lcm-trunk.2010.06.07
    OGRE_DIR=/home/dlab/pkgs/${YAM_TARGET}/stow/ogre-1.7.1
    BULLET_DIR=/home/dlab/pkgs/${YAM_TARGET}/stow/bullet-2.77-new

    LD_LIBRARY_PATH=/home/dlab/pkgs/${YAM_TARGET}/stow/boost-1.46.1-with_boostlog/lib:${LCM_DIR}/lib:${OGRE_DIR}/lib:/home/dlab/pkgs/${YAM_TARGET}/stow/libkml-trunk.2009.12.14/lib:/h
ome/dlab/pkgs/${YAM_TARGET}/stow/hdf5-1.8.4-patch1/lib:${BULLET_DIR}/lib:/home/dlab/pkgs/${YAM_TARGET}/stow/liblbfgs-1.8/lib:/usr/lib64:${LD_LIBRARY_PATH}:/usr/lib64/openmpi/lib:/usr
/lib64/mpich2/lib:/home/dlab/pkgs/src/pathLCP/path_23.5.1_c86_64:/home/dlab/pkgs/x86_64-fedora13-linux/stow/cuda/lib64
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

    OGRE_RENDERING_SYSTEM_PLUGIN=${OGRE_DIR}/lib/OGRE/RenderSystem_GL.so
    export OGRE_RENDERING_SYSTEM_PLUGIN

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

PATH=${MATLAB_BINDIR}:${PATH}
