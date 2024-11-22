# set generic (site independent) target specific variables

CC_DEFINES += -DVXWORKS -DCPU=PPC603 -D_GNU_TOOL -Dppc
CC_LIBS +=

# the equivalent RTI target name
RTI_TARGET = ppcVx5.3
