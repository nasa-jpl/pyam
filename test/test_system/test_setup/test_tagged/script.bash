#!/bin/bash
#
# Set up a sandbox created from a tagged package.

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
        setup --directory="$sandbox_directory" --revision-tag=R1-26q ROAMSDshellPkg

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

if [ -w "$sandbox_directory/common/YAM.modules" ]
then
    echo 'ERROR: Package data files should not be writable since it is from an old release'
    debugMessage
    exit 2
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

# Check that the sandbox directory is checked out from "Packages/.../releases/..."
actual_package_url=$(svn info "$sandbox_directory" | grep '^URL:' | awk '{print $2}')
expected_package_url="$fake_repository_url/Packages/ROAMSDshellPkg/releases/ROAMSDshellPkg-R1-26q"
if [ "$actual_package_url" != "$expected_package_url" ]
then
    echo "ERROR: Based on the SVN URL of the sandbox, it looks like it isn't checked out from a tagged package. See below."
    echo "Expected URL: $expected_package_url"
    echo "Actual URL: $actual_package_url"
    debugMessage
    exit 1
fi

# Check that the sandbox directory is checked out from "Packages/.../releases/.../common"
actual_common_url=$(svn info "$sandbox_directory/common" | grep '^URL:' | awk '{print $2}')
expected_common_url="$expected_package_url/common"
if [ "$actual_common_url" != "$expected_common_url" ]
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
