#!/bin/bash -ex
#
# Make sure we are testing this sandbox's pyam and not some globally installed
# pyam.

path_to_pyam=$(which pyam)
resolved_path_to_pyam=$(readlink -f $path_to_pyam)
correct_path_to_pyam=$(readlink -f  $YAM_ROOT/bin/pyam)
if [ "$resolved_path_to_pyam" != "$correct_path_to_pyam" ]
then
    echo "ERROR: Somehow we are testing the incorrect pyam. "which pyam" is pointing to \"$resolved_path_to_pyam\"."
    exit 2
fi

echo OK
