#!/bin/bash
#
# Check for unused functions.

unused=$(./vulture.py ../../../yam/*.py ../../../pyam ../../../pyam-block-until-release ../../../pyam-build | grep -v -f exceptions.txt -f false_positives.txt)
if [ -n "$unused" ]
then
    echo "$unused"
    exit 2
else
    echo 'OK'
fi
