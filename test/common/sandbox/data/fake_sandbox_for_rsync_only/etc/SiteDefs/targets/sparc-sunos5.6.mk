# set generic (site independent) target specific variables

CC_DEFINES 		+= -DSUNOS5
CC_LIBS 		+= -lm -lnsl -lsocket -lposix4
SHARED_COMPILE_FLAG	:= -fPIC

# the equivalent RTI target name
RTI_TARGET 		:= sparcSol2.6

# libkcs (Kodak format library needed by Scope for Solaris 5.6 and later
export LIBKCS 		:= -lkcs

# extension to use for building Mex wrappers for Dshell models
MEXEXT			:= mexsol
