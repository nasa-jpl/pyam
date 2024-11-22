#!/bin/bash

# Unset YAM_ROOT or it will interfere.
# Makefile.yam will pick up the real sandbox that contains the pyam module.
unset YAM_ROOT

# Unset configuration file environment variables as they may interfere.
unset YAM_PROJECT_CONFIG_DIR
unset YAM_PROJECT

# Use absolute path to avoid getting some possibly aliased version
PYAM=$(readlink -f ../../../../pyam)

temporary_directory=$(mktemp --directory)
sandbox_directory="$temporary_directory/FakeSandbox"
../../../common/sandbox/make_fake_sandbox.bash "$sandbox_directory"

release_directory="$temporary_directory/fake_release"
../../../common/release_directory/make_fake_release_directory.bash "$release_directory"

# Fill in the YAM.config
echo 'WORK_MODULES = Dshell++ DatabaseUnknownModule' >> "$temporary_directory/FakeSandbox/YAM.config"
echo 'BRANCH_Dshell++ = Dshell++-R4-06g my_branch' >> "$temporary_directory/FakeSandbox/YAM.config"
echo 'BRANCH_DatabaseUnknownModule = DatabaseUnknownModule-R3-07a my_branch' >> "$temporary_directory/FakeSandbox/YAM.config"

# Start MySQL server
source ../../../common/mysql/mysql_server.bash
start_mysql_server '../../../common/mysql/example_yam_for_import.sql'
port=$START_MYSQL_SERVER_RETURN_PORT

# Create fake SVN repository
fake_repository_path="$temporary_directory/fake_repository"
../../../common/svn/make_fake_repository.bash "$fake_repository_path"
fake_repository_url="file://`readlink -f \"$fake_repository_path\"`"

pushd "$sandbox_directory" >& /dev/null


# Test
expected="Work module 'NonExistentModule' not found in file '$temporary_directory/FakeSandbox/YAM.config'"

actual=$("$PYAM" --quiet --release-directory="$release_directory" \
                 --no-build-server --database-connection="127.0.0.1:$port/test" --default-repository-url="$fake_repository_url" rebuild 'NonExistentModule' 2>&1)

if ! echo "$actual" | fgrep -q expected
then
    echo -n '.'
else
    echo "ERROR: Unexpected error occurred. See below (+ expected, - unexpected)"
    echo "+ $expected"
    echo "- $actual"
    exit 2
fi


# Test module unknown to the database
expected="Could not find module 'DatabaseUnknownModule' in database"

actual=$("$PYAM" --quiet --release-directory="$release_directory" \
                 --no-build-server --database-connection="127.0.0.1:$port/test" --default-repository-url="$fake_repository_url" rebuild 'DatabaseUnknownModule' 2>&1)

if ! echo "$actual" | fgrep -q expected
then
    echo -n '.'
else
    echo "ERROR: Unexpected error occurred. See below (+ expected, - unexpected)"
    echo "+ $expected"
    echo "- $actual"
    exit 2
fi

# Replace YAM.config with a Dshell++ with an illegal branch ID
rm -f "$temporary_directory/FakeSandbox/YAM.config"
echo 'WORK_MODULES = Dshell++' >> "$temporary_directory/FakeSandbox/YAM.config"
echo 'BRANCH_Dshell++ = Dshell++-R4-06g illegal,character' >> "$temporary_directory/FakeSandbox/YAM.config"

# Test that branch with illegal characters does not get created
expected="Illegal character(s) used in branch ID 'illegal,character'; legal IDs are composed of one or more alphanumeric characters, underscores, or hyphens"

actual=$("$PYAM" --quiet --release-directory="$release_directory" \
                 --no-build-server --database-connection="127.0.0.1:$port/test" --default-repository-url="$fake_repository_url" rebuild 'Dshell++' 2>&1)

if ! echo "$actual" | fgrep -q expected
then
    echo -n '.'
else
    echo "ERROR: Unexpected error occurred. See below (+ expected, - unexpected)"
    echo "+ $expected"
    echo "- $actual"
    exit 2
fi


popd > /dev/null

../../../common/sandbox/remove_fake_sandbox.bash "$sandbox_directory"
rm -rf "$fake_repository_path"
rm -rf "$temporary_directory"

echo
echo 'OK'
