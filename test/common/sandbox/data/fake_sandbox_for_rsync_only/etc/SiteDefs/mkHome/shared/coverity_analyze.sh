#!/bin/sh
#
# Analyze files related to this module (this includes the module's include directory).
# Assumes that the current working directory is the module directory.

tmp_module_name=`basename ${PWD}`
escaped_module_name=`echo ${tmp_module_name} | sed 's/+/\\\\+/g' | sed 's/\./\\\\./g'`
cov-format-errors --dir coverity_output -x -X --include-files="/${escaped_module_name}/" $@
