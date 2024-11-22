#======================================================
# rules to deal with YamVersion.h
ifneq ($(YAM_OS),vx)
  ifeq ($(shell test -r $(YAM_ROOT)/include/Dversion.h && echo true),true)
    OBJ_YAMVERSION = YamVersion.o
  endif
endif
