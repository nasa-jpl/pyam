#!/bin/bash
#
# Test "pyam config --to-link".
# This requires database access since we need to get the latest build ID.
# But the test should not require repository access.

# Unset configuration file environment variables as they may interfere.
unset YAM_PROJECT_CONFIG_DIR
unset YAM_PROJECT

# Use absolute path to avoid getting some possibly aliased version
PYAM=$(readlink -f ../../../../pyam)

temporary_directory=$(mktemp --directory)
sandbox_directory="$temporary_directory/FakeSandbox"
../../../common/sandbox/make_fake_sandbox.bash "$sandbox_directory"

#echo "TEMP=$temporary_directory"
# Create a fake release area.

#release_directory="$temporary_directory/fake_release"
#"../../../common/release_directory/make_fake_release_directory.bash" "$release_directory"

# Start MySQL server
source ../../../common/mysql/mysql_server.bash
start_mysql_server '../../../common/mysql/example_yam_for_import.sql'
port=$START_MYSQL_SERVER_RETURN_PORT

# Fill in the YAM.config
config_filename="$temporary_directory/FakeSandbox/YAM.config"
echo 'WORK_MODULES = Dshell++ Darts' >> "$config_filename"
echo 'BRANCH_Dshell++ = Dshell++-R4-06g my_branch' >> "$config_filename"
echo 'BRANCH_Darts = Darts-R3-15g my_branch' >> "$config_filename"
echo 'LINK_MODULES = DshellEnv/DshellEnv-R1-64e' >> "$config_filename"


pushd "$sandbox_directory" >& /dev/null

# Run "pyam config --to-link".
# Note that we use bogus SQL information since this command should not depend on SQL
"$PYAM" --quiet --no-log --no-build-server --database-connection "127.0.0.1:$port/test" config --input-file $config_filename --output-file $config_filename --to-link Darts

popd > /dev/null

#cat "$config_filename"
#echo "XXXX"

cat "$config_filename" | grep 'Dshell'


# Dshell++ should now be a link module
cat "$config_filename" | grep '^Dshell++'


# Darts should now be a link module
cat "$config_filename" | grep 'Darts'





../../../common/sandbox/remove_fake_sandbox.bash "$sandbox_directory"
rm -rf "$temporary_directory"

echo 'OK'
