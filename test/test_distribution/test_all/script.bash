#!/bin/bash -ex
#
# Test that running distribute.bash and then setup.py results in a working system.

# Unset configuration file environment variables as they may interfere.
unset YAM_PROJECT_CONFIG_DIR
unset YAM_PROJECT

# We expect a tar to be produced with the filename "pyam-<version>.tar.gz"
base_directory_name=$(../../../pyam --version 2>&1 | sed 's/ /-/')
tar_filename="$base_directory_name.tar.gz"

# Clean up from previous tests
rm -rf "$tar_filename"
rm -rf "$base_directory_name"
rm -rf 'install_directory'

rm -f "$tar_filename"
../../../distribute.bash .

output=$(tar xf "$tar_filename" 2>&1)
if [ $? -ne 0 ]
then
    echo "ERROR: Could not untar file \"$tar_filename\""
    echo "$output"
    exit 2
fi

# Change to untarred directory and run setup.py install
cd "$base_directory_name"
output=$(./setup.py install --single-version-externally-managed --record record --prefix='../install_directory')
if [ $? -ne 0 ]
then
    echo "$output"
    exit 1
fi
cd ..

# Set paths to the test installation
PYTHON_VERSION=$(python --version | grep -o -E '3.[0-9]{1,2}')
if [[ "$(echo -e "3.11\n$PYTHON_VERSION" | sort -V | head -n1)" == "3.11" ]]; then
    # We do not have the "local" path if the Python version is >= 3.11
    INSTALL_DIR=/install_directory
else
    INSTALL_DIR=/install_directory/local
fi
export PATH="$PWD$INSTALL_DIR/bin:$PATH"
site_package_path=$(readlink -f ./$INSTALL_DIR/lib/python$PYTHON_VERSION/site-packages)
export PYTHONPATH="$site_package_path/:$PYTHONPATH"

# Check that we are pointing to the test installation's pyam
found_pyam_path=$(which pyam)
resolved_found_pyam_path=$(readlink -f "$found_pyam_path")
correct_pyam_path=$(readlink -f ./$INSTALL_DIR/bin/pyam)
if [ "$resolved_found_pyam_path" != "$correct_pyam_path" ]
then
    echo "ERROR: The test installation of pyam should be found, but it isn't"
    exit 2
fi

# Check for some data files
if ! stat ./$INSTALL_DIR/lib/python*/site-packages/yam/make_build_system_data/SiteDefs/makefile-yam-tail.mk > /dev/null 2>&1
then
    echo "ERROR: makefile-yam-tail.mk should exist"
    exit 2
fi

if ! stat ./$INSTALL_DIR/lib/python*/site-packages/yam/make_build_system_data/SiteDefs/Drun > /dev/null 2>&1
then
    echo "ERROR: Drun should exist"
    exit 2
fi

if ! stat ./$INSTALL_DIR/lib/python*/site-packages/yam/make_build_system_data/SiteDefs/mkHome/auto/bldRules.mk > /dev/null 2>&1
then
    echo "ERROR: bldRules.mk should exist"
    exit 2
fi

# Run a trivial command
pyam --version >& /dev/null
if [ $? -ne 0 ]
then
    echo 'ERROR: pyam --version failed'
    exit 2
fi

# Make sure we can import the test installation's yam Python package
./yam_package_path.py "$(readlink -f ./$INSTALL_DIR/lib/python*/site-packages/yam/__init__.py)"
if [ $? -ne 0 ]
then
    exit 2
fi

# Clean up
rm -rf "$tar_filename"
rm -rf "$base_directory_name"
rm -rf 'install_directory'

echo 'OK'
