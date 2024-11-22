#!/bin/bash -ex
#
# Test that setup.py correctly install pyam.

# Unset configuration file environment variables as they may interfere.
unset YAM_PROJECT_CONFIG_DIR
unset YAM_PROJECT

this_test_directory=$(pwd)

# Change to directory that contains setup.py
cd ../../..

install_directory="$this_test_directory/install_directory"
rm -rf "$install_directory"

output=$(./setup.py install --single-version-externally-managed --record record --prefix="$install_directory")
if [ $? -ne 0 ]
then
    echo "$output"
    exit 1
fi

# Confirm installation
PYTHON_VERSION=$(python --version | grep -o -E '3.[0-9]{1,2}')
if [[ "$(echo -e "3.11\n$PYTHON_VERSION" | sort -V | head -n1)" == "3.11" ]]; then
    # We do not have the "local" path if the Python version is >= 3.11
    INSTALL_DIR=$install_directory
else
    INSTALL_DIR=$install_directory/local
fi

if [ ! -e "$INSTALL_DIR/bin/pyam" ]
then
    echo "ERROR: \"$INSTALL_DIR/bin/pyam\" should exist"
    exit 1
fi

# Clean up
rm -rf "$install_directory"

echo 'OK'
