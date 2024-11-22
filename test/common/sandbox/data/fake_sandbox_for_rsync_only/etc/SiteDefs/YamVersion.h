/*
 * YamVersion.h
 *
 * Header file that uses Dversion.h to provide functions to access
 * version information for a module
 */

/* make sure DVERSION macros are not already defined */
#ifdef DVERSION_CPREFIX
#undef DVERSION_CPREFIX
#endif
#ifdef DVERSION_MODULE
#undef DVERSION_MODULE
#endif
#ifdef DVERSION_RELEASE
#undef DVERSION_RELEASE
#endif

/* declare module-specific RELEASE macro for use by other modules */
#define SITEDEFS_DVERSION_RELEASE "SiteDefs-R1-79z"

/* define DVERSION macros and include Dversion.h to declare functions */
#define DVERSION_CPREFIX SiteDefs
#define DVERSION_MODULE "SiteDefs"
#define DVERSION_RELEASE SITEDEFS_DVERSION_RELEASE
#include "Dversion.h"
