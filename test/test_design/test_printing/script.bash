#!/bin/bash

# Test that only the new-style print function is used rather than the print statement.
for file in `find ../../../yam/ -name '*.py'`
do
    found_line=`grep --max-count 1 '\<print\> *"' "$file" || grep --max-count 1 "\<print\> *'" "$file"`
    if [ $? -ne 1 ]
    then
            echo
            echo "ERROR: Found line '$found_line' in '$file', which looks like an old-style print statement. Use the new Python print function instead."
            exit 2
    fi
done

# Test that there is no printing at all in the library code.
# Only the top level pyam utility should print to standard out.
for file in `find ../../../yam/ -name '*.py'`
do
	echo -n '.'

	found_line=`grep --max-count 1 '\<print\> *(' "$file"`
	if [ $? -ne 1 ]
	then
		echo
		echo "ERROR: Found line '$found_line' in '$file', which indicates that the library code prints to standard out. Only the top level pyam utility should be allowed to print. For reporting errors in library code, throw errors. Do not print."
		exit 2
	fi
done
echo

echo 'OK'
