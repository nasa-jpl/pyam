########################################################################
#
#      !!!!!! EDIT & CUSTOMIZE THIS FILE !!!!!!
#
########################################################################
#
# Defines site independent, but target specific build variables
#
# This file is included by overall.mk

CC_DEFINES 	+= -DCYGWIN -fPIC -fno-strict-aliasing -fwrapv -Wall
CC_LIBS 	+= -lm

CPLUSPLUS_DEFINES	+= $(CC_DEFINES)
CPLUSPLUS_LIBS 		+= $(CC_LIBS)

#SHARED_COMPILE_FLAG	:= -fPIC

RANLIB 			:= ranlib
