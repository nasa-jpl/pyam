#!/bin/bash

# Python modules should not refer Email class directly.
# Only pyam should know about Email.

for file in `find ../../../yam/ -name "*.py" -a -not -iname 'Email.py'`
do
	echo -n '.'

        found_line=$(../../common/token/find_token.py --name Email "$file")
	if [ $? -eq 0 ]
	then
		echo "ERROR: Found line '$found_line' in '$file', which is a reference to Email. None of the Yam modules know about Email. That is only of concern to the top-level yam utility."
		exit 2
	fi
done
echo

echo 'OK'
