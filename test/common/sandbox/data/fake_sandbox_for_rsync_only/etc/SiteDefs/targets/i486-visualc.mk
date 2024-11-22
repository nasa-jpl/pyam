########################################################################
#
#      !!!!!! EDIT & CUSTOMIZE THIS FILE !!!!!!
#
########################################################################
#
# Defines site independent, but target specific build variables
#
# This file is included by overall.mk

CC_DEFINES += /D "_WIN32" /D "WIN32"
CC_LIBS += kernel32.lib user32.lib gdi32.lib comdlg32.lib \
	advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib \
	imm32.lib winmm.lib wsock32.lib

CPLUSPLUS_DEFINES       += $(CC_DEFINES)
CPLUSPLUS_LIBS          += $(CC_LIBS)
