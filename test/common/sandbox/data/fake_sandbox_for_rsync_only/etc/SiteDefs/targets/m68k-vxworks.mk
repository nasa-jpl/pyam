# set generic (site independent) target specific variables

CC_DEFINES 		+= -DCPU=MC68040
CPLUSPLUS_DEFINES 	+= -DCPU=MC68040
WIND_ARCH		=  68k
#WIND_TARGET_TYPE   	=  m68k-wrs-vxworks

# the equivalent RTI target name
RTI_TARGET 		= m68kVx5.1
