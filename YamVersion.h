/**
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
#define PYAM_DVERSION_RELEASE "pyam-R1-26g"

/* define DVERSION macros and include Dversion.h to declare functions */
#define DVERSION_CPREFIX pyam
#define DVERSION_MODULE "pyam"
#define DVERSION_RELEASE PYAM_DVERSION_RELEASE
#include "Dversion.h"
