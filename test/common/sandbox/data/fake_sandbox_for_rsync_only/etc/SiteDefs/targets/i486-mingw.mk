########################################################################
#
#      !!!!!! EDIT & CUSTOMIZE THIS FILE !!!!!!
#
########################################################################
#
# Defines site independent, but target specific build variables
#
# This file is included by overall.mk


CC_DEFINES 	+= -DCYGWIN -mno-cygwin -mdll -O
CC_LIBS 	+= -lm

CPLUSPLUS_DEFINES	+= $(CC_DEFINES)
CPLUSPLUS_LIBS 		+= $(CC_LIBS)

RANLIB 			:= ranlib
