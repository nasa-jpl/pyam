#!/bin/bash

./check_spelling.py should_fail.py
# Should return nonzero exit code to indicate failure
if [ $? -ne 0 ]
then
	exit 0
else
	echo "ERROR: check_spelling should have failed, but it didn't return a nonzero error code"
	exit 1
fi
