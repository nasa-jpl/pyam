#!/bin/bash

# To preserve encapsulation, prefer functions to static methods.

for file in `find ../../../yam/ -name '*.py'`
do
	echo -n '.'

	found_line=`grep --max-count 1 'staticmethod' "$file"`
	if [ $? -ne 1 ]
	then
		echo
		echo "ERROR: Found line '$found_line' in '$file', which indicates that a static method is defined. To preserve encapsulation, prefer functions over static methods."
		exit 2
	fi
done
echo

echo 'OK'
