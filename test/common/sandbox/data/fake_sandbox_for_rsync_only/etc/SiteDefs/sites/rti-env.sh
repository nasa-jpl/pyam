# Environment variable settings for RTI include files
#if (! $?OS_ARCH) then
if [ "X$OS_ARCH" = "X" ]; then
  os=`uname -s`
  case $os in
    SunOS)
      osver=`uname -r`
      case $osver in
	4*) OS_ARCH=sun4 ;;
       5.5*) OS_ARCH=sparcSol2.5 ;;
       5.6) OS_ARCH=sparcSol2.6 ;;
       5.7) OS_ARCH=sparcSol2.6 ;;
       5.8) OS_ARCH=sparcSol2.6 ;;
       5.9) OS_ARCH=sparcSol2.8 ;;
	*)  OS_ARCH=unknown ; echo "The \"$os\" host OS is not supported for RTI tools." ;;
      esac
	;;
    IRIX)
      osver=`uname -r`
      case $osver in
	4*) OS_ARCH=mipsIRIX4 ;;
	5*) OS_ARCH=mipsIRIX5 ;;
	6*) OS_ARCH=mipsIRIX6.4 ;;
	*)  OS_ARCH=unknown ; echo "The \"$os\" host OS is not supported for RTI tools." ;;
      esac
	;;
    IRIX64)
      osver=`uname -r`
      case $osver in
	6*) OS_ARCH=mipsIRIX6.4 ;;
	*)  OS_ARCH=unknown ; echo "The \"$os\" host OS is not supported for RTI tools." ;;
      esac
	;;
    Linux)
      osver=`uname -r`
      case $osver in
	2.2*) OS_ARCH=i86Linux2.2 ;;
	2.4*) OS_ARCH=i86Linux2.4 ;;
	2.6*) OS_ARCH=i86Linux2.4 ;;
	*)  OS_ARCH=unknown ; echo "The \"$os\" host OS is not supported for RTI tools." ;;
      esac
	;;
    HP-UX)
      osver=`uname -r`
      case $osver in
	A.09*) OS_ARCH=hppaUX9 ;;
	B.10*) OS_ARCH=hppaUX9 ;;
	*)  OS_ARCH=unknown ; echo "The \"$os\" host OS is not supported for RTI tools." ;;
      esac
	;;
    OSF1*)
      osver=`uname -r`
      OS_ARCH=alphaOSF1 ;;
    *)
      echo "OS $os may not be supported" ;;
  esac
#  echo "Setting OS_ARCH to $OS_ARCH"
fi

#if [ "X$OS_ARCH" = "X" ]; then
#  os=`uname -r`
#  case $os in
#  4*) OS_ARCH=sun4 ;;
#  5*) OS_ARCH=sparcSol2 ;;
#  *)  OS_ARCH=unknown ; echo "The \"$os\" host OS is not supported for RTI tools." ;;
#  esac
#  #echo "Setting OS_ARCH to ${OS_ARCH}"
#fi

export OS_ARCH


OLDRTIHOME=/home/atbe/pkgs/src/rti
export OLDRTIHOME

# added this for laptop machines where this variable may come from
# the environment
if [ "X$RTIHOME" = "X" ]; then
  RTIHOME=/home/atbe/pkgs/src/rti
fi
export RTIHOME

X11R5HOME=/home/X11R5
export X11R5HOME

if [ "X$NDDS_PEER_HOSTS" = "X" ]; then
  NDDS_PEER_HOSTS=saturnv:agena
  export NDDS_PEER_HOSTS
fi

if [ "X$RTI_LICENSE_FILE" = "X" ]; then
  RTI_LICENSE_FILE=${RTIHOME}/license.dat
  export RTI_LICENSE_FILE
#  RTID_LICENSE_FILE=${RTIHOME}/license.dat
#  export RTID_LICENSE_FILE
fi

#LM_LICENSE_FILE=${RTIHOME}/license.dat
#export LM_LICENSE_FILE

if [ "$os" = "Linux" ]; then
    if [ "X$STETHOSCOPEHOME" = "X" ]; then
	STETHOSCOPEHOME=${RTIHOME}/scope.5.3c-linux2.2
#	STETHOSCOPEHOME=${RTIHOME}/scope.6.0e-linux
    fi
    RTILIBHOME=${RTIHOME}/rtilib.4.0g-linux2.2
#    RTILIBHOME=${RTIHOME}/rtilib.4.1f-linux
else
    if [ "X$STETHOSCOPEHOME" = "X" ]; then
	STETHOSCOPEHOME=${RTIHOME}/scope.5.3b
    fi
    CONTROLSHELLHOME=${RTIHOME}/cs.5.2b
    #CONTROLSHELLHOME=/opt/rti/cs.5.1g
    RTILIBHOME=${RTIHOME}/rtilib.4.0b
    #VISIONSERVERHOME=${RTIHOME}/visionserver
    RTIMAKEHOME=${CONTROLSHELLHOME}/makehome
    MAKEHOME=${RTIMAKEHOME}
    MYMAKEHOME=${RTIMAKEHOME}
    NDDSHOME=${RTIHOME}/ndds.1.11q
fi



export STETHOSCOPEHOME CONTROLSHELLHOME RTILIBHOME VISIONSERVERHOME
export RTIMAKEHOME MAKEHOME NDDSHOME

XKEYSYMDB=${STETHOSCOPEHOME}/lib.X/X11/XKeysymDB
export XKEYSYMDB

# Stethoscope needs to be set to work properly
if [ "X$XFILESEARCHPATH" = "X" ]; then
  XFILESEARCHPATH=${STETHOSCOPEHOME}/resources
else
  XFILESEARCHPATH=${STETHOSCOPEHOME}/resources:${XFILESEARCHPATH}
fi
export XFILESEARCHPATH


CSLOADPATH=${CONTROLSHELLHOME}/lib/${OS_ARCH}/devices
CSLOADPATH=${CSLOADPATH}:${CONTROLSHELLHOME}/lib/${OS_ARCH}/components
export CSLOADPATH


if [ "X$OPENWINHOME" = "X" ]; then
  OPENWINHOME=/usr/openwin
  export OPENWINHOME
fi


if [ "X$PATH" = "X" ]; then
  PATH=/usr/bin:/usr/ucb
fi



if [ "X$MANPATH" = "X" ]; then
  MANPATH=/usr/man
fi
MANPATH=${MANPATH}:${STETHOSCOPEHOME}/man
MANPATH=${MANPATH}:${CONTROLSHELLHOME}/man
MANPATH=${MANPATH}:${RTILIBHOME}/man
MANPATH=${MANPATH}:${NDDSHOME}/man
MANPATH=${MANPATH}:/home/rti/lm/man
export MANPATH


#DARTS_PARAM_FILE=${YAM_ROOT}/lib/ds1-sc/sc_model/darts.param
#export DARTS_PARAM_FILE


CS_CELOADPATH=${CONTROLSHELLHOME}/lib/celib
CS_CELOADPATH=${CONTROLSHELLHOME}/nddsComps/celib:$CS_CELOADPATH
CS_CELOADPATH=./celib:./components/celib:./components:$CS_CELOADPATH
CS_CELOADPATH=../celib:../components/celib:./components:$CS_CELOADPATH
CS_CELOADPATH=$YAM_ROOT/lib/ds1-sc/celib:$CS_CELOADPATH
CS_CELOADPATH=$YAM_ROOT/lib/fsw-generic/celib:$CS_CELOADPATH
CS_CELOADPATH=$YAM_ROOT/lib/fsw-driver/allan-proto/celib:$CS_CELOADPATH
CS_CELOADPATH=$YAM_ROOT/lib/ds1-sc/ds1-fsw/celib:$CS_CELOADPATH
CS_CELOADPATH=$YAM_ROOT/lib/fsw-driver/rocky7/celib:$CS_CELOADPATH
CS_CELOADPATH=$YAM_ROOT/lib/fsw-driver/demo-fsw/celib:$CS_CELOADPATH
CS_CELOADPATH=$YAM_ROOT/lib/fsw-driver/ds3-collector-fsw/celib:$CS_CELOADPATH
CS_CELOADPATH=$YAM_ROOT/lib/cs-utils/celib:$CS_CELOADPATH
CS_CELOADPATH=$YAM_ROOT/lib/sc-sim/celib:$CS_CELOADPATH
#CS_CELOADPATH=$YAM_ROOT/src/proj/atbe/ds1-sim/components/celib:$CS_CELOADPATH
#CS_CELOADPATH=$YAM_ROOT/src/proj/atbe/sc-sim/components/celib:$CS_CELOADPATH
export CS_CELOADPATH


# PATH=.:${CONTROLSHELLHOME}/bin/${OS_ARCH}:${PATH}
# PATH=${PATH}:${RTIHOME}/GNU_RTI/${OS_ARCH}/bin
# PATH=${PATH}:${RTILIBHOME}/bin/${OS_ARCH}
# PATH=${PATH}:${STETHOSCOPEHOME}/bin/${OS_ARCH}
# PATH=${PATH}:${NDDSHOME}/bin/${OS_ARCH}
# PATH=${PATH}:${RTIHOME}/lm/bin/${OS_ARCH}
#PATH=${PATH}:${YAM_ROOT}/bin/sparc-sunos4
#PATH=${PATH}:${YAM_ROOT}/bin
#export PATH

#DARTS_PARAM_FILE=${YAM_ROOT}/lib/ds1-sc/sc_model/darts.param
#export DARTS_PARAM_FILE

# --- last line of rti-env.sh ---
