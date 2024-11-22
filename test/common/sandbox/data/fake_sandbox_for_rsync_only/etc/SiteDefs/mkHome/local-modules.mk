# this file defines additional rules that are specific to the YaM
# installation

# rules for both work and link modules
YAM_LINKMOD_RULES += install-doxygen-docs setup-doxygen-docs

# rules for only work modules
YAM_WORKMOD_RULES += moddeps sanitizeSrc

moddeps:
	$(YAM_ROOT)/etc/SiteDefs/module-dependencies.pl -outfile $(MODDEPSFILE)

#======================================================
export GENERATE_TAGFILE := $(YAM_ROOT)/src/$(MODULE_NAME)/doc/doxy-$(MODULE_NAME).tag

install-doxygen-docs: doxfiles
        ifeq ($(HAVE_DOXYGEN),true)
	    rm -rf $(DOXYGEN_DOCS_DIR)/modules/$(MODULE_NAME)/html
	    $(MAKE) -f Makefile.yam doxygen-docs DOXYGEN_GENERATE_HTML=YES DOXYGEN_CONFIG=$(DOXYGEN_DOCS_DIR)/Doxyfile-modules TAGFILES_EXPANDED="$(foreach file, $(DOXYGEN_TAGFILES),$(DOXYGEN_DOCS_DIR)/modules/$(file)/doxy-$(file).tag=$(WWW_URL)/modules/$(file)/html ) " DOXYGEN_OUTPUT_DIRECTORY=$(DOXYGEN_DOCS_DIR)/modules/$(MODULE_NAME) PROJECT_NAME="$(MODULE_NAME) module"
        endif

#======================================================
# flag to indicate the need to break up the rule into pieces using xargs
# when it is too long for the shell
USE_XARGS=0
ifeq ($(YAM_NATIVE),mips-irix6.5)
  USE_XARGS=1
endif

ifeq ($(YAM_NATIVE),mips-irix6.5-gcc)
  USE_XARGS=1
endif

# set this to "-t" to get a trace of what xargs is doing below
TRACE_XARGS =
