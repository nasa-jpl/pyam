########################################################################
#
#      !!!!!! EDIT & CUSTOMIZE THIS FILE !!!!!!
#
########################################################################
#
# Defines site independent, but target specific build variables
#
# This file is included by overall.mk

CC_DEFINES 		+= -DCPU=SIMSPARCSOLARIS
CPLUSPLUS_DEFINES 	+= -DCPU=SIMSPARCSOLARIS
WIND_ARCH		=  simso
export WIND_HOST_TYPE   =  sun4-solaris2
WIND_TARGET_TYPE   	=
