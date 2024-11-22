#!/bin/bash

# Unset configuration file environment variables as they may interfere.
unset YAM_PROJECT_CONFIG_DIR
unset YAM_PROJECT

# Use absolute path to avoid getting some possibly aliased version
PYAM=$(readlink -f ../../../../pyam)

temporary_directory=$(mktemp --directory)
sandbox_directory="$temporary_directory/FakeSandbox"
../../../common/sandbox/make_fake_sandbox.py "$sandbox_directory"

release_directory="$temporary_directory/fake_release"
../../../common/release_directory/make_fake_release_directory.bash "$release_directory"

# Start MySQL server
source ../../../common/mysql/mysql_server.bash
start_mysql_server '../../../common/mysql/example_yam_for_import.sql'
port=$START_MYSQL_SERVER_RETURN_PORT

# Create fake GIT repository
fake_repository_path="$temporary_directory/fake_repository"
../../../common/git/make_fake_repository.bash "$fake_repository_path"
fake_repository_url="file://`readlink -f \"$fake_repository_path\"`"
echo TEST NEW GIT
# Create release directory
release_directory="$temporary_directory/release_area"
mkdir "$release_directory"

# Do the test of "register-new-module"

"$PYAM" --use_git  --quiet --release-directory="$release_directory" \
        --no-build-server --database-connection="127.0.0.1:$port/test" \
        --default-repository-url="$fake_repository_url" \
        --release-directory="$release_directory" \
        register-new-module 'MyNewModule'

# The above command should have created a release directory for us
module_release_directory="$release_directory/Module-Releases/MyNewModule/MyNewModule-R1-00"
if [ ! -d "$module_release_directory" ]
then
    echo "ERROR: Module's release directory was not created at $module_release_directory"
    exit 2
fi

# Fill in the YAM.config
echo 'WORK_MODULES = MyNewModule' >> "$temporary_directory/FakeSandbox/YAM.config"
echo 'BRANCH_MyNewModule = MyNewModule-R1-00 my_branch' >> "$temporary_directory/FakeSandbox/YAM.config"

# Check out branched module
pushd "$sandbox_directory" >& /dev/null
if [ $? -ne 0 ]
then
    echo "ERROR: Could not change directory to $sandbox_directory"
    exit 2
fi
"$PYAM"  --quiet --release-directory="$release_directory" \
        --no-build-server --database-connection="127.0.0.1:$port/test" \
        --default-repository-url="$fake_repository_url" \
        rebuild 'MyNewModule'
popd > /dev/null

if [ ! -r "$sandbox_directory/src/MyNewModule/YamVersion.h" ]
then
    echo 'ERROR: Module source code should be checked out'
    exit 2
fi

# Make some changes and commit them to SVN repository
pushd "$sandbox_directory/src/MyNewModule" >& /dev/null
if [ $? -ne 0 ]
then
    echo "ERROR: Could not change directory to $sandbox_directory/src/MyNewModule"
    exit 2
fi
svn mkdir --quiet 'my_new_directory'
svn commit --quiet --message 'Add directory'
popd > /dev/null

# Save the branch
pushd "$sandbox_directory" >& /dev/null
"$PYAM" --quiet --non-interactive --release-directory="$release_directory" \
        --no-build-server --database-connection="127.0.0.1:$port/test" \
        --default-repository-url="$fake_repository_url" \
        --release-directory="$release_directory" \
        save 'MyNewModule'
if [ $? -ne 0 ]
then
    echo 'ERROR: pyam save failed'
    exit 2
fi
popd > /dev/null


pushd "$sandbox_directory" >& /dev/null
# Check out the module again and make sure the changes we made are still there.
# First we have to convert the link module to a work module.
"$PYAM" --quiet --release-directory="$release_directory" \
        --no-build-server --database-connection="127.0.0.1:$port/test" \
        --default-repository-url="$fake_repository_url" \
        checkout 'MyNewModule'
    
if [ $? -ne 0 ]
then
    echo "ERROR: Could not convert MyNewModule into a work module"
    echo "See temporary sandbox at $sandbox_directory"
    exit 2
fi
popd > /dev/null

# Now we check out the MyNewModule again
rm -rf "$sandbox_directory/src/MyNewModule"
pushd "$sandbox_directory" >& /dev/null
if [ $? -ne 0 ]
then
    echo "ERROR: Could not change directory to $sandbox_directory"
    exit 2
fi
"$PYAM" --quiet --release-directory="$release_directory" \
        --no-build-server --database-connection="127.0.0.1:$port/test" \
        --default-repository-url="$fake_repository_url" \
        rebuild 'MyNewModule'
if [ $? -ne 0 ]
then
    echo 'ERROR: pyam rebuild failed'
    exit 2
fi
popd > /dev/null

if [ ! -d "$sandbox_directory/src/MyNewModule/my_new_directory" ]
then
    echo 'ERROR: Module source code should be checked out after rebuilding after save'
    echo "See temporary sandbox at $sandbox_directory"
    exit 2
fi

if [ ! -r "$sandbox_directory/src/MyNewModule/YamVersion.h" ]
then
    echo 'ERROR: YamVersion.h file should exist'
    echo "See temporary sandbox at $sandbox_directory"
    exit 2
fi

# Make sure revision tag is updated (from 00 to 00a)
grep 'R1-00a' "$sandbox_directory/src/MyNewModule/YamVersion.h"

#../../../common/sandbox/remove_fake_sandbox.bash "$sandbox_directory"
#rm -rf "$fake_repository_path"
#rm -rf "$temporary_directory"

echo 'OK'
