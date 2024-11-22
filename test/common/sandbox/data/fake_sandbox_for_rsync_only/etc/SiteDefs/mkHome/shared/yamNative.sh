#!/bin/sh
#
# getYamNative - script to determine YAM_NATIVE.

if [ "X$YAM_NATIVE" = "X" ]; then
  os=`uname -s`
  osver=`uname -r`
  machine=`uname -m`
  case $os in
    SunOS)
      case $osver in
        4*) YAM_NATIVE=sparc-sunos4 ;;
        5.6) YAM_NATIVE=sparc-sunos5.6 ;;
        5.7) YAM_NATIVE=sparc-sunos5.7 ;;
        5.8) YAM_NATIVE=sparc-sunos5.8 ;;
        5.9) YAM_NATIVE=sparc-sunos5.9 ;;
        5*) YAM_NATIVE=sparc-sunos5 ;;
        *) YAM_NATIVE=unknown ; echo "The \"$os\" host OS is not supported." ;;
      esac
      ;;
    IRIX64)
      case $osver in
        6.5*) YAM_NATIVE=mips-irix6.5 ;;
        6*) YAM_NATIVE=mips-irix5 ;;
        *) YAM_NATIVE=unknown ; echo "The \"$os\" host OS is not supported." ;;
      esac
      ;;
    CYGWIN_NT-5.0)
       YAM_NATIVE=i486-cygwin
      ;;
    Linux)
       if [  $machine = "i686" ]; then
          pref="i486"
       else
          pref=$machine
       fi

       if [ -e /etc/fedora-release ]; then
	   YAM_NATIVE=${pref}-rh9-linux
	   str=`cat /etc/fedora-release | sed -e 's/Core //' | sed -n -e 's/Fedora release //p' | sed -n -e 's/ \(.*\)//p' | sed -e 's/\.//'`
           dist='fedora'
	   case $str in
	       1) YAM_NATIVE=${pref}-${dist}1-linux ;;
	       2) YAM_NATIVE=${pref}-${dist}2-linux ;;
	       '') case $str2 in
	            '') YAM_NATIVE=UNKNOWN_LINUX;;
	           esac ;;
               *) YAM_NATIVE=${pref}-${dist}${str}-linux
           esac
       elif [ -e /etc/redhat-release ]; then
	   # RHEL
 	   #      str=`cat /etc/redhat-release | `sed -n -e 's/^.*-> \(.*\)/\1/p'`
	   str=`cat /etc/redhat-release | sed -n -e 's/Red Hat Linux release //p' | sed -n -e 's/ \(.*\)//p' | sed -e 's/\.//'`
	   str2=`cat /etc/redhat-release | sed -n -e 's/Red Hat Enterprise Linux WS release //p' | sed -n -e 's/ \(.*\)//p' | sed -e 's/\.//'`
	   if [ "X$str" != "X" ]; then
	       dist='rhel'
	       case $str in
		   72*) YAM_NATIVE=${pref}-${dist}linux ;;
		   73*) YAM_NATIVE=${pref}-${dist}linux ;;
		   '') case $str2 in
		       '') YAM_NATIVE=UNKNOWN_LINUX;;
		       *) YAM_NATIVE=${pref}-rh9-linux
	               esac ;;
	           *) YAM_NATIVE=${pref}-rh${str}-linux
	       esac
	   else
	       # CentOS
	       str=`cat /etc/redhat-release | sed -n -e 's/CentOS release //p' | sed -n -e 's/ \(.*\)//p' | sed -e 's/\.//'`
	       str2=`cat /etc/redhat-release | sed -n -e 's/CentOS release //p' | sed -n -e 's/ \(.*\)//p' | sed -e 's/\.//'`
	       if [ "X$str" != "X" ]; then
		   dist='rhel'
		   case $str in
		       '') case $str2 in
		             '') YAM_NATIVE=UNKNOWN_LINUX;;
		             *) YAM_NATIVE=${pref}-${dist}9-linux
		           esac ;;
		        40) YAM_NATIVE=${pref}-${dist}4-linux;;
		        41) YAM_NATIVE=${pref}-${dist}4-linux;;
		        42) YAM_NATIVE=${pref}-${dist}4-linux;;
		        44) YAM_NATIVE=${pref}-${dist}4-linux;;
		        44) YAM_NATIVE=${pref}-${dist}4-linux;;
		        *) YAM_NATIVE=${pref}-${dist}4-linux
		   esac
	       fi
	   fi
       else
	   if [ -e /etc/SuSE-release ]; then
	       str=`cat /etc/SuSE-release | sed -n -e 's/SuSE Linux //p' | sed -n -e 's/ \(.*\)//p' | sed -e 's/\.//'`
	       dist='suse'
	       case $str in
#		   73*) YAM_NATIVE=${pref}-suse-linux ;;
# SuSE 9.0 can use Redhat 9
		   90*) YAM_NATIVE=${pref}-rh9-linux ;;
		   *) YAM_NATIVE=${pref}-suse${str}-linux
	       esac

	   else
	       YAM_NATIVE=UNKNOWN_LINUX
	   fi
       fi
      ;;
    HP-UX)
      case $osver in
        A.09*) YAM_NATIVE=hppa-hpux9 ;;
        B.10*) YAM_NATIVE=hppa-hpux10 ;;
        *) YAM_NATIVE=unknown ; echo "The \"$os\" host OS is not supported." ;;
      esac
      ;;
  esac
fi

echo $YAM_NATIVE
