#############################################################################
# personal.mk \- Personal definitions and rules
#
# Put any additional personal definitions or rules here, & include this
# file at the top of your $(USERMAKEFILE) (usually makefile.common). The
# definitions here will over-ride those in stddefs.mk, etc.

#############################################################################
#
#  Choose among:
#  (1)  keep_state_dependency_rules.mk and sun's make
#  (2)  gcc_v1_dependency_rules and gmake  (for use with gcc 1.x)
#  (3)  gcc_v2_dependency_rules and gmake  (for use with gcc 2.x)









DEPENDENCY_RULES = $(RTIMAKEHOME)/gcc_v2_dependency_rules.mk
MAKE = gmake -r






############################################################################
#
# Stan's personal make rules.
#

# Include this here to pre-define VXVARIANTS and UNIXVARIANTS
include $(RTIMAKEHOME)/stddefs.mk

BACKUP = $(COMMONSOURCES) $(UNIXSOURCES) $(VXSOURCES) $(RTSSOURCES) \
	 $(USERMAKEFILE) $(HEADERS) $(SPECIALBACKUPS)

backup:
	manageBackupFiles -b Backup $(BACKUP)
diff:
	manageBackupFiles Backup $(BACKUP)
cmp:
	manageBackupFiles -c Backup $(BACKUP)

headers: $(HEADERS)
	echo $(HEADERS)

#end

#########################################################
#
# Abhi's rules
#
#MYCSHOME=/proj/nmp/users/jain/src/new/control-shell
