#!/bin/sh -x
#
#echo "nargs1=$#"

if [ "X$help" != "X" ]; then
    echo "Additional '$YAM_SITE' site specific options from '`basename $0`':"
    echo "  -no-rti          do not set RTI environment variables"
    echo "                   -norti is the same as -no-rti"
    echo "  -dview_old       set up environment for old Dview"
    echo ""
    echo " NDDS options:"
    echo "  -ndds            start (and subsequently kill) RTI's NDDS daemon"
    echo "  -ndds_domain <port>  port number to use for NDDS daemon"
    echo "  -ndds_peer_hosts <hosts>  value for NDDS_PEER_HOSTS variable"
    echo ""
    echo " Tramel options:"
    echo "  -tramel           start (and subsequently kill) Tramel daemon"
    echo "  -tr-app  <auth>   use the specified Tramel application (TR_APPLICATION)"
    echo "  -tr-auth <auth>   use the specified Tramel authority (TR_AUTHORITY)"
    echo "  -tr-host <host>   use the specified Tramel host (TR_SERVER_HOST)"
    echo "  -tr-port <port>   use the specified Tramel port (TR_SERVER_PORT)"
    echo "  -tr-site <site>   use the specified Tramel site (TR_SITE)"
    echo ""
    exit 2
fi



dview_old="0"
start_ndds="0"
start_tramel="0"
rti_env="1"
clean="1"
while [ "$#" != "0" ]; do
    if [ "$1" = "-dview_old" ]; then
        dview_old="1"
    elif [ "$1" = "-ndds" ]; then
        start_ndds="1"
    elif [ "$1" = "-tramel" ]; then
        start_tramel="1"
    elif [ "$1" = "-tr-app" ]; then
        shift
        TR_APPLICATION=$1
        export TR_APPLICATION
    elif [ "$1" = "-tr-auth" ]; then
        shift
        TR_AUTHORITY=$1
        export TR_AUTHORITY
    elif [ "$1" = "-tr-site" ]; then
        shift
        TR_SITE=$1
        export TR_SITE
    elif [ "$1" = "-tr-port" ]; then
        shift
        TR_SERVER_PORT=$1
        export TR_SERVER_PORT
    elif [ "$1" = "-tr-host" ]; then
        shift
        TR_SERVER_HOST=$1
        export TR_SERVER_HOST
    elif [ "$1" = "-ndds_domain" ]; then
        shift
        ATBE_NDDS_DOMAIN=$1
        export ATBE_NDDS_DOMAIN
    elif [ "$1" = "-ndds_peer_hosts" ]; then
        shift
        NDDS_PEER_HOSTS=$1:0.0
        export NDDS_PEER_HOSTS
    elif [ "$1" = "-no-rti" ]; then
        rti_env="0"
    else
      break
    fi
    shift
done

# start up NDDS daemon if requested
if [ "$start_ndds" = "1" ]; then
    nddsStartDaemon -v 0 -d $ATBE_NDDS_DOMAIN &
    USING_NDDS=1
    export USING_NDDS
fi

############ Tramel Environment ##################################################

# start up the Tramel daemon if requested
# set up TR_AUTHORITY
if [ "X$TR_APPLICATION" = "X" ]; then
    TR_APPLICATION=test
    export TR_APPLICATION
fi

# set up TR_AUTHORITY
if [ "X$TR_AUTHORITY" = "X" ]; then
    TR_AUTHORITY=$USER
    export TR_AUTHORITY
fi

# set up TR_SITE
if [ "X$TR_SITE" = "X" ]; then
    TR_SITE=Dshell
    export TR_SITE
fi

# set up TR_SERVER_PORT
if [ "X$TR_SERVER_PORT" = "X" ]; then
    TR_SERVER_PORT=`expr 7900 + $$ % 10000`
    export TR_SERVER_PORT
fi

# set up TR_SERVER_HOST
if [ "X$TR_SERVER_HOST" = "X" ]; then
    TR_SERVER_HOST=$HOST
    export TR_SERVER_HOST
fi

if [ "$start_tramel" = "1" ]; then
    # finally start up the daemon
    trameld  -delay 0 -cs $TR_SERVER_PORT -rs 0:100:60 -ss 0 -app $TR_APPLICATION \
	    -auth $TR_AUTHORITY -site $TR_SITE  &
    USING_TRAMEL=1
    export USING_TRAMEL
fi

############ MATLAB ENVIRONMENT ###############################################

if [ -x "${YAM_ROOT}/lib/dhss-lib" ]; then
    if [ "X$MATLABPATH" = "X" ]; then
        MATLABPATH=${YAM_ROOT}/lib/dhss-lib/Matlab
    else
        MATLABPATH=${YAM_ROOT}/lib/dhss-lib/Matlab:${MATLABPATH}
    fi
fi

if [ -x "${YAM_ROOT}/lib/IMOS" ]; then
    if [ "X$MATLABPATH" = "X" ]; then
        MATLABPATH=${YAM_ROOT}/lib/IMOS:${YAM_ROOT}/bin/${YAM_NATIVE}
    else
        MATLABPATH=${YAM_ROOT}/lib/IMOS:${YAM_ROOT}/bin/${YAM_NATIVE}:${MATLABPATH}
    fi
fi
export MATLABPATH

if [ "$cmd" = "matlab" ]; then
    if [ "X$MATLABVERSION" = "X" ]; then
        cmd=matlab-5.3;
    else
        cmd=matlab-${MATLABVERSION};
    fi
fi

############ DVIEW ENVIRONMENT ################################################

# if have Open GL then use the appropriate version of Dview
OGLEXT=""
if [ -x "/usr/openwin/include/GL" ]; then
  OGLEXT="-ogl"
elif [ "$YAM_NATIVE" = "mips-irix5" ]; then
  OGLEXT="-ogl"
elif [ "$YAM_NATIVE" = "mips-irix6.5" ]; then
  OGLEXT="-ogl"
fi

# The variable DVIEWLIB must be set to the directory where all
# of dviews data is.  This enables dview to find datafiles and
# other information it needs to run.
if [ "X$DVIEWLIB" = "X" ]; then
    if [ "$dview_old" = "1" ]; then
	DVIEWLIB=${YAM_ROOT}/lib/Dview
	export DVIEWLIB
    fi
fi

if [ "X$DV_PATH" = "X" ]; then
    if [ "$dview_old" = "0" ]; then
	DV_PATH=${YAM_ROOT}/lib/DviewNew
	export DV_PATH
    fi
fi


if [ "X$DVIEWBIN" = "X" ]; then
    if [ "$dview_old" = "0" ]; then
	DVIEWBIN=dviewnew${OGLEXT}
    else
	DVIEWBIN=dview${OGLEXT}
    fi
fi
export DVIEWBIN

# The XENVIRONMENT variable must be set to the resource file GRres;
# this is where dview gets the sizes of its user interface windows and widgets.
if [ "X$XENVIRONMENT" = "X" ]; then
    if [ "$dview_old" = "1" ]; then
	XENVIRONMENT=${YAM_ROOT}/etc/Dview/GRres
    else
	XENVIRONMENT=${YAM_ROOT}/etc/Dview_src/DV-RES
    fi
    export XENVIRONMENT
fi

echo "$cmd"
