#################################

DS1_VERSION=R2S3

#DS1_IF_DIR=/proj/nm-ds1/Development/atbe/infrastructure/R2S3
#DS1_IF_DIR=/proj/nm-ds1/Stage/R2S3
#DS1_IF_DIR=/proj/nm-ds1/Test/R2S3

#DS1_IF_DIR=/proj/nm-ds1/Stage/R3_Current
DS1_IF_DIR=/home/atbe/users/jain/Test/telerobotics/ds1/R2S3

export DS1_IF_DIR
DS1_GLOBAL_INCDIR=$DS1_IF_DIR/global
export DS1_GLOBAL_INCDIR
DS1_UTILS_INCDIR=$DS1_IF_DIR/utils/include
export DS1_UTILS_INCDIR
DS1_UTILS_LIBDIR=$DS1_IF_DIR/utils/lib
export DS1_UTILS_LIBDIR

#################################
#ATBE_INCDIR=$DS1_GLOBAL_INCDIR/atbe
export ATBE_INCDIR

#################################
#ACS_INCDIR=$DS1_GLOBAL_INCDIR/acs
export ACS_INCDIR

#################################
#FSC_INCDIR=$DS1_GLOBAL_INCDIR/fsc
export FSC_INCDIR

#################################

#NAV_INCDIR=$DS1_GLOBAL_INCDIR/nav
export NAV_INCDIR

#################################

# this is OBSOLETE and should be done away with

#IPC_INCDIR=/proj/nm-ds1/Development/msgs/include
#IPC_INCDIR=$DS1_UTILS_INCDIR/ipc
export IPC_INCDIR

#IPC_LIBDIR=/proj/nm-ds1/Development/msgs/lib
#IPC_LIBDIR=$DS1_UTILS_LIBDIR
export IPC_LIBDIR

IPC_LIBS="-lclash-runtime -lipc"
#IPC_LIBS=$DS1_UTILS_LIBDIR/$YAM_TARGET/libipc.a
export IPC_LIBS

#################################

#DS1_GLOBAL_INCDIR=$DS1_GLOBAL_INCDIR/global
#export DS1_GLOBAL_INCDIR

#DS1_GLOBAL_LIBDIR=$DS1_GLOBAL_INCDIR/global/lib
#export DS1_GLOBAL_LIBDIR

#################################
