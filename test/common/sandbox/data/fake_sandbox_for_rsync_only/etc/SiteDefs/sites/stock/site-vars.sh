# site specific environment variables

export TK_VERSION
export TCLLIBPATH
export TK_LIBRARY
export TK_PKGLIBRARY
export GNOCL_VERSION
export GNOCL_LIBDIR
export GRAPHVIZ_VERSION
export GRAPHVIZ_LIBDIR

TCLLIBPATH="${TCLLIBPATH}  /usr/lib"

GRAPHVIZ_VERSION=2.2
GRAPHVIZ_LIBDIR=/usr/lib/graphviz

TK_VERSION=8.4
TK_LIBRARY=/usr/lib
TK_PKGLIBRARY=/usr/lib/libtk8.4.so

export POVRAY_BIN
POVRAY_BIN=/usr/local/bin/povray

GNOCL_VERSION=0.5.18
GNOCL_LIBDIR=/usr/lib

#======================================
LD_LIBRARY_PATH=${GRAPHVIZ_LIBDIR}:${LD_LIBRARY_PATH}

# vehicle graphics model files
CHARIOTROVER_IVDIR=/home/fornat/chariot1G/
export CHARIOTROVER_IVDIR
K10ROVER_IVDIR=/home/fornat/K10/ivFiles/
export K10ROVER_IVDIR


#======================================
if [ "X$TPS" = "X" ]; then
    TPS="/home/dlab/pkgs/${YAM_TARGET}"
    export TPS
fi

OGRE_RENDERING_SYSTEM_PLUGIN="$TPS/lib/OGRE/RenderSystem_GL.so"
export OGRE_RENDERING_SYSTEM_PLUGIN

export OGRE_PARTICLE_FX_PLUGIN="${TPS}/lib/OGRE/Plugin_ParticleFX.so"

LCM_CLASSPATH=${TPS}/share/java/lcm.jar
export LCM_CLASSPATH

#======================================
# for off-screen rendering with COIN
COIN_FULL_INDIRECT_RENDERING=1
COIN_FORCE_TILED_OFFSCREENRENDERING=0
#setenv COIN_OFFSCREENRENDERER_MAX_TILESIZE=2048
COIN_DEBUG_SOOFFSCREENRENDERING=0
COIN_OFFSCREENRENDERER_TILEWIDTH=4096
COIN_OFFSCREENRENDERER_TILEHEIGHT=4096
COIN_AUTOCACHE_LOCAL_MIN=9999999
COIN_AUTOCACHE_LOCAL_MAX=9999999
export COIN_FULL_INDIRECT_RENDERING
export COIN_FORCE_TILED_OFFSCREENRENDERING
export COIN_DEBUG_SOOFFSCREENRENDERING
export COIN_OFFSCREENRENDERER_TILEWIDTH
export COIN_OFFSCREENRENDERER_TILEHEIGHT
export COIN_AUTOCACHE_LOCAL_MIN
export COIN_AUTOCACHE_LOCAL_MAX
