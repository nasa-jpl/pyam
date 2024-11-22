#!/bin/bash

# Unset YAM_ROOT or it will interfere.
# Makefile.yam will pick up the real sandbox that contains the pyam module.
unset YAM_ROOT

# Unset configuration file environment variables as they may interfere.
unset YAM_PROJECT_CONFIG_DIR
unset YAM_PROJECT

output=$(../../../../pyam --database-connection='fake:fake@fake:1234/fake' 2>&1)
echo "$output"| grep "too few arguments" > /dev/null
if [ $? -ne 0 ]
then
    echo 'ERROR: pyam did not print "too few arguments" message. See below.'
    echo "$output"
    exit 2
fi

echo 'OK'
