#!/bin/bash -ex
#
# Check all Python files for coding style/correctness.

configuration_filename='../../../pylintrc'
if [ ! -r "$configuration_filename" ]
then
    echo "$configuration_filename is not readable"
    exit 1
fi

pylint --rcfile="$configuration_filename" --dummy-variables-rgx='^_+$' ../../../yam/*.py ../../../pyam ../../../setup.py ../../../pyam-block-until-release ../../../pyam-build
