########################################################################
#
#      !!!!!! EDIT & CUSTOMIZE THIS FILE !!!!!!
#
########################################################################
#
# Defines site independent, but target specific build variables
#
# This file is included by overall.mk

CC_DEFINES 		+= -DSUNOS5 -DSUNWSPRO -DNO_GCC
CC_LIBS 		+= -lm -lnsl -lsocket -lposix4
CPLUSPLUS_DEFINES	+= $(CC_DEFINES)
CPLUSPLUS_LIBS 		+= $(CC_LIBS)

SHARED_COMPILE_FLAG	:= -KPIC

# the equivalent RTI target name
RTI_TARGET :		= sparcSol2.6

# libkcs (Kodak format library needed by Scope for Solaris 5.6 and later
export LIBKCS :		:= -lkcs

# extension to use for building Mex wrappers for Dshell models
MEXEXT			:= mexsol

# GL variables
HAVE_MESA 	:= true
OGLDIRS 	:= $(wildcard /usr/openwin/include/GL/*)
ifneq ($(OGLDIRS),)
  HAVE_OPENGL 	:= true
else
  HAVE_OPENGL 	:= false
endif
