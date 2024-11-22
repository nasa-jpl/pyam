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
echo 'LINK_MODULES = DshellEnv/DshellEnv-R1-44e Dshell++/Dshell++-R4-06e' >> "$config_filename"


"$PYAM" --no-log --quiet --release-directory="$release_directory" \
        --no-build-server --database-connection "127.0.0.1:$port/test" latest Dshell++ DshellEnv



pushd "$sandbox_directory" >& /dev/null

# Note that we use bogus SQL information since this command should not depend on SQL
"$PYAM" --no-log --quiet --release-directory="$release_directory" \
        --no-build-server --database-connection "127.0.0.1:$port/test" sync --release R4-06f Dshell++

popd > /dev/null

# DshellEnv should be the latest
grep 'Dshell' "$config_filename"



../../../common/sandbox/remove_fake_sandbox.bash "$sandbox_directory"
rm -rf "$temporary_directory"

echo 'OK'
