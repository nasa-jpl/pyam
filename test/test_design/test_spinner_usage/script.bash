#!/bin/bash

# Make sure that Spinner is used properly.

for file in ../../../pyam
do
	echo -n '.'

        found_line=$(grep ' Spinner(' "$file")
	if [ $? -eq 0 ]
	then
		echo "ERROR: Found line '$found_line' in '$file', which indicates that Spinner is being used directly. Do no use Spinner directly. Use self.__spiner_class instead"
		exit 2
	fi

        spinner_count=$(grep 'spinner_class(' "$file" | wc -l)
        spinner_context_manager_count=$(grep 'spinner_class(' "$file" | grep 'with ' | grep ' as' | wc -l)
	if [ $spinner_count -ne $spinner_context_manager_count ]
	then
		echo "ERROR: In "$file" Spinner is not being used directly. It should be used with a 'with' statement so that it gets stopped automatically. It should not be instanced in the usual way."
		exit 2
	fi
done
echo

echo 'OK'
