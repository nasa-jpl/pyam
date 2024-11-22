#!/bin/bash
#
# Set up a sandbox created from a package's main branch.

# Unset configuration file environment variables as they may interfere.
unset YAM_PROJECT_CONFIG_DIR
unset YAM_PROJECT

# Use absolute path to avoid getting some possibly aliased version
PYAM=$(readlink -f ../../../../pyam)

temporary_directory=$(mktemp --directory)

# Start MySQL server
source ../../../common/mysql/mysql_server.bash
start_mysql_server '../../../common/mysql/example_yam_for_import.sql'
port=$START_MYSQL_SERVER_RETURN_PORT

# Create fake SVN repository
fake_repository_path="$temporary_directory/fake_repository"
../../../common/svn/make_fake_repository.bash "$fake_repository_path"
fake_repository_url="file://`readlink -f \"$fake_repository_path\"`"

cd "$temporary_directory"

# Run actual pyam command
output=$("$PYAM" --quiet --no-build-server --database-connection="127.0.0.1:$port/test" \
                 --default-repository-url="$fake_repository_url" \
                 test)
echo "$output" | grep 'Database access: succeeded' > /dev/null
if [ $? -ne 0 ]
then
    echo 'ERROR: Database access should have succeeded. See output below.'
    echo "$output"
    exit 2
fi

echo "$output" | grep 'Default repository access: succeeded' > /dev/null
if [ $? -ne 0 ]
then
    echo 'ERROR: Default repository access should have succeeded. See output below.'
    echo "$output"
    exit 2
fi

echo "$output" | grep 'failed' > /dev/null
if [ $? -eq 0 ]
then
    echo 'ERROR: There should be no failed access. See output below.'
    echo "$output"
    exit 2
fi

# Run actual pyam command
output=$("$PYAM" --quiet --no-build-server --database-connection="127.0.0.1:55555/blah" \
                 --default-repository-url="non_existent_repository" \
                 test)
echo "$output" | grep 'succeeded' > /dev/null
if [ $? -eq 0 ]
then
    echo 'ERROR: All access should have failed. See output below.'
    echo "$output"
    exit 2
fi

# Clean up
rm -rf "$fake_repository_path"
rm -rf "$temporary_directory"

echo 'OK'
