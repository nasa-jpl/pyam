########################################################################
#
#      !!!!!! EDIT & CUSTOMIZE THIS FILE !!!!!!
#
########################################################################
#
# Defines site independent, but target specific build variables
#
# This file is included by overall.mk

YAM_OS			:= unix

CC_DEFINES              += -DLinux
CC_LIBS                 += -lm

CPLUSPLUS_DEFINES       += $(CC_DEFINES)
CPLUSPLUS_LIBS          += $(CC_LIBS)

SHARED_COMPILE_FLAG     := -fPIC

RANLIB                  := ranlib


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
