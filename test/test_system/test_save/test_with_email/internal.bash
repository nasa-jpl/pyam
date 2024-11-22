#!/bin/bash
#
# Test "pyam save" with email enabled. This script assumes that it is called
# with an environment variable SMTP_PORT, which points to a fake SMTP server
# port on localhost.

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
echo 'BRANCH_Dshell++ = Dshell++-R4-06g my_branch' >> "$temporary_directory/FakeSandbox/YAM.config"

# Start MySQL server
source ../../../common/mysql/mysql_server.bash
start_mysql_server '../../../common/mysql/example_yam_for_import.sql'
port=$START_MYSQL_SERVER_RETURN_PORT

# Create fake SVN repository
fake_repository_path="$temporary_directory/fake_repository"
../../../common/svn/make_fake_repository.bash "$fake_repository_path"
fake_repository_url="file://`readlink -f \"$fake_repository_path\"`"


echo -n '.'


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
    --site='telerobotics' \
        rebuild 'Dshell++'
if [ $? -ne 0 ]
then
    echo 'ERROR: pyam rebuild failed'
    exit 2
fi
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
svn mkdir --quiet 'my_new_directory'
svn commit --quiet --message 'Add a directory; let me make this message longer to test wrapping in change log'

rm 'my_file.txt'
echo "this is my ☃." >> 'my_file.txt'
echo "" >> 'my_file.txt'
echo "" >> 'my_file.txt'
echo "1" >> 'my_file.txt'
echo "" >> 'my_file.txt'
echo "2" >> 'my_file.txt'
LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 svn commit --quiet --message 'Add snowman ☃'

popd > /dev/null


echo -n '.'


# Save the branch
pushd "$sandbox_directory" >& /dev/null
"$PYAM" --quiet --release-directory="$release_directory" \
        --no-build-server --database-connection="127.0.0.1:$port/test" \
        --default-repository-url="$fake_repository_url" \
    --site='telerobotics' \
        --email-server="127.0.0.1:$SMTP_PORT" \
        --email-to-address='fake.address@127.0.0.1' \
        --email-from-username='fake.sender'  \
        --email-from-hostname='127.0.0.1' \
        --non-interactive \
        save --to-tagged --release-note-message='My ☃' --bug-id='12345' --username='fakeuser' 'Dshell++'
if [ $? -ne 0 ]
then
    echo 'ERROR: pyam save failed'
    kill "$smtp_pid"
    exit 2
fi
popd > /dev/null


echo -n '.'


# We used the --to-tagged option with "pyam save" so it should have been
# checked out after it was saved
if [ ! -d "$sandbox_directory/src/Dshell++/my_new_directory" ]
then
    echo 'ERROR: Module source code should be checked out'
    exit 2
fi

if [ ! -r "$sandbox_directory/src/Dshell++/YamVersion.h" ]
then
    echo 'ERROR: Module source code should be checked out'
    exit 2
fi

# Make sure revision tag is updated (from g to h)
grep 'R4-06h' "$sandbox_directory/src/Dshell++/YamVersion.h" > /dev/null
if [ $? -ne 0 ]
then
    echo 'ERROR: The tag is incorrect'
    exit 2
fi

../../../common/sandbox/remove_fake_sandbox.bash "$sandbox_directory"
rm -rf "$fake_repository_path"
rm -rf "$temporary_directory"
