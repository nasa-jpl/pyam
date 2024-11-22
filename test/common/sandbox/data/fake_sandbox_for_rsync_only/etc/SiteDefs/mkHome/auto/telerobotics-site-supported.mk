# Defines the following optional variables that specify the
# supported/unsupported targets for the site
#
# Keep in mind that these settings are included in after the
# module's optional .supported.mk file has been included to set
# these same variables

# The SITE_RELEASES_DIR variable points to the module/packages releases area
# specific to this site.

# these variables define  the OSs' supported for the site
# SITE_SUPPORTED_OS   =
# SITE_UNSUPPORTED_OS +=

# these  variables  restrit the available  list of targets
SITE_RELEASES_DIR  :=
SITE_SUPPORTED_TARGETS   = i486-cygwin i486-fedora13-linux i486-fedora4-64linux i486-fedora4-linux i486-fedora6-linux i486-fedora7-linux i486-fedora8-linux i486-fedora9-linux i486-mingw i486-rh9-linux i486-visualc mips-irix6.5 mips-irix6.5-gcc ppc-vxworks5.5.1 sparc-sunos5.9 sparc-sunos5.9-CC sun4-vxsim2.2 x86_64-fedora11-linux x86_64-fedora13-linux x86_64-fedora15-linux x86_64-fedora9-linux x86_64-rhel4-linux
# SITE_UNSUPPORTED_TARGETS   =

# host computer to use (with rsh) when building for each target architecture
#    (when the current host does not build the desired target)
#            target archos	   host name
#            ---------------	   ----------
COMPILE_HOST-i486-cygwin	 :=
COMPILE_HOST-i486-fedora13-linux	 :=
COMPILE_HOST-i486-fedora4-64linux	 :=
COMPILE_HOST-i486-fedora4-linux	 :=
COMPILE_HOST-i486-fedora6-linux	 :=
COMPILE_HOST-i486-fedora7-linux	 :=
COMPILE_HOST-i486-fedora8-linux	 :=
COMPILE_HOST-i486-fedora9-linux	 :=
COMPILE_HOST-i486-mingw	 :=
COMPILE_HOST-i486-rh9-linux	 :=
COMPILE_HOST-i486-visualc	 :=
COMPILE_HOST-mips-irix6.5	 :=
COMPILE_HOST-mips-irix6.5-gcc	 :=
COMPILE_HOST-ppc-vxworks5.5.1	 :=
COMPILE_HOST-sparc-sunos5.9	 :=
COMPILE_HOST-sparc-sunos5.9-CC	 :=
COMPILE_HOST-sun4-vxsim2.2	 :=
COMPILE_HOST-x86_64-fedora11-linux	 :=
COMPILE_HOST-x86_64-fedora13-linux	 :=
COMPILE_HOST-x86_64-fedora15-linux	 := roberson
COMPILE_HOST-x86_64-fedora9-linux	 :=
COMPILE_HOST-x86_64-rhel4-linux	 :=
