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
SITE_SUPPORTED_TARGETS   = x86_64-fedora11-linux x86_64-fedora13-linux x86_64-fedora15-linux x86_64-fedora9-linux
# SITE_UNSUPPORTED_TARGETS   =

# host computer to use (with rsh) when building for each target architecture
#    (when the current host does not build the desired target)
#            target archos	   host name
#            ---------------	   ----------
COMPILE_HOST-x86_64-fedora11-linux	 :=
COMPILE_HOST-x86_64-fedora13-linux	 := cardano
COMPILE_HOST-x86_64-fedora15-linux	 :=
COMPILE_HOST-x86_64-fedora9-linux	 :=