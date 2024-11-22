########################################################################
#
#      !!!!!! EDIT & CUSTOMIZE THIS FILE !!!!!!
#
########################################################################
#
# Defines site independent, but target specific build variables
#
# This file is included by overall.mk

CC_DEFINES              += -DLinux
CC_LIBS                 += -lm

CPLUSPLUS_DEFINES       += $(CC_DEFINES)
CPLUSPLUS_LIBS          += $(CC_LIBS)

SHARED_COMPILE_FLAG     := -fPIC

RANLIB                  := ranlib

# the equivalent RTI target name

RTI_TARGET              := i86Linux2.4gcc2.96

# GL variables
OGLDIRS         := $(wildcard /usr/lib/libGLcore.so*)
ifneq ($(OGLDIRS),)
  HAVE_MESA     := false
  HAVE_OPENGL   := true
else
  HAVE_MESA     := true
  HAVE_OPENGL   := false
endif

MEXEXT                       := mexglx
