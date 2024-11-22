#!/bin/bash
#
# Test that setup.py fails are dependencies are not met.

this_test_directory=$(pwd)

# Make dependency requirement fail by causing fake Python packages to get
# imported
export PYTHONPATH="$this_test_directory/fake_packages:$PYTHONPATH"

# Change to directory that contains setup.py
cd ../../..

output=$(./setup.py 2>&1)
echo "$output" | grep pysvn | grep -i error > /dev/null
if [ $? -ne 0 ]
then
    echo 'ERROR: setup.py should have complained about "pysvn" being missing. See actual output below.'
    echo
    echo "$output"
    exit 2
fi

echo 'OK'
