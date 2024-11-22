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
echo 'BRANCH_Dshell++ = Dshell++-R4-06g' >> "$temporary_directory/FakeSandbox/YAM.config"

# Start MySQL server
source ../../../common/mysql/mysql_server.bash
start_mysql_server '../../../common/mysql/example_yam_for_import.sql'
port=$START_MYSQL_SERVER_RETURN_PORT

# Create fake SVN repository
fake_repository_path="$temporary_directory/fake_repository"
../../../common/svn/make_fake_repository.bash "$fake_repository_path"
fake_repository_url="file://`readlink -f \"$fake_repository_path\"`"

pushd "$sandbox_directory" >& /dev/null
"$PYAM" --quiet --release-directory="$release_directory" \
        --no-build-server --database-connection="127.0.0.1:$port/test" --default-repository-url="$fake_repository_url" rebuild Dshell++
popd > /dev/null

if [ ! -r "$sandbox_directory/src/Dshell++/YamVersion.h" ]
then
    echo 'ERROR: Module source code should be checked out'
    exit 2
fi

if [ -w "$sandbox_directory/src/Dshell++/YamVersion.h" ]
then
    echo 'ERROR: Module source code should not be writable'
    exit 2
fi

grep 'R4-06g' "$sandbox_directory/src/Dshell++/YamVersion.h" > /dev/null
if [ $? -ne 0 ]
then
    echo 'ERROR: The tag is incorrect'
    exit 2
fi

../../../common/sandbox/remove_fake_sandbox.bash "$sandbox_directory"
rm -rf "$fake_repository_path"
rm -rf "$temporary_directory"

echo 'OK'
