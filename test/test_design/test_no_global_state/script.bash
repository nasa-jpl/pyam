#!/bin/bash

# Test there is no use of global state.
for file in `find ../../../yam/ -name '*.py'` ../../../pyam
do
    found_line=`../../../test/common/token/find_token.py --keyword 'global' "$file"`
    if [ $? -eq 0 ]
    then
        echo "ERROR: Found lines '$found_line' in '$file', which indicates use of global state. Don't use globals."
        exit 2
    else
        echo -n '.'
    fi
done
echo

echo 'OK'
