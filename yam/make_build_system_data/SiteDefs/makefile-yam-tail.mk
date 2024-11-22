#
# Generic parts of Makefile.yam
#
# This file is included by Makefile.yam in a module's src directory.
# The module developer should set the following variables *BEFORE* including
# this file. All "lists" are space-separated.
#
# PROJ - What to build, either the name of a binary executable or a library (in
# which case $(PROJ) should start with "lib" and NOT contain a suffix such as
# .a or .so). If left blank, then no source files are compiled but the module
# can contain scripts and header files.
#
# FLAVORS - List of "flavors" of the module to build if FLAVORS is set to
# "FOO BAR", then each source file gets compiled with -DFOO for the "FOO"
# flavor and -DBAR for the "BAR" flavor. Object, dependency, and library files
# have "-FOO" or "-BAR" appended to them. For specifying different source
# files for each flavor, use "ifeq ($(FLAVOR),FOO)" in Makefile.yam, and append
# to CC_SRC (etc.) as appropriate for that flavor.
#
# INC_LINKS - List of public header files.
#
# BIN_LINKS - List of scripts, go in $(YAM_ROOT)/bin.
#
# DOC_LINKS - List of documentation files, go in $(YAM_ROOT)/doc.
#
# AS_SRC - List of .s/.ppc files to assemble.
#
# CC_SRC - List of .c files to compile.
#
# CPLUSPLUS_SRC - List of .cc files to compile.
#
# MODULE_COMPILE_FLAGS - Augments standard C pre-processor flags (-I, -D).
#
# LIBS - List of libraries to link in for shared libraries and binary
# executables.
#
# The following variables may be set to explicitly list which targets/OSs
# are supported or unsupported:
#
# MODULE_SUPPORTED_TARGETS
# MODULE_UNSUPPORTED_TARGETS
# MODULE_SUPPORTED_OS
# MODULE_UNSUPPORTED_OS
#
# To build multiple libraries or executables, specify PROJS variable instead
# of PROJ. Then define FLAVORS-*, AS_SRC-*, CC_SRC-*, CPLUSPLUS_SRC-*, and
# LIBS-* for each project listed in PROJS. In the future, might do this for
# MODULE_* variables as well.
#
# Makefile.yam is used by YAM scripts to build and link a module.
# This file should have rules for:
#     yam-mklinks yam-rmlinks links docs depends libs libsso bins clean regtest
# even if some are no-ops.
#
# Makefile.yam is the top-level Makefile for the module, and is the one a
# developer should invoke directly to rebuild a single module.
# Invoke it while in the module's checked out src directory.
#
# When invoked from the YAM scripts, this Makefile is passed values for
# YAM_NATIVE, YAM_ROOT, and YAM_TARGET variables.
#


PROJ_BINS ?=
PROJ_LIBS ?=
PROJ_BINS_INTERNAL ?=
PROJ_LIBS_INTERNAL ?=
CFLAGS-$(PROJ) ?=
LIBS-$(PROJ) ?= $(MODULE_LIBS)
LINKER-$(PROJ) ?=
CC_SRC-$(PROJ) ?=
CPLUSPLUS_SRC-$(PROJ) ?=
F77_SRC-$(PROJ) ?=
FLAVORS-$(PROJ) ?=

# make sure the '-o' below has a trailing space.
CC_OUTPUT_OPT ?= -o
CPLUSPLUS_OUTPUT_OPT ?= $(CC_OUTPUT_OPT)
# make sure the '-o' below has a trailing space.
LINK_OUTPUT_OPT ?= -o
# make sure the '-L' below has a trailing space.
LINK_LIBPATH_OPT ?= -L

LINKER_MAP :=
ifeq ($(YAM_TARGET),i486-visualc)
  LINKER_MAP = /MAP:$@.map
endif

CC_COMPILEONLY_OPT ?= -c
CPLUSPLUS_COMPILEONLY_OPT ?= $(CC_COMPILEONLY_OPT)

AR_OUTPUT_OPT ?=

FLAVOR_EXT-$(PROJ)-$(FLAVOR) ?=
MODEL_COMPILE_FLAGS ?=


ifneq ($(FLAVOR),)
  FAPP := $(YAM_TARGET)/$(FLAVOR)/
else
  FAPP := $(YAM_TARGET)/
endif

#------------------------------------------------------------------------------
# include a file from YaM that provides much common functionality
# look in SiteDefs/README for a description of this elaborate organization,
# just note that it does include the appropriate
# sites/fst/site-config-* file that specifies compilers and compilation options
#------------------------------------------------------------------------------

# Preserve backwards compatibility with the now deprecated MODULE_COMPILE_FLAGS
# variable.
MODULE_CFLAGS ?= $(MODULE_COMPILE_FLAGS)

# Handle compilation flags for VXWORKS top-level object file compilation.
ifeq ($(PROJ),VXOBJ)
  MODULE_CFLAGS += $(VX_CFLAGS)
endif

CC_COMPILE_FLAGS += $(CFLAGS-$(PROJ)) $(MODULE_CFLAGS)
CPLUSPLUS_COMPILE_FLAGS += $(CFLAGS-$(PROJ)) $(MODULE_CFLAGS)
F77_COMPILE_FLAGS += $(F77FLAGS-$(PROJ)) $(MODULE_CFLAGS)

# Generates a list for a library project of the libraries that will be built
# for all its flavors.
libflavs = $(addprefix $(YAM_TARGET)/,\
                    $(if $(FLAVORS-$(1)),\
                       $(foreach f, $(FLAVORS-$(1)),\
                           $(1)$(call flavext,$1,$(f))),\
                       $(1)))

# Gets the extension value for a project/flavor. The default is to use the
# flavor name, unless the FLAVOR_EXT-project-flavor variable in which case it
# is used. The special extension value "-NONE-" should be used to set an
# "empty" extension.
flavext = $(subst -NONE-,,$(if $(FLAVOR_EXT-$(1)-$(2)),$(FLAVOR_EXT-$(1)-$(2)),$(2)))

# Generates a list for a binary project of the binaries that will be built for
# all its flavors.
binflavs1 = $(addprefix $(YAM_TARGET)/,\
                    $(if $(FLAVORS-$(1)),\
                       $(foreach f, $(FLAVORS-$(1)),$(addsuffix $(f),$(1))),\
                       $(1)))

binflavs = $(addprefix $(YAM_TARGET)/,\
                    $(if $(FLAVORS-$(1)),\
                       $(foreach f, $(FLAVORS-$(1)),\
                           $(1)$(call flavext,$1,$(f))),\
                       $(1)))


ALLLIBS := $(foreach p, $(PROJ_LIBS),$(call libflavs,$(p)))

# Building DLLs requires linking in libraries contianing symbols that are
# needed by the DLL. To meet this cross-coupling needs, we need to enable
# static library builds for CYGWIN DLL building.

ifeq ($(BUILD_STATIC_LIBS),true)
  LIB_STATIC_TARGET_LINKS += $(addsuffix .$(LIB_SUFFIX),$(ALLLIBS))
endif

ifeq ($(BUILDING_SHARED_LIBS),true)
  LIB_TARGET_LINKS += $(addsuffix .$(LIB_SHARED_SUFFIX),$(ALLLIBS))
  ifeq ($(YAM_OS_TMP),windows)
    LIB_TARGET_LINKS += $(addsuffix .$(LIB_SHARED_SUFFIX).a,$(ALLLIBS))
  endif
endif



ifeq ($(YAM_OS),unix)
  ALLBINS := $(foreach p, $(PROJ_BINS),$(call binflavs,$(p)))
  BIN_TARGET_LINKS += $(ALLBINS)
else
    VXOBJ := $(addprefix $(FAPP),$(addsuffix .o, \
        $(notdir $(basename $(VX_CC_SRC) \
        $(VX_CPLUSPLUS_SRC) \
                                ))))
  BIN_TARGET_LINKS += $(VXOBJ)
endif


ifneq ($(wildcard $(LOCAL_DIR)/YamVersion.h),)
ifneq ($(INC_MODULE_LINKS),)
  INC_MODULE_LINKS += YamVersion.h
endif
endif

ifeq ($(HAVE_DOXYGEN),true)
ifeq ($(DOXYGEN_DOCS),true)
   # export the tag file so that we can run "ymk docs" in a sanbox with
   # only link modules
   ifneq ($(GENERATE_TAGFILE),)
      DOC_MODULE_LINKS += doc/doxy-$(MODULE_NAME).tag
   endif
endif
endif

# sanitizeSrc rule for removing doc directory.
sanitizeSrc-module::
	@rm -rf doc

# sanitizeSrc rule for removing test directories.
sanitizeSrc-module::
	@rm -rf test tests Test*

# Create arbitrary links in the export area.

# Rach subpath listed in EXTRA_NESTED_LINK_DIRS is created under
# YAM_ROOT in the sandbox.
#
# For each subpath, the files/dirs listed in the variable
# EXTRA_NESTED_LINKS_<subpath> are exported to this subpath.
#
# Example:
#   EXTRA_NESTED_LINK_DIRS := etc/aa/bb/cc rkk/extra/headers
#   EXTRA_NESTED_LINKS_etc/aa/bb/cc := tt/aa/bb dsdfds/dfss/nn/ff
#   EXTRA_NESTED_LINKS_rkk/extra/headers := tt/aa/bb1 dsdfds/dfss/nn/ff1
#
# In this exaple links to tt/aa/bb and dsdfds/dfss/nn/ff are exported
# to the YAM_ROOT/etc/aa/bb/cc directory, and links to tt/aa/bb1 and
# dsdfds/dfss/nn/ff1 are exported to the rkk/extra/headers directory.

ifneq ($(EXTRA_NESTED_LINK_DIRS),)

mklinks-module::
	@$(foreach p, $(EXTRA_NESTED_LINK_DIRS), $(call exportmklinks,$(p), $(EXTRA_NESTED_LINKS_$(p)),$(LOCAL_DIR));  )

rmlinks-module::
	@rm -rf $(foreach p, $(EXTRA_NESTED_LINK_DIRS), $(call exportrmlinks,$(p),$(EXTRA_NESTED_LINKS_$(p))) )

endif



# Handle the links for the PLUGINS.
ifeq ($(YAM_OS),vx)
PLUGINLIBS := $(addsuffix .$(LIB_SUFFIX), $(addprefix $(YAM_TARGET)/, $(PROJ_PLUGINS) ) )
else
PLUGINLIBS := $(addsuffix .$(LIB_SHARED_SUFFIX), $(addprefix $(YAM_TARGET)/, $(PROJ_PLUGINS) ) )
endif

ifneq ($(PLUGINLIBS),)

mklinks-module::
	@$(call exportmklinks,lib/$(YAM_TARGET)/PLUGINS, $(PLUGINLIBS),$(LOCAL_DIR))

rmlinks-module::
	@rm -f $(call exportrmlinks,lib/$(YAM_TARGET)/PLUGINS, $(PLUGINLIBS))

endif


# Handle the links for the Tcl packages.
ifeq ($(YAM_OS),vx)
TCLPKG_LIBS := $(addsuffix .$(LIB_SUFFIX), $(addprefix $(YAM_TARGET)/, $(PROJ_TCL_PKGS) ) )
else
TCLPKG_LIBS := $(addsuffix .$(LIB_SHARED_SUFFIX), $(addprefix $(YAM_TARGET)/, $(PROJ_TCL_PKGS) ) )
endif

ifneq ($(TCLPKG_LIBS),)

mklinks-module::
	@$(call exportmklinks,lib/$(YAM_TARGET)/TCLPKG, $(TCLPKG_LIBS),$(LOCAL_DIR))

rmlinks-module::
	@rm -f $(call exportrmlinks,lib/$(YAM_TARGET)/TCLPKG, $(TCLPKG_LIBS))

endif


ifeq ($(HAVE_PYTHON),true)

ifneq ($(findstring $(PROJ),$(PROJ_PYTHON_MODULES)),)
   SKIP_YAM_VERSION := true
endif

# Handle the links for the Python modules.
PROJ_PYTHON_MODULE_LIBS += $(PROJ_PYTHON_MODULES)

ifeq ($(YAM_OS),vx)
   PYTHON_TARGET_LINKS += $(addsuffix .$(LIB_SUFFIX), $(addprefix $(YAM_TARGET)/, $(PROJ_PYTHON_MODULE_LIBS) ) )
else
  ifeq ($(BUILDING_SHARED_LIBS),true)
     PYTHON_TARGET_LINKS += $(addsuffix .$(LIB_SHARED_SUFFIX), $(addprefix $(YAM_TARGET)/, $(PROJ_PYTHON_MODULE_LIBS) ) )
  endif
endif

ifneq ($(PYTHON_TARGET_LINKS),)

mklinks-module::
	@$(call exportmklinks,lib/$(YAM_TARGET)/PYTHON, $(PYTHON_TARGET_LINKS),$(LOCAL_DIR))

rmlinks-module::
	@rm -f $(call exportrmlinks,lib/$(YAM_TARGET)/PYTHON, $(PYTHON_TARGET_LINKS))

endif

# Python top-level modules
ifneq ($(PYTHON_LINKS),)

mklinks-module::
	@$(call exportmklinks,lib/PYTHON, $(PYTHON_LINKS),$(LOCAL_DIR))

rmlinks-module::
	@rm -f $(call exportrmlinks,lib/PYTHON, $(PYTHON_LINKS))

endif

# Python package links

# Create nested Python package links in the export area.

# Each subpath listed in PYTHON_PKGS is created under
# YAM_ROOT/lib/PYTHON in the sandbox.
#
# For each subpath, the files/dirs listed in the variable
# PYTHON_LINKS_<subpath> are exported to this subpath.
#
# Example:
#   PYTHON_PKGS := Dutils abc/def/ghj
#   PYTHON_LINKS_Dutils := python/DGraph.py python/DThread.py
#   PYTHON_LINKS_abc/def/ghj := my/link1 y/link2/agb
#
# In this exaple links to python/DGraph.py python/DThread.py are
# exported to the YAM_ROOT/lib/PYTHON/Dutils directory, and links to
# my/link1 and y/link2/agb are exported to the abc/def/ghj directory.

ifneq ($(PYTHON_PKGS),)

# Export link for tgt/_Darts_Py.a as lib/tgt-static/lib_Darts_Py.a for
# convenience in linking.
mklinks-module::
	@mkdir -p $(YAM_ROOT)/lib/$(YAM_TARGET)-static
	@$(foreach i, $(PROJ_PYTHON_MODULE_LIBS), \
           $(call exportsinglelink,lib/$(YAM_TARGET)-static/lib$(i).$(LIB_SUFFIX),$(YAM_TARGET)/$(i).$(LIB_SUFFIX),$(RELTGTLNK_DIR)) )
	@$(foreach p, $(PYTHON_PKGS), $(call exportmklinks,lib/PYTHON/$(p), $(PYTHON_LINKS_$(p)),$(LOCAL_DIR)); touch $(YAM_ROOT)/lib/PYTHON/$(p)/__init__.py;  )


rmlinks-module::
	@rm -f $(foreach i, $(PROJ_PYTHON_MODULE_LIBS), \
	       $(call exportrmlinks,lib/$(YAM_TARGET)-static, lib$(i).$(LIB_SUFFIX)) )
	@rm -rf $(foreach p, $(PYTHON_PKGS), $(call exportrmlinks,lib/PYTHON/$(p),$(PYTHON_LINKS_$(p))) )

endif

endif

ifneq ($(findstring $(PROJ),$(PROJ_JAVA_MODULES)),)
   SKIP_YAM_VERSION := true
endif

ifeq ($(YAM_OS),vx)
JAVA_TARGET_LINKS += $(addsuffix .$(LIB_SUFFIX), $(addprefix $(YAM_TARGET)/, $(PROJ_JAVA_MODULE_LIBS) ) )
else
  ifeq ($(BUILDING_SHARED_LIBS),true)
     JAVA_TARGET_LINKS += $(addsuffix .$(LIB_SHARED_SUFFIX), $(addprefix $(YAM_TARGET)/, $(PROJ_JAVA_MODULE_LIBS) ) )
  endif

  ifeq ($(BUILD_STATIC_LIBS),true)
     LIB_STATIC_TARGET_LINKS += $(addsuffix .a, $(addprefix $(YAM_TARGET)/, $(PROJ_JAVA_MODULE_LIBS) ) )
  endif
endif

ifneq ($(JAVA_TARGET_LINKS),)

mklinks-module::
	@$(call exportmklinks,lib/JAVA, $(SWIG_JAVA_PACKAGE),$(LOCAL_DIR))
	@$(call exportmklinks,lib/$(YAM_TARGET)/JAVA, $(JAVA_TARGET_LINKS),$(LOCAL_DIR))

rmlinks-module::
	@rm -f $(call exportrmlinks,lib/JAVA, $(SWIG_JAVA_PACKAGE))
	@rm -f $(call exportrmlinks,lib/$(YAM_TARGET)/JAVA, $(JAVA_TARGET_LINKS))

endif

# Java top-level modules
ifneq ($(JAVA_LINKS),)

mklinks-module::
	@$(call exportmklinks,lib/JAVA, $(JAVA_LINKS),$(LOCAL_DIR))

rmlinks-module::
	@rm -f $(call exportrmlinks,lib/JAVA, $(JAVA_LINKS))

endif

#------------------------------------------------------------------------------
# Rule for compiling a static library.
# Normally invokes another Makefile in a target subdirectory
# for MER, we just build shared libraries under VxWorks and static
# libraries under Unix (to avoid having to set LD_LIBRARY_PATH).
#------------------------------------------------------------------------------
PROJ_LIB_TARGETS := $(strip $(PROJ_LIBS) $(PROJ_LIBS_INTERNAL) $(PROJ_PLUGINS) $(PROJ_PYTHON_MODULE_LIBS) $(PROJ_TCL_PKGS) $(PROJ_JAVA_MODULE_LIBS))
PROJ_BIN_TARGETS := $(strip $(PROJ_BINS) $(PROJ_BINS_INTERNAL))
PROJ_TARGETS := $(strip $(PROJ_LIB_TARGETS) $(PROJ_BIN_TARGETS))

links-std: $(if $(strip $(PROJ_TARGETS) $(VX_CC_SRC) $(VX_CPLUSPLUS_SRC)),$(YAM_TARGET)/$(FLAVOR),)

$(YAM_TARGET)/$(FLAVOR):
	@echo "Creating $@ directory ..."
	@mkdir -p $@

#------------------------------------------------------------------------------
# SWIG rules
#------------------------------------------------------------------------------

# sanitizeSrc rule for removing swig directory.
sanitizeSrc-module::
	@rm -rf swig

ifneq ($(SWIG),)

.PHONY: swig

swigNew: $(foreach i, $(SWIG_WRAPPERS), \
                $(if $(SWIG_IFILE_PYTHON-$(i)), $(i)_swigwrap_Py.cc ) \
                $(if $(SWIG_IFILE_TCL-$(i)), $(i)_swigwrap_Tcl.cc ) \
               )

# Include in the SWIG dependency information.
ifeq ($(HAVE_PYTHON),true)
        # for some reason need the following line without which
        # SWIG_DEPFILES variable remains empty
        JUNK := 4
	SWIG_DEPFILES := $(foreach i, $(SWIG_WRAPPERS), \
                $(if $(SWIG_IFILE_PYTHON-$(i)), $(i)_swigwrap_Py.d ) )
    ifneq ($(SWIG_DEPFILES),)
        # LL := $(SWIG_DEPFILES) 66
        ifeq ($(COMPILING),true)
           -include $(SWIG_DEPFILES)
        endif
    endif
endif

ifeq ($(COMPILING),true)

  ifeq ($(HAVE_TCL),true)
	SWIG_DEPFILES := $(foreach i, $(SWIG_WRAPPERS), \
                $(if $(SWIG_IFILE_TCL-$(i)), $(i)_swigwrap_Py.d ) )
         ifneq ($(SWIG_DEPFILES),)
           -include $(SWIG_DEPFILES)
         endif
  endif


  ifeq ($(HAVE_JAVA),true)
	SWIG_DEPFILES := $(foreach i, $(SWIG_WRAPPERS), \
                $(if $(SWIG_IFILE_JAVA-$(i)), $(i)_swigwrap_Py.d ) )
         ifneq ($(SWIG_DEPFILES),)
           -include $(SWIG_DEPFILES)
         endif
  endif




endif


# Template rules for wrapper generation.
define swigtcl-TEMPLATE
$(1)_swigwrap_Tcl.d $(1)_swigwrap_Tcl.cc: $(SWIG_IFILE_TCL-$(1))
	$(SWIG) $(SWIG_TCL_INC) -tcl8 -c++ -I$(YAM_ROOT)/include $(SWIG_OPTIONS) -module $(1) -namespace -MMD -o $(1)_swigwrap_Tcl.cc $(SWIG_IFILE_TCL-$(1))
	@echo ""
endef

define swigpython-TEMPLATE
$(1)_swigwrap_Py.d $(1)_swigwrap_Py.cc $(1)_Py.py: $(SWIG_IFILE_PYTHON-$(1))
	# Run SWIG to auto-generate the wrapper files
	$(SWIG) $(SWIG_PYTHON_INC) -python -c++ -I$(YAM_ROOT)/include $(SWIG_OPTIONS) -module $(1)_Py -MMD -o $(1)_swigwrap_Py.cc $(SWIG_IFILE_PYTHON-$(1))
	# The following defines the import command to be added to the
	# auto-generated Python file to pull in required modules
	# SWIG_addimports_$(1):
	if test -w "$(1)_Py.py" ; \
          then \
            echo "Fixing $(1)_Py.py"; \
	    perl -pi.bak -e 's@import _$(1)_Py@import Dmain\n$(SWIG_PYIMPORTS_$(1))\nimport _$(1)_Py@g' $(1)_Py.py; \
            echo "Done fixing $(1)_Py.py"; \
          else \
            echo "Skipping fixing of read only $(1)_Py.py"; \
        fi;
endef

ifeq ($(HAVE_PYTHON),true)
# define the Python wrap generation rules
$(foreach i, $(SWIG_WRAPPERS), $(if $(SWIG_IFILE_PYTHON-$(i)),$(eval $(call swigpython-TEMPLATE,$(i)))))
endif

define swigjava-TEMPLATE
$(1)_swigwrap_Java.d $(1)_swigwrap_Java.cc: $(SWIG_IFILE_JAVA-$(1))
	mkdir -p $(SWIG_JAVA_PACKAGE)
	$(SWIG) -java -c++ -I$(YAM_ROOT)/include $(SWIG_OPTIONS) -package $(SWIG_JAVA_PACKAGE) -MMD -o $(1)_swigwrap_Java.cc -outdir $(SWIG_JAVA_PACKAGE) $(SWIG_IFILE_JAVA-$(1))
endef

ifeq ($(HAVE_TCL),true)
# define the Tcl wrap generation rules
$(foreach i, $(SWIG_WRAPPERS), $(if $(SWIG_IFILE_TCL-$(i)),$(eval $(call swigtcl-TEMPLATE,$(i)))))
endif

ifeq ($(HAVE_JAVA),true)
# Define the Java wrap generation rules.
$(foreach i, $(SWIG_WRAPPERS), $(if $(SWIG_IFILE_JAVA-$(i)),$(eval $(call swigjava-TEMPLATE,$(i)))))
endif


# Rules for documentation generation.
define swigdox-TEMPLATE
doc/$(1).swigdox: $(1).swigxml FORCE
	  $(YAM_ROOT)/bin/Drun -fep - swigdox $(1).swigxml doc/$(1).swigdox
	  rm -f $<

$(1).swigxml: $(SWIG_IFILE_TCL-$(1))
	$(SWIG) -xml -xmllite -c++ -I$(YAM_ROOT)/include $(SWIG_OPTIONS) -module $(1) -o $(1).swigxml $(SWIG_IFILE_TCL-$(1))
endef

# define the swigdox wrap generation rules
$(foreach i, $(SWIG_WRAPPERS), $(if $(SWIG_IFILE_TCL-$(i)),$(eval $(call swigdox-TEMPLATE,$(i)))))

endif

#------------------------------------------------------------------------------
# Dependency files
#------------------------------------------------------------------------------
depends-std:

ifdef DEPEND_MODULE_FLAGS
  $(warning "Error: The DEPEND_MODULE_FLAGS variable is no longer used")
endif

#******************************************************************************
# Compilation rules
#
# Note that all of the following rules are invoked while in
# a target-specific subdirectory.
#******************************************************************************

# list all object files to be produced by and linked into this compilation
OBJ := $(addsuffix .o, $(notdir $(basename $(CC_SRC-$(PROJ)) \
           $(CPLUSPLUS_SRC-$(PROJ)) $(F77_SRC-$(PROJ)) \
        )))

VPATH := $(sort $(dir $(CC_SRC-$(PROJ)) \
             $(CPLUSPLUS_SRC-$(PROJ)) $(F77_SRC-$(PROJ)) \
             $(VX_CC_SRC) $(VX_CPLUSPLUS_SRC) ) \
          )

# is munching for C++ code required?
ifdef WTXTCL
  MUNCHED_OBJ := $(addsuffix .o, $(notdir $(basename \
			 $(CPLUSPLUS_SRC-$(PROJ)) )))
endif

FLAVOR_EXT := $(call flavext,$(PROJ),$(FLAVOR))

OBJ := $(addprefix $(FAPP),$(OBJ))
MUNCHED_OBJ := $(addprefix $(FAPP),$(MUNCHED_OBJ))
DEPFILES := $(OBJ:.o=.d)

ifeq ($(SKIP_YAM_VERSION),false)
  ADD_YAMVERSION := $(findstring $(PROJ) ,$(PROJ_TCL_PKGS) ) $(findstring $(PROJ) ,$(PROJ_PYTHON_MODULES) )

  ifneq ($(strip $(ADD_YAMVERSION)),)
    ifneq ($(OBJ_YAMVERSION),)
      OBJ += $(FAPP)$(OBJ_YAMVERSION)
      CC_COMPILE_FLAGS += -DUSE_YAMVERSION
      CPLUSPLUS_COMPILE_FLAGS += -DUSE_YAMVERSION
    endif
  endif
endif


#------------------------------------------------------------------------------
# Dependency files
#------------------------------------------------------------------------------
libs-std:
ifeq ($(BUILD_STATIC_LIBS),true)
ifeq ($(PROJ),)
	@$(foreach p,$(PROJ_LIB_TARGETS), \
           $(MAKE) --no-print-directory -f Makefile.yam \
           PROJ=$(p) libs-std;)
else
ifeq ($(FLAVORS-$(PROJ)),)
	@$(MAKE) --no-print-directory -f Makefile.yam \
            PROJ=$(PROJ) $(YAM_TARGET)/ $(FAPP)$(PROJ).$(LIB_SUFFIX) COMPILING=true
else
	@$(foreach f, $(FLAVORS-$(PROJ)), \
           mkdir -p $(YAM_TARGET)/$(f); \
           printf "\n\t Creating library $(YAM_TARGET)/$(PROJ)$(call flavex\t,$(PROJ),$(f)).$(LIB_SUFFIX) of '$(f)' flavor ...\n\n"; \
           $(MAKE) --no-print-directory -f Makefile.yam \
           FLAVOR=$(f) PROJ=$(PROJ) $(YAM_TARGET)/$(f) $(YAM_TARGET)/$(PROJ)$(call flavext,$(PROJ),$(f)).$(LIB_SUFFIX) COMPILING=true; )
endif
endif
endif

#------------------------------------------------------------------------------
# Rule for compiling a shared library (which may link in static libraries)
# normally invokes another Makefile in a target subdirectory.
#------------------------------------------------------------------------------

libsso-std:
ifeq ($(BUILDING_SHARED_LIBS),true)
ifeq ($(PROJ),)
	    @$(foreach p,$(PROJ_LIB_TARGETS), \
                 $(MAKE) --no-print-directory -f Makefile.yam \
                          PROJ=$(p) libsso-std;)
else
ifeq ($(FLAVORS-$(PROJ)),)
ifeq ($(YAM_OS_TMP),windows)
	        $(MAKE) --no-print-directory -f Makefile.yam \
                          PROJ=$(PROJ) $(YAM_TARGET)/ $(FAPP)$(PROJ).dll COMPILING=true
else
	        $(MAKE) --no-print-directory -f Makefile.yam \
                          PROJ=$(PROJ) $(YAM_TARGET)/ $(FAPP)$(PROJ).$(LIB_SHARED_SUFFIX) COMPILING=true
endif
else
ifeq ($(YAM_OS_TMP),windows)
	       @$(foreach f, $(FLAVORS-$(PROJ)), \
                  mkdir -p $(YAM_TARGET)/$(f); \
                  printf "\n\t Creating library $(YAM_TARGET)/$(PROJ)$(call flavex\t,$(PROJ),$(f)).$(LIB_SHARED_SUFFIX) of '$(f)' flavor ...\n\n"; \
	          $(MAKE) --no-print-directory -f Makefile.yam \
                      FLAVOR=$(f) PROJ=$(PROJ) $(YAM_TARGET)/$(f) $(YAM_TARGET)/$(PROJ)$(call flavext,$(PROJ),$(f)).dll COMPILING=true; )
else
	       @$(foreach f, $(FLAVORS-$(PROJ)), \
                  mkdir -p $(YAM_TARGET)/$(f); \
                  printf "\n\t Creating library $(YAM_TARGET)/$(PROJ)$(call flavex\t,$(PROJ),$(f)).$(LIB_SHARED_SUFFIX) of '$(f)' flavor ...\n\n"; \
	          $(MAKE) --no-print-directory -f Makefile.yam \
                      FLAVOR=$(f) PROJ=$(PROJ) $(YAM_TARGET)/$(f) $(YAM_TARGET)/$(PROJ)$(call flavext,$(PROJ),$(f)).$(LIB_SHARED_SUFFIX) COMPILING=true; )
endif
endif
endif
endif

#------------------------------------------------------------------------------
# Rule for compiling a binary executable (which may link in other libraries)
# normally invokes another Makefile in a target subdirectory.
#------------------------------------------------------------------------------
bins-std:
ifeq ($(YAM_OS),unix)
ifeq ($(PROJ),)
	    @$(foreach p,$(PROJ_BIN_TARGETS), \
                 $(MAKE) --no-print-directory -f Makefile.yam \
                          PROJ=$(p) bins-std;)
else
ifeq ($(FLAVORS-$(PROJ)),)
	      @$(MAKE) --no-print-directory -f Makefile.yam \
                          PROJ=$(PROJ) $(YAM_TARGET)/ $(FAPP)$(PROJ) COMPILING=true
else
	     @$(foreach f, $(FLAVORS-$(PROJ)), \
                mkdir -p $(YAM_TARGET)/$(f); \
                printf "\n\t Creating binary $(YAM_TARGET)/$(PROJ)$(call flavext,$(PROJ),$(f)) of '$(f)' flavor ...\n\n"; \
	        $(MAKE) --no-print-directory -f Makefile.yam \
                    FLAVOR=$(f) PROJ=$(PROJ) $(YAM_TARGET)/$(f) $(YAM_TARGET)/$(PROJ)$(call flavext,$(PROJ),$(f)); )
endif
endif
else
ifneq ($(VXOBJ),)
	    @$(MAKE) --no-print-directory -f Makefile.yam \
                        PROJ=VXOBJ VXOBJ COMPILING=true
endif
endif

#------------------------------------------------------------------------------
# rule for generating documentaiton
#------------------------------------------------------------------------------
ifeq ($(DOXYGEN_DOCS),true)
  DOXYGEN_RULE = doxygen-docs
endif

# thie predefined is needed by Dvalue
export DOXYGEN_PREDEFINED += __cplusplus

export DOXYGEN_WARN_FILE :=

# set default to not generate HTML or Latex output for speed
export DOXYGEN_GENERATE_HTML ?= NO
export DOXYGEN_GENERATE_LATEX ?= NO
export DOXYGEN_EXAMPLE_PATH ?= $(LOCAL_DIR)

%.1: %.pod
	@echo "Creating $@ ..."
	@$(POD2MAN) $< > $@

%.txt: %.pod
	@echo "Creating $@ ..."
	@$(POD2TEXT) $< > $@

%.html: %.pod
	@echo "Creating $@ ..."
	@$(POD2MAN) $< > $@
doc/%_dox: doc/%
	@echo "Creating $@ ..."
	@$(POD2DOX) $< > $@

# rule that module Makefiles can use to create dox files needed by the
# "docs" and "install-doxygen-docs" rules
doxfiles::

# rules for creating html docs from POD files
export DOXYGEN_ENABLED_SECTIONS
ifneq ($(MODEL_MODULE),true)
doxfiles:: $(addsuffix _dox, $(wildcard doc/*.pod?))
else
DOXYGEN_ENABLED_SECTIONS := standalone_model
endif

docs-std: docdir doxfiles docs-module $(DOXYGEN_RULE)

# create the doc/ dorectory if necessary
docdir:
	@mkdir -p doc

# converty POD files to HTML
doc/%.html: doc/%
	@echo "Creating $@ ..."
	@$(PERL) $(SDFBIN) +sdf2html_ -o- -ppod $< > $@

docshtml:
	$(MAKE) -f Makefile.yam docs DOXYGEN_GENERATE_HTML=YES

# this flag signifies whether a module's code has already been documented
# for Doxygen. Setting it to true causes only the documented information to
# be extracted, and warnings to be generated for code that is undocumented
DOXYGEN_DOCUMENTED ?= true
ifeq ($(DOXYGEN_DOCUMENTED),true)
  DOXYGEN_EXTRACT_ALL := NO
else
  DOXYGEN_EXTRACT_ALL := YES
endif
export DOXYGEN_EXTRACT_ALL

# enable the generation of XML Doxygen output for SWIG wrapped modules
export DOXYGEN_GENERATE_XML
ifneq ($(SWIG_WRAPPERS),)
DOXYGEN_GENERATE_XML := YES
endif

# default value for the Doxygen configuration file
DOXYGEN_CONFIG ?= $(YAM_ROOT)/doc/DshellEnv/Doxyfile-generic
doxygen-docs: doxygen-mesg
        ifeq ($(HAVE_DOXYGEN),true)
          ifeq ($(DOXYGEN_DOCS),true)
	    mkdir -p $(DOXYGEN_OUTPUT_DIRECTORY)
	    $(DOXYGEN) $(DOXYGEN_CONFIG)
            ifneq ($(SWIG_WRAPPERS),)
	      $(YAM_ROOT)/bin/Drun -fep - dox2docs.py doc/docstrings.i
            endif
          endif
        endif

#.PHONY: doc/%.swigdox
FORCE:

doxygen-mesg:
ifeq ($(HAVE_DOXYGEN),true)
ifeq ($(DOXYGEN_DOCS),true)
	@echo ">>>>> All Doxygen warnings will be saved in '$(DOXYGEN_WARN_FILE)' file <<<<<"
ifneq ($(DOXYGEN_DOCUMENTED),true)
	@echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
	@echo "WARNING:  $(MODULE_NAME) code does not yet have Doxygen documentation."
	@echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
endif
endif
else
	@echo ">>>>> Doxygen is not available for the $(YAM_TARGET) platform <<<<<"
endif
#------------------------------------------------------------------------------
# rule for cleaning up, just deletes all subdirectories for supported targets
#------------------------------------------------------------------------------

clean-std:
ifneq ($(SKIP_STD_CLEAN),true)
	/bin/rm -rf $(MODULE_SUPPORTED_TARGETS)
ifeq ($(DOXYGEN_DOCS),true)
	/bin/rm -rf doc/doxygen
	/bin/rm -rf doc/*.pod*_dox doc/*.swigdox
endif
endif


#=======================================================
#              Regular regtest rules
#=======================================================
# variable set to tests sub-directory path in module Makefile.yams
export DTEST_TESTDIR
DTEST_DATAFILE ?= regtest.data
DTEST_DATA_ARGS = --data=$(DTEST_DATAFILE)
ifeq ($(DTEST_APPEND_DATAFILE),true)
    DTEST_DATA_ARGS += --dataAppend
endif

RAWDTEST := $(YAM_ROOT)/bin/Drun dtest
DTEST := $(RAWDTEST) $(DTEST_DATA_ARGS)

regtest-module::
ifneq ($(DTEST_TESTDIR),)
	@$(DTEST) --dir $(DTEST_TESTDIR)
endif


#=======================================================
#              Parallel regtest rules
#=======================================================

# integrated log file with test results

ifeq ($(PROJ),regtest)
  PLLDTESTLOG := dtestlog
  # get list of all dtest tests
  ifneq ($(DTEST_TESTDIR),)
    REGTESTS := $(shell $(YAM_ROOT)/bin/Drun $(RAWDTEST) --dir $(DTEST_TESTDIR) --list)
  endif

  # replace '/' with '@' in test subpath
  sanitizetestname = $(subst /,@,$(1))

  # create a template rule for _run_test-XXX rules
  define runtest-TEMPLATE
    _run_$(1):
	  $(RAWDTEST) $(1) -l $(call sanitizetestname,dtestlog-_run_$(1))
  endef

  # Generate _run_test-XXX rules for all test cases
  $(foreach t, $(REGTESTS), $(eval $(call runtest-TEMPLATE,$(t))))

  # rule to run dtest regtests in parallel. Integrated log will be
  # in dtestlog file
  pllregtest:
        ifneq ($(REGTESTS),)
	  $(MAKE) -f Makefile.yam $(YAM_MKPLL) _pllregtest
        else
	  @echo "No parallel regtests for the module"
        endif

  # rule that does the real work of running tests in parallel
  _pllregtest: $(foreach t, $(REGTESTS), _run_$(t) )
	@echo "------------- COMBINING LOGS ------------"
	@rm -f $(PLLDTESTLOG)
	@$(foreach t, $^, cat $(DTEST_TESTDIR)/$(call sanitizetestname,dtestlog-$(t)) >> $(PLLDTESTLOG); )
	@rm -f $(foreach t, $^, $(DTEST_TESTDIR)/$(call sanitizetestname,dtestlog-$(t)) )
        ifneq ($(PLLDTEST_LOGFILE),)
	   cat $(PLLDTESTLOG) >> $(PLLDTEST_LOGFILE)
	   @echo "Test log in '$(PLLDTESTLOG)'"
        else
	   @echo "Test log in '$(PLLDTEST_LOGFILE)'"
        endif
endif



#------------------------------------------------------------------------------
# rule for running any available regression tests
#------------------------------------------------------------------------------

# this is needed for some regression tests where links for the test
# binaries are not being exported (built using PROJ_BINS_INTERNAL)
PATH := $(LOCAL_DIR):$(LOCAL_DIR)/$(YAM_TARGET):$(PATH)
export PATH

# this is needed for some regression tests where links for libraries
# needed for test binaries are not being exported (built using PROJ_LIBS_INTERNAL)
LD_LIBRARY_PATH := $(LOCAL_DIR)/$(YAM_TARGET):$(LD_LIBRARY_PATH)
export LD_LIBRARY_PATH

#------------------------------------------------------------------------------
# compile and link rules
#------------------------------------------------------------------------------

# rule to build a binary executable
# use the C++ compiler for the linking if we also need to
#    link in standard C++ libraries (for I/O streams, etc.)

# use MODULE_LINKER as default value if it is defined
ifneq ($(MODULE_LINKER),)
  MYLINKER := $(MODULE_LINKER)
endif

# if a PROJ specific LINKER is defined, use it
ifneq ($(LINKER-$(PROJ)),)
  MYLINKER := $(LINKER-$(PROJ))
endif

# the default linker
MYLINKER ?= $(CC)

# rules to build top level VxWorks object files
.PHONY: $(FAPP)VXOBJ
VXOBJ: $(VXOBJ)

ifneq ($(LINK_FLAGS-$(PROJ)),)
  PROJ_LINK_FLAGS := $(LINK_FLAGS-$(PROJ)) $(MODULE_LINK_FLAGS)
endif

ifeq ($(LINKER-$(PROJ)),)
  PROJ_LINK_FLAGS ?= $(CC_SHARED_LINK_FLAGS) $(MODULE_LINK_FLAGS)
else
  PROJ_LINK_FLAGS ?= $(CPLUSPLUS_SHARED_LINK_FLAGS) $(MODULE_LINK_FLAGS)
endif


# link rule for creating binaries for Unix targets
$(YAM_TARGET)/$(PROJ)$(FLAVOR_EXT): $(if $(PROJ),$(OBJ),)
    ifneq ($(PROJ),)
      ifneq ($(SKIP_STD_BINS),true)
        ifeq ($(strip $(OBJ)),$(FAPP)$(OBJ_YAMVERSION))
	  @echo "   >>>>>> WARNING - no real object files for $@ <<<<<<"
        endif
        ifeq ($(LINKER-$(PROJ)),)
	  $(MYLINKER) $(PROJ_LINK_FLAGS) $(LINK_OUTPUT_OPT)$@ $(LINKER_MAP) $(OBJ) $(LIBS-$(PROJ)) \
		$(LINK_LIBPATH_OPT)$(YAM_TARGET)/$(BIN_USE_FLAVOR) $(CC_LIBS)
        else
	  $(MYLINKER) $(PROJ_LINK_FLAGS) $(LINK_OUTPUT_OPT)$@  $(LINKER_MAP) $(OBJ) $(LIBS-$(PROJ)) \
		$(LINK_LIBPATH_OPT)$(YAM_TARGET)/$(BIN_USE_FLAVOR) $(CPLUSPLUS_LIBS)
        endif
        # copy over the binaries for the Cygwin platform
        ifeq ($(YAM_TARGET),i486-cygwin)
	  rm -f $(YAM_ROOT)/bin/$@
	  cp $@ $(YAM_ROOT)/bin/$@
        endif
        ifeq ($(YAM_TARGET),i486-visualc)
	  rm -f $(YAM_ROOT)/bin/$@.exe
	  cp $@ $(YAM_ROOT)/bin/$@.exe
        endif
	@echo ""
      endif
    endif

# rule to build static library
$(YAM_TARGET)/$(PROJ)$(FLAVOR_EXT).a : $(OBJ)
    ifneq ($(SKIP_STD_LIBS),true)
      ifeq ($(strip $(OBJ)),$(FAPP)$(OBJ_YAMVERSION))
	@echo "   >>>>>> WARNING - no real object files for $@ <<<<<<"
      endif
	$(AR) $(AR_FLAGS) $(AR_OUTPUT_OPT)$@ $(OBJ)
        ifneq ($(YAM_TARGET),i486-visualc)
	  $(RANLIB) $@
        endif
        ifeq ($(YAM_TARGET),i486-cygwin)
	  rm -f $(YAM_ROOT)/lib/$@
	  cp $@ $(YAM_ROOT)/lib/$(YAM_TARGET)
        endif
        ifeq ($(YAM_TARGET),i486-visualc)
	  rm -f $(YAM_ROOT)/lib/$@
	  cp $@ $(YAM_ROOT)/lib/$(YAM_TARGET)
        endif
	@echo ""
    endif

# rule to build shared library
$(YAM_TARGET)/$(PROJ)$(FLAVOR_EXT).so : $(OBJ)
    ifneq ($(SKIP_STD_LIBSSO),true)
      ifeq ($(strip $(OBJ)),$(FAPP)$(OBJ_YAMVERSION))
	@echo "   >>>>>> WARNING - no real object files for $@ <<<<<<"
      endif
	$(LD_SHARED) $(PROJ_LINK_FLAGS) $(LINK_OUTPUT_OPT)$@ $(OBJ) $(LIBS-$(PROJ)) $(CC_EXTRA_SHLIB)
	@echo ""
    endif

# rule to build dll under Cygwin and VisualC
$(YAM_TARGET)/$(PROJ)$(FLAVOR_EXT).dll : $(OBJ)
    ifneq ($(SKIP_STD_LIBSSO),true)
      ifeq ($(strip $(OBJ)),$(FAPP)$(OBJ_YAMVERSION))
	@echo "   >>>>>> WARNING - no real object files for $@ <<<<<<"
      endif
        ifeq ($(YAM_TARGET),i486-cygwin)
	  # from http://sources.redhat.com/ml/cygwin/2002-03/msg01454.html
	  $(CC) -shared -o $@ -Wl,--out-implib=$@.a \
                  -L$(YAM_ROOT)/lib/$(YAM_TARGET) \
                  -Wl,--export-all-symbols \
                  -Wl,--enable-auto-import \
                  -Wl,--whole-archive $(OBJ) \
                  -Wl,--no-whole-archive $(LIBS-$(PROJ)) $(CC_EXTRA_SHLIB)
        else
	  # Borrow the 'dlltool' utility from cygwin/gcc to create an export table
	  # This forces the DLL to export ALL symbols in it. Not great, but it works.
	  dlltool --output-def $@.def --export-all-symbols $(OBJ)
	  # Link the DLL using the above generated .DEF exports file.
	  $(LD_SHARED) /FORCE /DEF:$@.def /IMPLIB:$@.a $(LINKER_MAP) $(CPLUSPLUS_LINK_FLAGS) $(LINK_OUTPUT_OPT)$@ $(OBJ) $(LIBS-$(PROJ)) $(CC_EXTRA_SHLIB)
        endif
	rm -f $(YAM_ROOT)/lib/$@ $(YAM_ROOT)/lib/$@.a
	cp $@ $@.a $(YAM_ROOT)/lib/$(YAM_TARGET)
    endif

# rule to build VxWorks load library
$(YAM_TARGET)/$(PROJ)$(FLAVOR_EXT).ro : $(OBJ) $(if $(WTXTCL),$(FAPP)munch.o,)
    ifneq ($(SKIP_STD_LIBS),true)
      ifeq ($(strip $(OBJ)),$(FAPP)$(OBJ_YAMVERSION))
	@echo "   >>>>>> WARNING - no real object files for $@ <<<<<<"
      endif
	$(LD) -r -o $@ $^
	@echo ""
    endif

#=====================
# rules to build dependency .d files. The use of rules such as this
#  is documented in the Gnu make manual
ifeq ($(YAM_TARGET),i486-visualc)
  define deprule-cc
       touch $@
  endef
else
  define deprule-cc
	$(CC) $(CC_COMPILE_FLAGS) $(CC_DEPEND_FLAG) $(CC_COMPILEONLY_OPT) $< \
                  | sed "s!^$*.[ :]*!$@ $(FAPP)&!" > $@
  endef
endif

ifeq ($(YAM_TARGET),i486-visualc)
  define deprule-cplusplus
       touch $@
  endef
else
  define deprule-cplusplus
	$(CPLUSPLUS) $(CPLUSPLUS_COMPILE_FLAGS) $(CPLUSPLUS_DEPEND_FLAG) $(CC_COMPILEONLY_OPT) $< \
                  | sed "s!^$*.[ :]*!$@ $(FAPP)&!" > $@
  endef
endif

define deprule-f77
	$(F77) $(F77_COMPILE_FLAGS) $(CPLUSPLUS_DEPEND_FLAG) $(CC_COMPILEONLY_OPT) $< \
                  | sed "s!^$*.[ :]*!$@ $(FAPP)&!" > $@
endef

$(FAPP)%.d : $(YAM_TARGET)/$(FLAVOR)

$(FAPP)%.d : %.c
	$(deprule-cc)

$(FAPP)%.d : %.cc
	$(deprule-cplusplus)

$(FAPP)%.d : %.C
	$(deprule-cplusplus)

$(FAPP)%.d : %.cpp
	$(deprule-cplusplus)

$(FAPP)%.d : %.f
	$(deprule-f77)

# this will keep the .d files being treated as intermiediate files and be deleted
.SECONDARY:  $(DEPFILES)

# make sure .d file gets built for the .o files
$(FAPP)%.o : $(FAPP)%.d

# rule to compile C code
$(FAPP)%.o : %.c
	$(CC) $(CC_COMPILE_FLAGS) $(CC_COMPILEONLY_OPT) $< $(CC_OUTPUT_OPT)$@
	@echo ""

# rule to munch C++ code for VxWorks cross-compilation
# this rule is based upon the example in the VxWorks documentation
$(FAPP)munch.o : $(MUNCHED_OBJ)
	$(NM) $< | $(WTXTCL) > $(FAPP)munch.c
	$(CC) -c $(FAPP)munch.c -o $@
	@echo ""

$(FAPP)%.o : %.cc
	$(CPLUSPLUS) $(CPLUSPLUS_COMPILE_FLAGS) $(CPLUSPLUS_COMPILEONLY_OPT) $< $(CPLUSPLUS_OUTPUT_OPT)$@
	@echo ""

# another rule to compile C++ code
$(FAPP)%.o : %.C
	$(CPLUSPLUS) $(CPLUSPLUS_COMPILE_FLAGS) $(CPLUSPLUS_COMPILEONLY_OPT) $< $(CPLUSPLUS_OUTPUT_OPT)$@
	@echo ""

# another rule to compile C++ code
$(FAPP)%.o : %.cpp
	$(CPLUSPLUS) $(CPLUSPLUS_COMPILE_FLAGS) $(CPLUSPLUS_COMPILEONLY_OPT) $< $(CPLUSPLUS_OUTPUT_OPT)$@
	@echo ""

# rule for Fortran files
$(FAPP)%.o : %.f
	$(F77) $(F77_COMPILE_FLAGS) -c $< -o $@
	@echo ""

$(FAPP)YamVersion.o : $(YAM_ROOT)/include/Dversion.* YamVersion.h
ifeq ($(YAM_TARGET),i486-visualc)
	$(CC) -I. $(CC_COMPILE_FLAGS) $(TCL_INCDIR) $(CC_COMPILEONLY_OPT) `cygpath -w $<` $(CPLUSPLUS_OUTPUT_OPT)$@
else
	$(CC) -I. $(CC_COMPILE_FLAGS) $(TCL_INCDIR) $(CC_COMPILEONLY_OPT) $< $(CPLUSPLUS_OUTPUT_OPT)$@
endif
	@echo ""

# include in .d files if they exist
ifeq ($(COMPILING),true)
  ifneq ($(DEPFILES),)
    -include $(DEPFILES)
  endif
endif

#======================================================
# rule to print out variables specified from the command line
myvars1:
	@$(foreach i, $(MYVARS), echo "$i=<$($i)>";)
