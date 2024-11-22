#!/bin/bash

# File system access should be done through an implementation of FileSystem.
# *Module and *Sandbox classes should not directly access the file system.

for file in `find ../../../yam/ -name '*module.py' -o -name '*sandbox*.py' -o -name 'file_system.py'`
do
    echo -n '.'

	
    found_line=$(grep -P '^(?!\s*#)(?=.*path\.exists|.*open\(|.*os\.walk|.*chmod)' "$file")
    if [ $? -ne 1 ]
    then
        echo "ERROR: Found line '$found_line' in '$file', which is a direct file system call. Module classes should make file system calls indirectly through the FileSystem interface for testability."
        exit 2
    fi
done
echo

echo 'OK'
