#!/bin/bash -ex
#
# Test that distribute.bash correctly tars up pyam.

# Unset configuration file environment variables as they may interfere.
unset YAM_PROJECT_CONFIG_DIR
unset YAM_PROJECT

# We expect a tar to be produced with the filename "pyam-<version>.tar.gz"
base_directory_name=$(../../../pyam --version 2>&1 | sed 's/ /-/')
tar_filename="$base_directory_name.tar.gz"

rm -f "$tar_filename"
rm -rf "$base_directory_name"
../../../distribute.bash .

if [ ! -e "$tar_filename" ]
then
    echo "ERROR: Tar file \"$tar_filename\" should have been created"
    exit 2
fi

# Extract and check contents
output=$(tar xf "$tar_filename" 2>&1)
if [ $? -ne 0 ]
then
    echo "ERROR: Could not untar file \"$tar_filename\""
    echo "$output"
    exit 2
fi

# Clean up
rm "$tar_filename"

if [ ! -e "$base_directory_name/pyam" ]
then
    echo "ERROR: \"$base_directory_name/pyam\" should exist"
    exit 2
fi

if [ ! -e "$base_directory_name/setup.py" ]
then
    echo "ERROR: \"$base_directory_name/setup.py\" should exist"
    exit 2
fi

if [ ! -e "$base_directory_name/README.rst" ]
then
    echo "ERROR: \"$base_directory_name/README.rst\" should exist"
    exit 2
fi

if [ ! -e "$base_directory_name/README.pdf" ]
then
    echo "ERROR: \"$base_directory_name/README.pdf\" should exist"
    exit 2
fi

if [ ! -d "$base_directory_name/yam" ]
then
    echo "ERROR: "$base_directory_name/yam" should exist"
    exit 2
fi

# Clean up
rm -r "$base_directory_name"

echo 'OK'
