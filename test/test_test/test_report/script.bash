#!/bin/bash
#
# Make sure that test/report is not under version control. We links to it
# under etc so that yam will complain if the user has not run the regression
# tests.

svn ls ../../report >& /dev/null
if [ $? -eq 0 ]
then
    echo 'ERROR: test/report should not be under version control'
    exit 2
else
    echo 'OK'
fi
