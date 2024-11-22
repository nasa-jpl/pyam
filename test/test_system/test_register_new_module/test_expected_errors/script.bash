#!/bin/bash

# Unset configuration file environment variables as they may interfere.
unset YAM_PROJECT_CONFIG_DIR
unset YAM_PROJECT

# Use absolute path to avoid getting some possibly aliased version
PYAM=$(readlink -f ../../../../pyam)

temporary_directory=$(mktemp --directory)
function close() {
    rm -rf $temporary_directory
}
trap close EXIT
sandbox_directory="$temporary_directory/FakeSandbox"
../../../common/sandbox/make_fake_sandbox.bash "$sandbox_directory"

release_directory="$temporary_directory/fake_release"
../../../common/release_directory/make_fake_release_directory.bash "$release_directory"

# Start MySQL server
source ../../../common/mysql/mysql_server.bash
start_mysql_server '../../../common/mysql/example_yam_for_import.sql'
port=$START_MYSQL_SERVER_RETURN_PORT

# Create fake SVN repository
fake_repository_path="$temporary_directory/fake_repository"
../../../common/svn/make_fake_repository.bash "$fake_repository_path"
fake_repository_url="file://`readlink -f \"$fake_repository_path\"`"

# Create release directory
release_directory="$temporary_directory/release_area"
mkdir "$release_directory"

"$PYAM" --quiet --release-directory="$release_directory" \
        --no-build-server --database-connection="127.0.0.1:$port/test" \
        --default-repository-url="$fake_repository_url" \
        --release-directory="$release_directory" \
        register-new-module 'MyNewModule'

echo -n '.'

# Test of "register-new-module" with a module that already exists
expected="Module 'MyNewModule' already exists"

actual=$("$PYAM" --quiet --release-directory="$release_directory" \
                 --no-build-server --database-connection="127.0.0.1:$port/test" \
                 --default-repository-url="$fake_repository_url" \
                 --release-directory="$release_directory" \
                 register-new-module 'MyNewModule' 2>&1)

if echo "$actual" | grep --quiet "$expected"
then
    echo -n '.'
else
    echo "ERROR: Unexpected error occurred. See below (+ expected, - unexpected)"
    echo "+ $expected"
    echo "- $actual"
    exit 2
fi

# Test of "register-new-module" with non-existent keyword
expected="Repository keyword 'non_existent_keyword' is not in"

actual=$("$PYAM" --quiet --release-directory="$release_directory" \
                 --no-build-server --database-connection="127.0.0.1:$port/test" \
                 --default-repository-url="$fake_repository_url" \
                 --release-directory="$release_directory" \
                 --keyword-to-repository='a=svn://blah, b=svn://blue' \
                 register-new-module --repository-keyword='non_existent_keyword' 'MyNewModule1' 2>&1)

if echo "$actual" | grep --quiet "$expected"
then
    echo -n '.'
else
    echo "ERROR: Unexpected error occurred. See below (+ expected, - unexpected)"
    echo "+ $expected"
    echo "- $actual"
    exit 2
fi

echo
echo 'OK'
