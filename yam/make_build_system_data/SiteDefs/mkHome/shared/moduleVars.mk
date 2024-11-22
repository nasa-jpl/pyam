########################################################################
#
# !!!!!! DO NOT EDIT THIS FILE !!!!!!
#
# This file is created by pyam.
#
########################################################################
#
# Set some module specific flags

# get the name of the module directory
MODULE_DIR := $(notdir $(LOCAL_DIR))

# strip out any trailing revision numbers (for link modules)
export MODULE_NAME := $(shell echo $(MODULE_DIR) | sed 's/-R.-...*//')

# figure out whether this module a link or a work module
ifeq ($(findstring $(YAM_ROOT),$(LOCAL_DIR)),)
   MODULE_TYPE := link
else
  MODULE_TYPE := work
endif

# define relative (absolute) paths for exporting of links for work (link)
# modules
ifeq ($(MODULE_TYPE),link)
  RELLNK_DIR = $(LOCAL_DIR)
  RELMODLNK_DIR = $(LOCAL_DIR)
  RELTGTLNK_DIR = $(LOCAL_DIR)
else
  RELLNK_DIR = ../src/$(MODULE_NAME)
  RELMODLNK_DIR = ../../src/$(MODULE_NAME)
  RELTGTLNK_DIR = ../../src/$(MODULE_NAME)
endif
