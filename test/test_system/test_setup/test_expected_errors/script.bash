#!/bin/bash
#
# Test the expected error conditions of "pyam setup".

# Unset configuration file environment variables as they may interfere.
unset YAM_PROJECT_CONFIG_DIR
unset YAM_PROJECT

# Use absolute path to avoid getting some possibly aliased version
PYAM=$(readlink -f ../../../../pyam)

temporary_directory=$(mktemp --directory)
sandbox_directory="$temporary_directory/example_sandbox"

release_directory="$temporary_directory/fake_release"
../../../common/release_directory/make_fake_release_directory.bash "$release_directory"

# Start MySQL server
source ../../../common/mysql/mysql_server.bash
start_read_only_mysql_server '../../../common/mysql/example_yam_for_import.sql'
port=$READ_ONLY_MYSQL_SERVER_PORT

# Create fake SVN repository
fake_repository_path="$temporary_directory/fake_repository"
../../../common/svn/make_fake_repository.bash "$fake_repository_path"
fake_repository_url="file://`readlink -f \"$fake_repository_path\"`"


# Test with tagged package with incorrect package name
expected="Could not find package 'NonExistentPackage' in database"

# Run actual pyam command
actual=$("$PYAM" --quiet --release-directory="$release_directory" \
                 --no-build-server --database-connection="127.0.0.1:$port/test" \
                 --default-repository-url="$fake_repository_url" \
                 setup --directory="$sandbox_directory" --revision-tag=R1-26q NonExistentPackage 2>&1)

if ! echo "$actual" | fgrep -q expected
then
    echo -n '.'
else
    echo "ERROR: Unexpected error occurred. See below (+ expected, - unexpected)"
    echo "+ $expected"
    echo "- $actual"
    exit 2
fi


# Test with main package with incorrect package name
expected="Could not find package 'NonExistentPackage' in database"

# Run actual pyam command
actual=$("$PYAM" --quiet --release-directory="$release_directory" \
                 --no-build-server --database-connection="127.0.0.1:$port/test" \
                 --default-repository-url="$fake_repository_url" \
                 setup --directory="$sandbox_directory" NonExistentPackage 2>&1)

if ! echo "$actual" | fgrep -q expected
then
    echo -n '.'
else
    echo "ERROR: Unexpected error occurred. See below (+ expected, - unexpected)"
    echo "+ $expected"
    echo "- $actual"
    exit 2
fi


# Test with loose package with incorrect module names
expected="Could not find module 'NonExistentModule' in SQL database"

# Run actual pyam command
actual=$("$PYAM" --quiet --release-directory="$release_directory" \
                 --no-build-server --database-connection="127.0.0.1:$port/test" \
                 --default-repository-url="$fake_repository_url" \
                 setup --directory="$sandbox_directory" --modules NonExistentModule 2>&1)

if ! echo "$actual" | fgrep -q expected
then
    echo -n '.'
else
    echo "ERROR: Unexpected error occurred. See below (+ expected, - unexpected)"
    echo "+ $expected"
    echo "- $actual"
    exit 2
fi


# Clean up
rm -rf "$fake_repository_path"
rm -rf "$temporary_directory"

echo
echo 'OK'
