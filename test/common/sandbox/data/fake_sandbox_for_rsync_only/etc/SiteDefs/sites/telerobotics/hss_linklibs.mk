# file specifying libraries needed by HSS from DHSS during the linking
# stage. This file is included by the HSS makefiles.

# The following point to 3rd party tools needed for the builds. These
# are currently only installed in the /home/atbe area.
# RTI_TARGET should be set to sparcSol2 for sparc-sunos5, and hppaUX9
# for hppa-hpux10 target
RTIHOME=/home/atbe/pkgs/src/rti
DHSS_SCOPE_DIR = $(RTIHOME)/scope.5.0d/lib/$(RTI_TARGET)
DHSS_RTILIBDIR = $(RTIHOME)/rtilib.3.7l/lib/$(RTI_TARGET)
#DHSS_SCOPE_DIR = /home/atbe/pkgs/src/rti/scope.5.0d/lib/$(RTI_TARGET)
#DHSS_RTILIBDIR = /home/atbe/pkgs/src/rti/rtilib.3.7l/lib/$(RTI_TARGET)

DHSS_LIBGCCDIR = /tps/lib

ifeq ($(HAVE_SCOPE),true)
  HSS_LINKLIBS = -lDshellScope \
        $(DHSS_SCOPE_DIR)/libscope.a \
        $(DHSS_RTILIBDIR)/libutilsip.a
endif

HSS_LINKLIBS += \
	-lDhss \
        -lDhssModels \
	-lDhss \
        -lDhssStubs \
        -lDshellExpr \
        -lDshell++ \
	-lDartsDgetset \
        -lDarts \
	-lSOA \
        -lDvalue \
        -lYAClasses \
        -lAtbeTclMesg \
        -lpsx \
        -lgnc-utl
