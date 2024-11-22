#!/bin/bash

grep '__del__' ../../../yam/*.py
if [ $? -eq 0 ]
then
    echo 'Do not define __del__() as it is not guaranteed to be called. Define an explicit close() or define an __exit__().'
    exit 2
fi
