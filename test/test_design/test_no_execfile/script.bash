#!/bin/bash

# Test there is no use of execfile. There is no reason to do so in pyam code.
for file in `find ../../../yam/ -name '*.py'` ../../../pyam
do
    found_line=`../../../test/common/token/find_token.py --name 'execfile' "$file"`
    if [ $? -eq 0 ]
    then
        echo "ERROR: Found lines '$found_line' in '$file', which indicates use of execfile. Don't use execfile."
        exit 2
    else
        echo -n '.'
    fi
done
echo

echo 'OK'
