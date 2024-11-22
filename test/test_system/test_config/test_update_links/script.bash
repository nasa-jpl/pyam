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
# Fill in the YAM.config
config_filename="$temporary_directory/FakeSandbox/YAM.config"
echo 'LINK_MODULES = DshellEnv/DshellEnv-R1-04d Dshell++/Dshell++-R4-06f' >> "$config_filename"

# Dshell++ should be older version link module
cat "$config_filename" | grep 'Dshell++'


#-----------------------------------------------
# test --update-links

out_config_filename="${config_filename}.out"

pushd "$sandbox_directory" >& /dev/null

# Run "pyam config --update-links
# Note that we use bogus SQL information since this command should not depend on SQL
"$PYAM" --quiet --no-log --no-build-server --database-connection "127.0.0.1:$port/test" config --update-links  --output-file $out_config_filename

popd > /dev/null

#echo "XXX"
# Dshell++ should now be latest link module
cat "$out_config_filename" | grep 'Dshell'


#-----------------------------------------------
# test --update-links with work module conversion (default branch)

pushd "$sandbox_directory" >& /dev/null

# Run "pyam config --update-links --all-to-work".
# Note that we use bogus SQL information since this command should not depend on SQL
"$PYAM" --quiet --no-log --no-build-server --database-connection "127.0.0.1:$port/test" config --update-links --all-to-work  --output-file $out_config_filename

popd > /dev/null

#echo "XXX"
# Dshell++ should now be latest link module
cat "$out_config_filename" | grep 'Dshell'


#-----------------------------------------------
# test --update-links with work module conversion (junk branch)

pushd "$sandbox_directory" >& /dev/null

# Run "pyam config --update-links --all-to-work --branch junk".
# Note that we use bogus SQL information since this command should not depend on SQL
"$PYAM" --quiet --no-log --no-build-server --database-connection "127.0.0.1:$port/test" config --update-links --all-to-work  --output-file $out_config_filename --branch junk

popd > /dev/null

#echo "XXX"
# Dshell++ should now be latest link module
cat "$out_config_filename" | grep 'Dshell'


#-----------------------------------------------
#-----------------------------------------------
# test --update-links with work module conversion (no branch)

pushd "$sandbox_directory" >& /dev/null

# Run "pyam config --update-links --all-to-work --branch -".
# Note that we use bogus SQL information since this command should not depend on SQL
"$PYAM" --quiet --no-log --no-build-server --database-connection "127.0.0.1:$port/test" config --update-links --all-to-work --branch - --output-file $out_config_filename

popd > /dev/null

#echo "XXX"
# Dshell++ should now be latest link module
cat "$out_config_filename" | grep 'Dshell'





# clean up
../../../common/sandbox/remove_fake_sandbox.bash "$sandbox_directory"
rm -rf "$temporary_directory"



echo 'OK'
