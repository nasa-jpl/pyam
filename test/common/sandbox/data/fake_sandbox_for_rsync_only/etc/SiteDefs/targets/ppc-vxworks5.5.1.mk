########################################################################
#
#      !!!!!! EDIT & CUSTOMIZE THIS FILE !!!!!!
#
########################################################################
#
# Defines site independent, but target specific build variables
#
# This file is included by overall.mk

CC_DEFINES 		+= -DCPU=PPC603
#CPLUSPLUS_DEFINES 	+= -DCPU=PPC603 -fno-builtin -fno-for-scope \
#                                   -nostdinc -c
CPLUSPLUS_DEFINES 	+= -DCPU=PPC603

WIND_ARCH		=  ppc
#WIND_TARGET_TYPE   	=  powerpc-wrs-vxworks/

#CC_INCLUDES += -I$(WIND_BASE)/host/$(WIND_HOST_TYPE)/lib/gcc-lib/powerpc-wrs-vxworks/gcc-2.96/include
CC_INCLUDES += -I$(INT_GCC_EXEC_PREFIX)powerpc-wrs-vxworks/gcc-2.96/include \
		 -I$(WIND_BASE)/host/$(WIND_HOST_TYPE)/include/g++-3 \
		 -I$(WIND_BASE)/host/$(WIND_HOST_TYPE)/powerpc-wrs-vxworks/include


#export GCC_EXEC_PREFIX = $(WIND_BASE)/host/$(WIND_HOST_TYPE)/lib/gcc-lib/
# need to do this so that the cross-compiler gcc can find cpp. For some
# reason GCC_EXEC_PREFIX is not working properly to solve this problem
# Also needed to do this so that "as" could be found
#export PATH		:= $(PATH):$(GCC_EXEC_PREFIX)powerpc-wrs-vxworks/cygnus-2.7.2-960126:$(WIND_BASE)/host/$(WIND_HOST_TYPE)/powerpc-wrs-vxworks/bin
