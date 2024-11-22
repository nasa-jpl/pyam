# set generic (site independent) target specific variables

CC_DEFINES 		+= -DIRIX5 -DNO_GCC -LANG:std -OPT:Olimit=0
# need the -LANG options for ANSI compatible C++ and ANSI compatible
# for loop scoping rules (eg. TerrainObject, GraphicsUtils modules)
#CC_DEFINES 		+= -LANG:std -LANG:ansi-for-init-scope=ON

CC_LIBS 		+=
CPLUSPLUS_DEFINES	+= $(CC_DEFINES)
CPLUSPLUS_LIBS 		+= $(CC_LIBS)

LIBSTDCPP		:= -lCio

SHARED_COMPILE_FLAG	:=

# the equivalent RTI target name
RTI_TARGET 		:= mipsIRIX6.4

# extension to use for building Mex wrappers for Dshell models
MEXEXT			:= mexsg64

# GL variables
HAVE_MESA 	:= false
HAVE_OPENGL 	:= true
