#!/bin/bash
#
# Test "pyam config --all-to-work".

# Unset configuration file environment variables as they may interfere.
unset YAM_PROJECT_CONFIG_DIR
unset YAM_PROJECT

# Use absolute path to avoid getting some possibly aliased version
PYAM=$(readlink -f ../../../../pyam)

temporary_directory=$(mktemp --directory)
sandbox_directory="$temporary_directory/FakeSandbox"
../../../common/sandbox/make_fake_sandbox.bash "$sandbox_directory"

# Start MySQL server
source ../../../common/mysql/mysql_server.bash
start_mysql_server '../../../common/mysql/example_yam_for_import.sql'
port=$START_MYSQL_SERVER_RETURN_PORT

# Create fake SVN repository
fake_repository_path="$temporary_directory/fake_repository"
../../../common/svn/make_fake_repository.bash "$fake_repository_path"
fake_repository_url="file://`readlink -f \"$fake_repository_path\"`"


#-----------------------------------------------
out_config_filename="YAM.config.out"

#pushd "$sandbox_directory" >& /dev/null

# Run "pyam config --update-links
# Note that we use bogus SQL information since this command should not depend on SQL
"$PYAM" --quiet --no-log --no-build-server --default-repository-url=$fake_repository_url --database-connection "127.0.0.1:$port/test" config --current-modules  --output-file $out_config_filename

#popd > /dev/null

#echo "XXX"
# Dshell++ should now be latest link module
#cat "$out_config_filename"




# clean up
../../../common/sandbox/remove_fake_sandbox.bash "$sandbox_directory"
rm -rf "$temporary_directory"



echo 'OK'
