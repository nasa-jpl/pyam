# This file is included by the top-level Makefile. It is meant to contain
# rules and definitions unique for a YaM installation

# rules for both work and link modules
YAM_LINKMOD_RULES += install-doxygen-docs setup-doxygen-docs

# rules for only work modules
#YAM_BUILD_RULES += links depends libs libsso bins
#YAM_WORKMOD_RULES += $(YAM_BUILD_RULES) clean docs
YAM_WORKMOD_RULES += moddeps doxfiles sanitizeSrc

# define the "strip" command
ifeq ($(YAM_NATIVE),i486-linux)
  STRIP = strip -s
else
  STRIP = strip
endif

#=======================================================
# set environment variables for running regtest regression tests
# regression test output file
#export OELTEST_REPORT = $(YAM_ROOT)/report.regtest
# global destination logfile for "regtest" dtest runs
#export DTEST_LOGFILE = $(YAM_ROOT)/report.regtest
# global destination datafile for "regtest" dtest runs
export DTEST_DATAFILE = $(YAM_ROOT)/regtest.data
# concatenate all the module regression test reports
#export APPEND_OELTEST_REPORT = 1
# dtest runs should not append logs to existing log file for "regtest" dtest runs
export DTEST_APPENDLOG = 0
# dtest runs should append data to existing log file for "regtest" dtest runs
export DTEST_APPEND_DATAFILE = true

# global destination logfile for "regtest" dtest runs
export PLLDTEST_LOGFILE = $(YAM_ROOT)/report.pllregtest

# combine module level logs at end of finish up
# pllregtest::

pllregtest:: pllregtest-clean
pllregtest-clean:
	rm -f $(PLLDTEST_LOGFILE)

#=======================================================
# generate an index page for the coverage data
#lcov::
#	etc/SiteDefs/mkhome/shared/lcovIndex.sh $(YAM_ROOT)/src /home/dlab/repo/www/DLabDoc/coverage/index.html

#=======================================================
supp-map::
	@$(MAKE) -i --no-print-directory QUIET=1 RULE=$@ \
		$(foreach t, $(YAM_TARGETS), allmods-rule-target-$(t) )


regtest:: regtest-clean

regtest::
        ifneq ($(YAM_TARGET),$(REGRESSION_TEST_YAM_TARGET))
	  @echo ""
	  @echo "    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
	  @echo "    ! WARNING: The regression tests are meant to be !"
	  @echo "    !          run on '$(REGRESSION_TEST_YAM_TARGET)' platforms -  !"
	  @echo "    !          NOT the '$(YAM_TARGET)' platform        !"
	  @echo "    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
	  @echo ""
        endif

regtest-clean:
	@echo "DTEST Data file: $(DTEST_DATAFILE)"
	rm -f $(OELTEST_REPORT)
	rm -f $(DTEST_DATAFILE)


#=======================================================
# rule to prep source code to be deliverd
prepSource:
	@echo "Running prepSource rule"
	@$(MAKE) mklinks links sanitizeSrc clean-links


#=======================================================
# Cluster build rules

ifndef CLUSTERTAG
 export CLUSTERTAG := $(shell date '+%H%M%S')
endif

export CLUSTER_OUTDIR := cluster-$(CLUSTERTAG)

# no checkpoint, no rerun, cpu limit of 45min
QSUB = qsub -d $(YAM_ROOT) -c n -r n -l walltime=00:45:00 -j oe /home/atbe/dev/users/jain/builds/DevUtils/src/dev-utils/cluster/cluster.pbs

# move the modules (Spice, RoamsDev) that take a long time to build
WMODS = $(findstring Spice, $(WORK_MODULES)) $(findstring mathc90, $(WORK_MODULES)) $(findstring RoamsDev, $(WORK_MODULES)) $(filter-out Spice, $(filter-out mathc90, $(filter-out RoamsDev, $(sort $(WORK_MODULES) ) ) ) )

#QSUBSH = /home/atbe/dev/users/jain/builds/Dshell-main/src/qsub.sh
QSUBSH = qsub.sh
PMODS = $(sort $(LINK_MODULES) ) $(WMODS)

export CLUSTER_YAM_TARGET := i486-fedora4-64linux

OUTFILE = Log.cluster

#allcluster: initcluster mklinks-cluster finicluster

#mklinks-cluster finicluster

#allcluster: initcluster  mklinks-cluster links-cluster libs-cluster libsso-cluster bins-cluster finicluster

allcluster: initcluster mklinks-cluster links-cluster libs-cluster libsso-cluster bins-cluster finicluster

initcluster:
	mkdir $(CLUSTER_OUTDIR)
	rm -f $(OUTFILE)

finicluster:
	rm -rf $(CLUSTER_OUTDIR)

# $(foreach mod, $(PMODS), $(QSUB) -o $(CLUSTER_OUTDIR)/$*-$(mod) -N $*$(mod) -v MODULES=$(mod),RULE=$*,YAM_TARGET=$(CLUSTER_YAM_TARGET),YAM_SITE=$(YAM_SITE) ; sleep 1; )

# default name for the job
JOB ?= dummy

%-cluster:
#	sudo qmgr -c "create queue $(JOB)$*"
#	sudo qmgr -c "set queue $(JOB)$* queue_type = Execution"
#	sudo qmgr -c "set queue $(JOB)$* enabled = True"
	$(foreach mod, $(PMODS), $(QSUBSH)  $(JOB)  $* $(mod); )
	qstat.py $(JOB)$*
#	sudo qmgr -c "delete queue $(JOB)$*"
	cd $(CLUSTER_OUTDIR); cat $(foreach mod, $(PMODS),$*-$(mod) ) >> ../$(OUTFILE); rm *; cd ..


#=======================================================
# Web page generation rules

# Generate the index page for the coverage results from lcov and coverage.py.
coverage-html:
	$(YAM_ROOT)/etc/SiteDefs/mkHome/shared/coverageIndex.sh "$(YAM_ROOT)/src" \
	                                                        "$(YAM_ROOT)/etc/SiteDefs/mkHome/shared/maintainers.txt" \
	                                                        "." \
	                                                        "../coveragepy" \
	                                                        "/home/dlab/repo/www/DLabDocs/coverage/index.html"

#lcov-html: coverage-html
#	echo "lcov-html rule is deprecated. Use coverage-html instead."

# Generate the index page for the cppcheck results.
cppcheck-html:
	$(YAM_ROOT)/etc/SiteDefs/mkHome/shared/cppcheckIndex.sh "$(YAM_ROOT)/src" "$(YAM_ROOT)/etc/SiteDefs/mkHome/shared/maintainers.txt" "/home/dlab/repo/www/DLabDocs/cppcheck/index.html"

# Generate the index page for the coding style (dkwstyle and pylint) results.
codingstyle-html:
	$(YAM_ROOT)/etc/SiteDefs/mkHome/shared/codingstyleIndex.sh "$(YAM_ROOT)/src" \
	                                                           "$(YAM_ROOT)/etc/SiteDefs/mkHome/shared/maintainers.txt" \
	                                                           "." \
	                                                           "../dpylint" \
	                                                           "/home/dlab/repo/www/DLabDocs/codingstyle/index.html"

dkwstyle-html: codingstyle-html
	echo "dkwstyle-html rule is deprecated. Use codingstyle-html instead."


#=======================================================
# a generic help message
help::
	@echo ""
	@echo "This top-level makefile provides a convenient way to loop "
	@echo "  through all the modules in the sandbox and build the target rule"
	@echo "  for all of them. The available rules are:"
	@echo ""
	@echo "      mklinks: Export links for all link/work modules"
	@echo "      rmlinks: Remove exported links for all link/work modules"
	@echo "        links: Build the 'links' rule for all work modules"
	@echo "      depends: Build the 'depends' rule for all work modules"
	@echo "         docs: Build the 'docs' rule for all work modules"
	@echo "         libs: Build the 'libs' rule for all work modules"
	@echo "       libsso: Build the 'libsso' rule for all work modules"
	@echo "         bins: Build the 'bins' rule for all work modules"
	@echo "        clean: Build the 'clean' rule for all work modules"
	@echo "      regtest: Run available rgression tests all work modules"
	@echo "  sanitizeSrc: Remove unneeded source files from modules"
	@echo "     supp-map: Build the 'supp-map' rule for all work modules"
	@echo ""
	@echo "          all: Build the 'all' rule for all work modules"
	@echo "        build: Build the 'build' rule for all work modules"
	@echo "  clean-links: Remove top level link export directories"
	@echo "   prepSource: Initialize module source for delivery"
	@echo ""
	@echo "The list of link/work modules is normally derived from the "
	@echo "WORK_MODULES and LINK_MODULES settings in YAM.config."
	@echo "However to use only a subset of the modules you can set"
	@echo "the 'MODULES' variable to the list of modules as part of the"
	@echo "make command line. The corresponding sublist of link and work"
	@echo "modules will be extracted and used."
	@echo ""
	@echo "The following 'alltgt' rules additionally allow the building"
	@echo "  of rules for all the modules for all supported targets."
	@echo "  The ALLTGT variable can be used to restrict the 'alltgt' targets."
	@echo ""
	@echo "       alltgt-<xxx>: Build the 'xxx' rule for all modules"
	@echo ""
	@echo "Other available utility rules are: "
	@echo ""
	@echo "          help: Generate this message"
	@echo "   clean-links: Delete the top-level bin, doc, etc, include, lib directories"
	@echo "        config: Returns the branch names for all work modules"
	@echo "    cvs-update: Runs 'cvs update' for all the work modules"
	@echo "      cvscheck: Runs 'cvscheck' for all the work modules"
	@echo " release-diffs: Runs 'yam diff' for all the work modules"
	@echo "       rshtest: Check for access to the remote build hosts"
	@echo ""
	@echo "Recognized Unix targets: $(unix_targets)"
	@echo "Recognized VxWorks targets: $(vx_targets)"
	@echo ""
