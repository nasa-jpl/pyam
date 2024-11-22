#!/bin/bash

# Python modules should not refer to concrete implementations of interfaces.
# The only file that should refer to concrete class is the pyam top-level utility.

echo "Checking files for references to SQL"
for file in `find ../../../yam/ -name "*.py" -a -not -iname '*sql*'`
do
	echo -n '.'

	found_line=`grep -i 'sql' "$file"`
	if [ $? -ne 1 ]
	then
		echo "ERROR: Found line '$found_line' in '$file', which is a reference to SQL. It should not have a reference to such a concrete implementation."
		exit 2
	fi
done
echo

echo "Checking files for references to SVN"
for file in `find ../../../yam/ -name "*.py" -a -not -iname '*svn*'`
do
	echo -n '.'

	found_line=`grep -i 'svn' "$file"`
	if [ $? -ne 1 ]
	then
		echo "ERROR: Found line '$found_line' in '$file', which is a reference to SVN. It should not have a reference to such a concrete implementation."
		exit 2
	fi
done
echo

echo 'OK'
