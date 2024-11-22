########################################################################
#
#      !!!!!! EDIT & CUSTOMIZE THIS FILE !!!!!!
#
########################################################################
#
# Defines site independent, but target specific build variables
#
# This file is included by overall.mk

# use the Irix 6.5 settings
include $(SITEDEFSHOME)/targets/mips-irix6.5.mk

CC_LIBS                 += -lm
CPLUSPLUS_LIBS          += $(CC_LIBS)

CC_DEFINES              := -DIRIX5

# extension to use for building Mex wrappers for Dshell models
MEXEXT=mexsg64

# GL variables
HAVE_MESA 	:= false
HAVE_OPENGL 	:= true
