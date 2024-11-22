#!/bin/bash
#
# Test loading configuration file based on environment variables.

export YAM_PROJECT_CONFIG_DIR='fake_configuration_directory'
export YAM_PROJECT='FakeProject'

# Unset YAM_ROOT or it will interfere.
# Makefile.yam will pick up the real sandbox that contains the pyam module.
unset YAM_ROOT

../../../../pyam --help |& grep 'parsing error' > /dev/null
if [ $? -ne 0 ]
then
    echo 'ERROR: Output should mention error parsing bad configuration file.'
    echo "$output"
    exit 2
fi

echo 'OK'
