#!/bin/bash

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
echo 'WORK_MODULES = Dshell++' >> "$temporary_directory/FakeSandbox/YAM.config"
echo 'BRANCH_Dshell++ = main' >> "$temporary_directory/FakeSandbox/YAM.config"

# Start MySQL server
. ../../../common/mysql/mysql_server.bash
start_read_only_mysql_server '../../../common/mysql/example_yam_for_import.sql'
port=$READ_ONLY_MYSQL_SERVER_PORT

# Create fake SVN repository
fake_repository_path="$temporary_directory/fake_repository"
../../../common/svn/make_fake_repository.bash "$fake_repository_path"
fake_repository_url="file://`readlink -f \"$fake_repository_path\"`"

# Check out branched module
pushd "$sandbox_directory" >& /dev/null
if [ $? -ne 0 ]
then
    echo "ERROR: Could not change directory to $sandbox_directory"
    exit 2
fi
"$PYAM" --quiet --release-directory="$release_directory" \
        --no-build-server --database-connection="127.0.0.1:$port/test" \
        --default-repository-url="$fake_repository_url" \
        rebuild 'Dshell++'
popd > /dev/null

if [ ! -r "$sandbox_directory/src/Dshell++/YamVersion.h" ]
then
    echo 'ERROR: Module source code should be checked out'
    exit 2
fi

grep 'R4-06g' "$sandbox_directory/src/Dshell++/YamVersion.h" > /dev/null
if [ $? -ne 0 ]
then
    echo 'ERROR: The tag is incorrect'
    exit 2
fi

# Make some changes and commit them to SVN repository
pushd "$sandbox_directory/src/Dshell++" >& /dev/null
if [ $? -ne 0 ]
then
    echo "ERROR: Could not change directory to $sandbox_directory/src/Dshell++"
    exit 2
fi
file_contents='my file contents is this'
echo "$file_contents" >> 'my_file'
svn add --quiet 'my_file'
svn commit --quiet --message 'Add a file'


# Run "pyam diff"
output=$("$PYAM" --no-build-server --database-connection="127.0.0.1:$port/test" --default-repository-url="$fake_repository_url"  diff Dshell++)
echo "$output" | grep "$file_contents" > /dev/null
if [ $? -eq 0 ]
then
    echo -n '.'
else
    echo "ERROR: Diff did not contain correct output. We expected to see the addition of the line '$file_contents'. See below for actual output."
    echo "$output"
    exit 2
fi

# Run "pyam diff" without argument. It should know that we are in the Dshell++ directory.
output=$("$PYAM" --no-build-server --database-connection="127.0.0.1:$port/test" --default-repository-url="$fake_repository_url"  diff)
echo "$output" | grep "$file_contents" > /dev/null
if [ $? -eq 0 ]
then
    echo -n '.'
else
    echo "ERROR: Diff did not contain correct output. We expected to see the addition of the line '$file_contents'. See below for actual output."
    echo "$output"
    exit 2
fi

# Run "pyam diff" with release tags specified
output=$("$PYAM" --no-build-server --database-connection="127.0.0.1:$port/test" --default-repository-url="$fake_repository_url"  diff   --from-release R4-06e   --to-release R4-06g  Dshell++)
echo "$output" | grep "my_file" > /dev/null
if [ $? -eq 0 ]
then
    echo -n '.'
else
    echo "ERROR: Diff did not contain correct output. We expected to see a my_file entry. See below for actual output."
    echo "$output"
    exit 2
fi

popd > /dev/null

../../../common/sandbox/remove_fake_sandbox.bash "$sandbox_directory"
rm -rf "$fake_repository_path"
rm -rf "$temporary_directory"

echo
echo 'OK'