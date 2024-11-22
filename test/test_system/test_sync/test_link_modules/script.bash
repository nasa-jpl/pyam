#!/bin/bash
#
# Test "pyam sync --link-modules".
# This test should not require repository access.

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

# Start MySQL server
source ../../../common/mysql/mysql_server.bash
start_mysql_server '../../../common/mysql/example_yam_for_import.sql'
port=$START_MYSQL_SERVER_RETURN_PORT

# Fill in the YAM.config
config_filename="$temporary_directory/FakeSandbox/YAM.config"
echo 'WORK_MODULES =' >> "$config_filename"
echo 'LINK_MODULES = DshellEnv/DshellEnv-R1-64e SimModels/SimModels-R1-02b' >> "$config_filename"


pushd "$sandbox_directory" >& /dev/null

# Note that we use bogus SQL information since this command should not depend on SQL
"$PYAM" --quiet --release-directory="$release_directory" \
        --no-build-server --database-connection "127.0.0.1:$port/test" sync --link-modules
if [ $? -ne 0 ]
then
    echo "ERROR: "pyam config" failed"
    exit 2
fi

popd > /dev/null


# DshellEnv should be the latest
grep 'DshellEnv-R1-49r' "$config_filename" > /dev/null
if [ $? -ne 0 ]
then
    echo 'ERROR: DshellEnv should be on the latest revision (R1-49r) in YAM.config'
    echo "See $config_filename"
    exit 2
fi

grep 'SimModels-R1-02c' "$config_filename" > /dev/null
if [ $? -ne 0 ]
then
    echo 'ERROR: SimModels should be on the latest revision (R1-02c) in YAM.config'
    echo "See $config_filename"
    exit 2
fi


../../../common/sandbox/remove_fake_sandbox.bash "$sandbox_directory"
rm -rf "$temporary_directory"

echo 'OK'
