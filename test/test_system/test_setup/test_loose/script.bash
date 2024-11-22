#!/bin/bash
#
# Set up a sandbox created from a list of module names.

# Unset configuration file environment variables as they may interfere.
unset YAM_PROJECT_CONFIG_DIR
unset YAM_PROJECT

# Use absolute path to avoid getting some possibly aliased version
PYAM=$(readlink -f ../../../../pyam)

release_directory=$(readlink -f './fake_release_area')

temporary_directory=$(mktemp --directory)
sandbox_directory="$temporary_directory/example_sandbox"

# Start MySQL server
source ../../../common/mysql/mysql_server.bash
start_read_only_mysql_server '../../../common/mysql/example_yam_for_import.sql'
port=$READ_ONLY_MYSQL_SERVER_PORT

# Create fake SVN repository
fake_repository_path="$temporary_directory/fake_repository"
../../../common/svn/make_fake_repository.bash "$fake_repository_path"
fake_repository_url="file://`readlink -f \"$fake_repository_path\"`"

# Run actual pyam command
"$PYAM" --quiet --release-directory="$release_directory" \
        --no-build-server --database-connection="127.0.0.1:$port/test" \
        --default-repository-url="$fake_repository_url" \
        setup --directory="$sandbox_directory" --modules DshellEnv

debugMessage()
{
    echo "See temporary sandbox which should be in \"$temporary_directory/example_sandbox\""
}

# Confirm that expected files were created
if [ ! -d "$sandbox_directory" ]
then
    echo 'ERROR: sandbox is missing'
    debugMessage
    exit 1
fi

if [ ! -d "$sandbox_directory/common" ]
then
    echo 'ERROR: "common" directory is missing'
    debugMessage
    exit 1
fi

if [ ! -e "$sandbox_directory/YAM.config" ]
then
    echo 'ERROR: "YAM.config" is missing'
    debugMessage
    exit 1
fi

if [ ! -e "$sandbox_directory/Makefile" ]
then
    echo 'ERROR: "Makefile" is missing'
    debugMessage
    exit 1
fi

# Make sure that the sandbox directory is not an SVN working directory
svn info "$sandbox_directory" &> /dev/null
if [ $? -eq 0 ]
then
    echo "ERROR: Sandbox should not be a working directory."
    debugMessage
    exit 1
fi

# Check that the sandbox directory is checked out from "common/trunk"
actual_common_url=$(svn info "$sandbox_directory/common" | grep '^URL:' | awk '{print $2}')
expected_common_url="$fake_repository_url/common/trunk"
if [ "$actual_package_url" != "$expected_package_url" ]
then
    echo "ERROR: Based on the SVN URL of the sandbox, it looks like it isn't checked out from a tagged package. See below."
    echo "Expected URL: $expected_common_url"
    echo "Actual URL: $actual_common_url"
    debugMessage
    exit 1
fi

# Clean up
rm -rf "$fake_repository_path"
rm -rf "$temporary_directory"

echo 'OK'
