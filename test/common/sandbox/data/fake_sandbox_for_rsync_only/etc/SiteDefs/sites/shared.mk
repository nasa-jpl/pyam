# commonly used flags in make process shared by all sites. The site specific
# files can override these settings.

# This file is meant to included by the site specific site.local file

#export BUILDING_SHARED_LIBS
export MODULE_SUPPORTED_TARGETS
export SHARED_LIBDIR
export CC CPLUSPLUS
export CC_DEFINES CPLUSPLUS_DEFINES
export CC_DEPEND_FLAG CPLUSPLUS_DEPEND_FLAG
export CC_WARNINGS CPLUSPLUS_WARNINGS
export CC_OPTIMIZATION  CPLUSPLUS_OPTIMIZATION
export F77
export LIBF77

export USE_GCC295


export HAVE_MATLAB
export HAVE_SIMULINK
export HAVE_RTW
export HAVE_MATHEMATICA
export HAVE_G77
export HAVE_X
export HAVE_TRAMEL
export HAVE_MOTIF
export HAVE_MESA

export RTI_TARGET

export HAVE_TCL		= true
export HAVE_TK		= true
export HAVE_TIX		= true
export TCLSH		?= /home/atbe/pkgs/$(YAM_NATIVE)/bin/tclsh

export CPUSPLUS_EXCEPTIONS_FLAG = -exceptions

#export SGI_NATIVE_CC = /usr/bin/cc
#export SGI_NATIVE_CPLUSPLUS = /usr/bin/CC

# the strip binary to strip symbols from binaries & libraries

#===============================================================
ifneq ($(MODULE_NAME),DshellEnv)
  DOXYGEN_TAGFILES += DshellEnv
endif
export TAGFILES_EXPANDED = $(foreach file, $(DOXYGEN_TAGFILES), $(YAM_ROOT)/doc/$(file)/doxy-$(file).tag=$(YAM_ROOT)/src/$(file)/doc/doxygen/html )

WWW_DOCS_SUBDIR := DLabDocs
export DOXYGEN_DOCS_DIR := /home/dlab/repo/www/$(WWW_DOCS_SUBDIR)
export DOXYGEN_IMAGE_DIR := /home/dlab/repo/www/images/doxygen
export WWW_URL = http://dartslab.jpl.nasa.gov/internal/www/$(WWW_DOCS_SUBDIR)

INSTALLDOX_STR = $(foreach file, $(DOXYGEN_TAGFILES), -l doxy-$(file).tag@$(WWW_URL)/modules/$(file)/html )
export DOXYGEN_OUTPUT_DIRECTORY	?= $(YAM_ROOT)/src/$(MODULE_NAME)/doc/doxygen

export BUILT_DOXYGEN_DIR = /home/dlab/repo/www/DLabDocs/modules
# The modules that have doxygen have an 'html' dir, so limit the list to those
export BUILT_DOXYGEN_MODULES = $(subst /html,,$(subst $(BUILT_DOXYGEN_DIR)/,,$(wildcard $(BUILT_DOXYGEN_DIR)/*/html)))

#==================================================================
DOXYGEN_FILEPATTERNS_SRC  := *.h \
                             *.H \
                             *.cc \
                             *.cpp \
                             *.C \
                             *.cxx \
                             *.c \
                             *.py \
                             *.dox \
			     *.pod3_dox
DOXYGEN_FILEPATTERNS_SCMODEL	:= *.scmodel_dox
DOXYGEN_FILEPATTERNS_MODEL	:= *.model_dox *.reference_dox
DOXYGEN_FILEPATTERNS_MODELLIB	:= *.modellib_dox
DOXYGEN_FILEPATTERNS_BINS	:= *.pod1_dox
DOXYGEN_FILEPATTERNS_TCLCMD	:= *.podn_dox \
				   *.tcl_cmd_dox
DOXYGEN_FILEPATTERNS_OVERVIEW	:= *.pod7_dox
DOXYGEN_FILEPATTERNS_SWIG	:= *.swigdox

DOXYGEN_FILEPATTERNS	?= 	$(DOXYGEN_FILEPATTERNS_SRC) \
				$(DOXYGEN_FILEPATTERNS_SCMODEL) \
				$(DOXYGEN_FILEPATTERNS_MODEL) \
				$(DOXYGEN_FILEPATTERNS_MODELLIB) \
				$(DOXYGEN_FILEPATTERNS_BINS) \
				$(DOXYGEN_FILEPATTERNS_TCLCMD) \
				$(DOXYGEN_FILEPATTERNS_SWIG) \
				$(DOXYGEN_FILEPATTERNS_OVERVIEW)
export DOXYGEN_FILEPATTERNS

#==================================================================
# initialize some of the standard variables
_PROF			?=
NDDSHOME		?=
HAVE_DOXYGEN		?=
MEXEXT			?=

# in site-config-xxx
USE_GCC272              ?=
GCC_EXEC_PREFIX         ?=
USE_SHARED_LIBS         ?=

# in site-config-xxx
IV_INCDIR		?=
MOTIF_INCDIR		?=
HAVE_IV			?=
HAVE_LIBSITE		?=
HAVE_LIBIPC		?=
IV_LIBS			?=
LIBSTDCPP		?=

# module Makefile.yam
SKIP_STD_DEPENDS	?=
SKIP_STD_BINS		?=
SKIP_STD_LIBS		?=
SKIP_STD_CLEAN		?=
SKIP_YAM_VERSION	?=
FLAVOR			?=
MODULE_COMPILE_FLAGS	?=
DOXYGEN_DOCS		?=
DOXYGEN_TAGFILES	?=
ADDT_CSRCS		?=
ADDT_SOLIBS		?=
BUILD_STATIC_LIBS	?=
MODULE_DEPENDS_FLAGS	?=
SPHINX_DOCS		?=

# makefile-yam.mk
BUILD_STATIC_LIB	?=
BUILD_SHARED_LIB	?=
PROJ			?=
DOXYGEN_RULE		?=

# site.gcc
FPERMISSIVE_OPT		?=
FWRITABLE_STRINGS_OPT	?=


# from RsrAcsModels
#OBJ_YAMVERSION		?=
#BINPROJ			?=
#BINEXT			?=

# from Darwin2k

# from SWIFT
#QHULL_INC		?=
#QSLIM_INC		?=

# m68k-vxworks
# from Dspace
# RsrAcsModels
#LIBSSODO		?=

# mips-irix6.5
# EDLModels, EphemPropagayorModels

# sparc-sunos5.7
# aejTools
#LIB			?=
# Dmex
#LIBS-libDMexRTW		?=

# sparc-sunos5.7-CC
# Craft

# for converting POD documentation into HTML
SDFBIN			?=


POD2MAN         := /home/atbe/pkgs/bin/pod2man -center "Dshell/DARTS software"
POD2TEXT        := /home/atbe/pkgs/bin/pod2text
#POD2DOX        := /home/soa/dev/users/jain/builds/Dshell-main/src/pod2dox.pl
POD2DOX         := /home/atbe/sim-utils/bin/pod2dox.pl




#==========================================================
# set up RTI variables
# we still only have StethoScope 5.0x for VxWorks builds
ifeq ($(YAM_OS),vx)
#	SCOPE_50 = true
endif
ifdef RTIHOME
	RTI_OS = $(YAM_OS)
	ifdef SCOPE_50
		STETHOSCOPEHOME=$(RTIHOME)/scope.5.0d
		NDDSHOME=$(RTIHOME)/ndds.1.11q
		RTILIBHOME=$(RTIHOME)/rtilib.3.7l
	else
                # Have had to turn this off because we do not have an NDDS
                # compatible with RTILIB 4.0
		HAVE_NDDS = false
		STETHOSCOPEHOME=$(RTIHOME)/scope.5.3b
		RTILIBHOME=$(RTIHOME)/rtilib.4.0b
	endif

	SCOPEGCCEXT = gcc
	export SCOPE_INCDIR	= -I$(STETHOSCOPEHOME)/include/$(RTI_OS) \
			        -I$(STETHOSCOPEHOME)/include/share \
				-I$(RTILIBHOME)/include/share
	export SCOPE_LIBS	= $(STETHOSCOPEHOME)/lib/$(RTI_TARGET)$(SCOPEGCCEXT)/libscope.a \
			      $(RTILIBHOME)/lib/$(RTI_TARGET)$(SCOPEGCCEXT)/libutilsip.a

	ifdef SCOPE_50
	  	SCOPE_INCDIR	+= -DSCOPE_50
        else
		SCOPE_INCDIR	+= -DRTI_UNIX
	endif

  ifndef HAVE_SCOPE
	HAVE_SCOPE	= true
  endif

  ifndef HAVE_NDDS
	HAVE_NDDS	= true
  endif
endif
export HAVE_SCOPE
export HAVE_NDDS

#==========================================================
ifeq ($(YAM_OS),unix)
  HAVE_G77 = true
  HAVE_X = true
endif

ifeq ($(YAM_OS),vx)
  USE_GCC295 		= false
  BUILDING_SHARED_LIBS 	= false
  HAVE_MATLAB 		= false
  HAVE_SIMULINK 	= false
  HAVE_RTW 		= false
  HAVE_MATHEMATICA 	= false
  HAVE_X 		= false
  HAVE_MESA 		= false


  #===============================================================
  # define stardard VxWorks flags
  # needs definitions for WIND_BASE, WIND_HOST_TYPE, WIND_ARCH
  #   	     TORNADO_VERSION
  WIND_BIN	 	= $(WIND_BASE)/host/$(WIND_HOST_TYPE)/$(WIND_TARGET_TYPE)bin

  INT_GCC_EXEC_PREFIX	= ${WIND_BASE}/host/${WIND_HOST_TYPE}/lib/gcc-lib/


  # needed so that wtxtcl can be found
  export PATH          := $(PATH):$(WIND_BIN)

  # set the default for Tornado 2.0
  TORNADO_VERSION	?= 2.0

  ifeq ($(TORNADO_VERSION),2.0)
    # needed for munching C++ code
    export WTXTCL	= $(WIND_BIN)/wtxtcl $(WIND_BASE)/host/src/hutils/munch.tcl \
			     -asm $(WIND_ARCH)
  endif

  # set up Tcl variables
  export TCL_VERSION		= 8.0
  export TCL_INCDIR		= -I$(WIND_BASE)/host/include
  HAVE_TK 		= false
  HAVE_TIX 		= false

  #===========================================
  # C compiler and flags for the native target
  export CC	 		= $(WIND_BIN)/cc$(WIND_ARCH)
  export CC_DEPEND_FLAG		= -MM
  export CC_INCLUDES		+= -I$(WIND_BASE)/target/h

  export CC_WARNINGS		= -Wall -Wmissing-prototypes -Waggregate-return
  export CC_OPTIMIZATION	= -g -O2
#  export CC_OPTIMIZATION	= -g
  export CC_DEFINES		+= -DVXWORKS -ansi -nostdinc -fno-builtin \
				   -fvolatile -DRW_MULTI_THREAD -D_REENTRANT

  #==========================================================
  # C++ compiler and flags for the native target
  export CPLUSPLUS 		= $(CC)
  export CPLUSPLUS_DEPEND_FLAG	= $(CC_DEPEND_FLAG)
  export CPLUSPLUS_INCLUDES	+= -I$(WIND_BASE)/target/h
  export CPLUSPLUS_WARNINGS	= $(CC_WARNINGS) -Woverloaded-virtual -Wno-unused -Wno-aggregate-return -Wconversion
  export CPLUSPLUS_OPTIMIZATION	= -O2 -g -fno-default-inline -finline-functions
#  export CPLUSPLUS_OPTIMIZATION	= -g
  export CPLUSPLUS_DEFINES	+= $(CC_DEFINES)

  #==========================================================
  export AR			= $(WIND_BIN)/ar$(WIND_ARCH)
  export LD			= $(WIND_BIN)/ld$(WIND_ARCH)
  export RANLIB			= $(WIND_BIN)/ranlib$(WIND_ARCH)
  export NM	     		= $(WIND_BIN)/nm$(WIND_ARCH)

endif

HAVE_MESA	?= false
