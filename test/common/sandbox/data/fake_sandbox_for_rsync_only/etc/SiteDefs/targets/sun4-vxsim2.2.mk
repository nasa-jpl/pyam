########################################################################
#
#      !!!!!! EDIT & CUSTOMIZE THIS FILE !!!!!!
#
########################################################################
#
# Defines site independent, but target specific build variables
#
# This file is included by overall.mk

CC_DEFINES              += -DCPU=SIMSPARCSOLARIS
CPLUSPLUS_DEFINES       += -DCPU=SIMSPARCSOLARIS
WIND_ARCH               =  simso
export WIND_HOST_TYPE   =  sun4-solaris2
WIND_TARGET_TYPE        =

#CC_INCLUDES += -I$(INT_GCC_EXEC_PREFIX)sparc-wrs-solaris2.5.1/gcc-2.96/include
CC_INCLUDES += -I$(INT_GCC_EXEC_PREFIX)powerpc-wrs-vxworks/gcc-2.96/include \
		 -I$(WIND_BASE)/host/$(WIND_HOST_TYPE)/include/g++-3 \
		 -I$(WIND_BASE)/host/$(WIND_HOST_TYPE)/powerpc-wrs-vxworks/include
