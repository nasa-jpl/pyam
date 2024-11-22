# set generic (site independent) target specific variables

CC_DEFINES += -DSUNOS4 -DNO_TIMESPEC
CC_LIBS += -lm
RANLIB = ranlib

export USE_SHARED_LIBS = false

# the equivalent RTI target name
RTI_TARGET = sun4

# extension to use for building Mex wrappers for Dshell models
MEXEXT=mex4
