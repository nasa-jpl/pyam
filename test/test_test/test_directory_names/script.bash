#!/bin/bash -ex
#
# Make sure test directories are named consistently.
# Except for unit tests, which are named by class name, directories should
# be named using lowercase letters with underscores separating words.

for directory in $(find .. -type d -name 'test_*' 2>&1 | grep -v 'test_unit/' | grep -v 'test_unit_test_coverage/')
do
    if echo $directory | grep '[A-Z]' > /dev/null
    then
        echo "ERROR: Directory '$directory' is named incorrectly. Except for unit tests, which are named by class name, directories should be named using lowercase letters with underscores separating words."
        exit 2
    fi
done
echo OK
